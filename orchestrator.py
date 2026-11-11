"""
Multi-Agent Orchestrator
Coordinates the 4 specialized agents (Retrieval, Eligibility, Application, Explainer)
with conversation memory and intent routing using LangChain Expression Language (LCEL).

Improvements:
  - True conditional routing by intent
  - Relevance thresholding via retrieve_with_quality_check()
  - Metadata / state-aware query enrichment
  - Missing-info gate before expensive agent chains
  - Structured error handling (rate-limit, auth, network, generic)
"""
from typing import Dict, Any, List, Optional
import json

from config import get_llm
from memory import CitizenProfile, extract_profile_updates
from agents.intent_router import route_user_intent
from agents.retrieval_agent import RetrievalAgent
from agents.eligibility_agent import evaluate_eligibility
from agents.application_agent import generate_application_guide
from agents.explainer_agent import explain_to_citizen

# Human-readable message returned when no relevant docs found
_NO_DOCS_MSG = (
    "I couldn't find specific information about this in my knowledge base. "
    "For accurate details, please visit myscheme.gov.in or the official scheme portal."
)


class SchemeNavigatorOrchestrator:
    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider
        self.model = model
        self.llm = get_llm(provider=provider, model=model)
        self.retriever_agent = RetrievalAgent()

    # ------------------------------------------------------------------
    # Helper: Missing-info deterministic gate
    # ------------------------------------------------------------------
    def _check_missing_info(
        self,
        profile: CitizenProfile,
        intent: str,
        target_scheme: Optional[str] = None
    ) -> Optional[str]:
        """
        Returns a clarifying question string if critical profile info is absent,
        or None if we have enough to proceed.
        """
        if intent == "scheme_discovery":
            if profile.occupation is None and profile.state is None:
                return (
                    "To find the right schemes for you, could you share: "
                    "your **state** (e.g., Karnataka, Maharashtra), "
                    "your **occupation** (e.g., farmer, street vendor, student), "
                    "and your **approximate annual household income**?"
                )

        if intent == "eligibility_check":
            if (
                target_scheme
                and "kisan" in target_scheme.lower()
                and profile.landholding_acres is None
            ):
                return (
                    "To check your PM-KISAN eligibility, could you tell me "
                    "how many **acres of land** you own?"
                )

        return None  # No missing info — proceed normally

    # ------------------------------------------------------------------
    # Helper: Build a retrieval result dict (chunks + citations)
    # ------------------------------------------------------------------
    def _do_retrieval(
        self,
        search_query: str,
        profile: CitizenProfile,
        filter_dict: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        Enriches query with profile state if available, calls
        retrieve_with_quality_check(), and returns structured info.
        Returns dict with keys: no_docs, chunks, context_text, citations_summary.
        """
        enriched_query = search_query
        if profile.state:
            enriched_query = f"{search_query} {profile.state}"

        result = self.retriever_agent.retrieve_with_quality_check(
            query=enriched_query,
            top_k=4,
            distance_threshold=1.2,
            filter_dict=filter_dict
        )

        if result["no_relevant_docs"]:
            return {
                "no_docs": True,
                "chunks": [],
                "context_text": "",
                "citations_summary": ""
            }

        chunks = result["chunks"]
        context_text = self.retriever_agent.format_context_for_prompt(chunks)

        unique_sources = {}
        for chunk in chunks:
            s_name = chunk["scheme"]
            if s_name not in unique_sources:
                unique_sources[s_name] = (
                    f"- **{s_name}** | Document: `{chunk['source_file']}` "
                    f"(Page {chunk['page']}) | Portal: {chunk['source_url']}"
                )
        citations_summary = "\n".join(unique_sources.values())

        return {
            "no_docs": False,
            "chunks": chunks,
            "context_text": context_text,
            "citations_summary": citations_summary
        }

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def process_message(
        self,
        user_message: str,
        current_profile: CitizenProfile,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        End-to-End Multi-Agent execution pipeline with true conditional routing:

        scheme_discovery     → Profile update → Retrieval → Eligibility → Application → Explainer
        eligibility_check    → Profile update → Retrieval (filtered) → Eligibility → Explainer
        application_guidance → Profile update → Retrieval (filtered) → Application → Explainer
        profile_update       → Profile update only → ask for missing fields
        chitchat_or_greeting → Direct LLM response (no retrieval)
        """
        chat_history = chat_history or []
        chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history[-4:]])

        # Canonical empty response dict (returned on early-exit paths)
        def _empty_response(msg: str) -> Dict[str, Any]:
            return {
                "final_response": msg,
                "intent_routing": {},
                "retrieved_chunks": [],
                "eligibility_findings": "",
                "application_guidance": "",
                "citations_summary": "",
                "profile": current_profile
            }

        try:
            # ----------------------------------------------------------------
            # Step 1: Extract & update citizen profile from message
            # ----------------------------------------------------------------
            extracted_fields = extract_profile_updates(user_message, current_profile, self.llm)
            current_profile.update_from_extracted(extracted_fields)
            profile_summary = current_profile.summary_text()

            # ----------------------------------------------------------------
            # Step 2: Intent Routing
            # ----------------------------------------------------------------
            routing = route_user_intent(user_message, profile_summary, chat_context, self.llm)
            intent = routing.get("intent", "scheme_discovery")
            search_query = routing.get("search_query", user_message)
            target_scheme = routing.get("target_scheme") or None  # normalise empty string → None

            retrieved_chunks = []
            context_text = ""
            eligibility_findings = ""
            application_guidance = ""
            citations_summary = ""
            final_response = ""

            # ----------------------------------------------------------------
            # Step 3: Route by intent
            # ----------------------------------------------------------------

            # --- CHITCHAT / GREETING: Direct LLM, no retrieval ---
            if intent == "chitchat_or_greeting":
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.output_parsers import StrOutputParser
                greet_prompt = ChatPromptTemplate.from_messages([
                    ("system",
                     "You are the friendly Government Scheme Eligibility Navigator for Indian citizens. "
                     "Explain how you help citizens discover schemes, check criteria, and get application guidance. "
                     "Invite them to describe their profile (state, age, occupation, income, landholding)."),
                    ("human", "{user_message}")
                ])
                final_response = (greet_prompt | self.llm | StrOutputParser()).invoke(
                    {"user_message": user_message}
                )

            # --- PROFILE UPDATE: Update profile, ask for missing fields ---
            elif intent == "profile_update":
                missing = current_profile.missing_fields_for_eligibility()
                final_response = (
                    f"Thank you! I have updated your profile with the details provided:\n\n"
                    f"**Current Profile:** {profile_summary}\n\n"
                )
                if missing:
                    final_response += (
                        f"To give you an exact scheme eligibility assessment, could you also tell me your "
                        f"**{', '.join(missing)}**?"
                    )
                else:
                    final_response += (
                        "Your profile has all necessary information. "
                        "You can ask: *'What schemes am I eligible for?'*"
                    )

            # --- SCHEME DISCOVERY: Full pipeline ---
            elif intent == "scheme_discovery":
                # Missing-info gate
                gate_msg = self._check_missing_info(current_profile, intent)
                if gate_msg:
                    return _empty_response(gate_msg)

                ret = self._do_retrieval(search_query, current_profile)
                if ret["no_docs"]:
                    return _empty_response(_NO_DOCS_MSG)

                retrieved_chunks = ret["chunks"]
                context_text = ret["context_text"]
                citations_summary = ret["citations_summary"]

                # Eligibility Agent
                eligibility_findings = evaluate_eligibility(
                    user_message=user_message,
                    profile_summary=profile_summary,
                    context=context_text,
                    llm=self.llm
                )

                # Application Agent
                application_guidance = generate_application_guide(
                    user_message=user_message,
                    eligibility_findings=eligibility_findings,
                    context=context_text,
                    llm=self.llm
                )

                # Explainer
                final_response = explain_to_citizen(
                    user_message=user_message,
                    profile_summary=profile_summary,
                    intent=intent,
                    eligibility_findings=eligibility_findings,
                    application_guidance=application_guidance,
                    citations=citations_summary,
                    llm=self.llm,
                    chat_context=chat_context,
                    context_chunks_text=context_text
                )

            # --- ELIGIBILITY CHECK: Skip Application Agent ---
            elif intent == "eligibility_check":
                # Missing-info gate
                gate_msg = self._check_missing_info(current_profile, intent, target_scheme)
                if gate_msg:
                    return _empty_response(gate_msg)

                # Optionally filter by target_scheme
                filter_dict = None
                if target_scheme:
                    # Append scheme name to query for better retrieval
                    search_query = f"{search_query} {target_scheme}"

                ret = self._do_retrieval(search_query, current_profile, filter_dict=filter_dict)
                if ret["no_docs"]:
                    return _empty_response(_NO_DOCS_MSG)

                retrieved_chunks = ret["chunks"]
                context_text = ret["context_text"]
                citations_summary = ret["citations_summary"]

                # Eligibility Agent only (no Application Agent)
                eligibility_findings = evaluate_eligibility(
                    user_message=user_message,
                    profile_summary=profile_summary,
                    context=context_text,
                    llm=self.llm
                )

                # Explainer (no application_guidance)
                final_response = explain_to_citizen(
                    user_message=user_message,
                    profile_summary=profile_summary,
                    intent=intent,
                    eligibility_findings=eligibility_findings,
                    application_guidance="",
                    citations=citations_summary,
                    llm=self.llm,
                    chat_context=chat_context,
                    context_chunks_text=context_text
                )

            # --- APPLICATION GUIDANCE: Skip Eligibility Agent ---
            elif intent == "application_guidance":
                # Optionally filter by target_scheme
                filter_dict = None
                if target_scheme:
                    search_query = f"{search_query} {target_scheme}"

                ret = self._do_retrieval(search_query, current_profile, filter_dict=filter_dict)
                if ret["no_docs"]:
                    return _empty_response(_NO_DOCS_MSG)

                retrieved_chunks = ret["chunks"]
                context_text = ret["context_text"]
                citations_summary = ret["citations_summary"]

                # Application Agent only (no Eligibility Agent)
                application_guidance = generate_application_guide(
                    user_message=user_message,
                    eligibility_findings="",
                    context=context_text,
                    llm=self.llm
                )

                # Explainer (no eligibility_findings)
                final_response = explain_to_citizen(
                    user_message=user_message,
                    profile_summary=profile_summary,
                    intent=intent,
                    eligibility_findings="",
                    application_guidance=application_guidance,
                    citations=citations_summary,
                    llm=self.llm,
                    chat_context=chat_context,
                    context_chunks_text=context_text
                )

            else:
                # Unknown / unhandled intent — treat as scheme discovery
                ret = self._do_retrieval(search_query, current_profile)
                if ret["no_docs"]:
                    return _empty_response(_NO_DOCS_MSG)

                retrieved_chunks = ret["chunks"]
                context_text = ret["context_text"]
                citations_summary = ret["citations_summary"]

                eligibility_findings = evaluate_eligibility(
                    user_message=user_message,
                    profile_summary=profile_summary,
                    context=context_text,
                    llm=self.llm
                )
                application_guidance = generate_application_guide(
                    user_message=user_message,
                    eligibility_findings=eligibility_findings,
                    context=context_text,
                    llm=self.llm
                )
                final_response = explain_to_citizen(
                    user_message=user_message,
                    profile_summary=profile_summary,
                    intent=intent,
                    eligibility_findings=eligibility_findings,
                    application_guidance=application_guidance,
                    citations=citations_summary,
                    llm=self.llm
                )

        # ----------------------------------------------------------------
        # Structured error handling
        # ----------------------------------------------------------------
        except Exception as e:
            err_str = str(e).lower()

            if any(tok in err_str for tok in ["429", "rate_limit", "quota", "rate limit"]):
                msg = (
                    "The AI service is currently rate-limited or quota-exhausted. "
                    "Please wait a moment and try again, or switch to a different model."
                )
            elif any(tok in err_str for tok in ["api key", "401", "403", "apikey", "api_key"]):
                msg = (
                    "There's an issue with the API key or authentication. "
                    "Please check your API key in the settings and try again."
                )
            elif any(tok in err_str for tok in ["connection", "timeout", "network", "connect"]):
                msg = (
                    "A network or connection error occurred. "
                    "Please check your internet connection and try again."
                )
            else:
                msg = (
                    f"Something went wrong ({type(e).__name__}). Please try again."
                )

            return {
                "final_response": msg,
                "intent_routing": {},
                "retrieved_chunks": [],
                "eligibility_findings": "",
                "application_guidance": "",
                "citations_summary": "",
                "profile": current_profile
            }

        return {
            "final_response": final_response,
            "intent_routing": routing,
            "retrieved_chunks": retrieved_chunks,
            "eligibility_findings": eligibility_findings,
            "application_guidance": application_guidance,
            "citations_summary": citations_summary,
            "profile": current_profile
        }
