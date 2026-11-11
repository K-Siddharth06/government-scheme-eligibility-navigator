"""
Explainer Agent
Synthesizes multi-agent outputs into simple, empathetic, citizen-friendly language.
Ensures source citations and asks follow-up questions if profile information is incomplete.
Demonstrates:
- Zero-Shot Persona & Grounded Prompting
- Reflection / Grounding Verifier pass (Prompt Engineering technique 4)
"""
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

EXPLAINER_SYSTEM_PROMPT = """You are the Citizen Explainer Agent for the Government Scheme Eligibility Navigator.
Your role is to translate complex bureaucratic guidelines and legal criteria into warm, clear, plain language that any citizen can easily understand.

GUIDELINES FOR YOUR RESPONSE:
1. Tone: Respectful, helpful, empathetic, and encouraging.
2. Structure:
   - Quick Summary: Directly answer the citizen's question in 1-2 simple sentences.
   - Schemes You Qualify For: Bullet points with Scheme Name, What You Get (exact benefit amount/coverage), and Why You Qualify.
   - What Documents to Keep Ready: Bullet list of required items (e.g. Aadhaar, Bank Passbook, Land RTC).
   - How to Apply: Simple step-by-step guidance (mentioning online portal or local CSC/Panchayat).
   - Follow-up Questions: If any crucial detail is missing (e.g., annual income, land size, state domicile, or tax status), ask a polite, conversational follow-up question instead of guessing.
   - Official Sources & Verification: Cite the official document name, page number, and portal URL for every claim made.
3. Strict Grounding: Never invent schemes, eligibility amounts, or dates not present in the verified context."""

EXPLAINER_USER_PROMPT = """CITIZEN PROFILE:
{profile_summary}

CONVERSATION CONTEXT:
{chat_context}

CITIZEN QUESTION:
{user_message}

INTENT DETECTED:
{intent}

ELIGIBILITY REASONING:
{eligibility_findings}

APPLICATION DETAILS:
{application_guidance}

VERIFIED SOURCE CITATIONS:
{citations}

Produce a warm, citizen-friendly explanation following all instructions."""

EXPLAINER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", EXPLAINER_SYSTEM_PROMPT),
    ("human", EXPLAINER_USER_PROMPT)
])

# ------------------------------------------------------------------------------
# REFLECTION & GROUNDING VERIFIER (Prompt Engineering Technique 4)
# ------------------------------------------------------------------------------
GROUNDING_VERIFIER_SYSTEM_PROMPT = """You are a Strict Grounding Auditor for Indian Government Scheme information.
Review the drafted citizen response against the retrieved source context chunks.

Audit Checklist:
1. Are all stated monetary benefits (e.g. Rs 6,000, Rs 5 Lakh, Rs 10,000) accurate as per context?
2. Are all required documents actually listed in the context?
3. Did the draft avoid hallucinating schemes not present in the context?

If the draft is 100% grounded, return it UNCHANGED.
If any unsupported claim exists, remove or correct it while preserving the citizen-friendly tone."""

GROUNDING_VERIFIER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", GROUNDING_VERIFIER_SYSTEM_PROMPT),
    ("human", "RETRIEVED OFFICIAL CONTEXT:\n{context}\n\nDRAFT RESPONSE:\n{draft}\n\nVERIFIED RESPONSE:")
])

def explain_to_citizen(
    user_message: str,
    profile_summary: str,
    intent: str,
    eligibility_findings: str,
    application_guidance: str,
    citations: str,
    llm,
    chat_context: str = "",
    context_chunks_text: str = "",
    run_reflection_check: bool = False
) -> str:
    """Executes the citizen explanation synthesis via LCEL with optional Reflection pass."""
    chain = EXPLAINER_PROMPT | llm | StrOutputParser()
    draft = chain.invoke({
        "user_message": user_message,
        "profile_summary": profile_summary,
        "chat_context": chat_context or "Starting conversation.",
        "intent": intent,
        "eligibility_findings": eligibility_findings or "No formal eligibility evaluation required for this inquiry.",
        "application_guidance": application_guidance or "Refer to the official portal for application schedules.",
        "citations": citations
    })

    # Optional Reflection / Grounding Verifier pass
    if run_reflection_check and context_chunks_text:
        try:
            verifier_chain = GROUNDING_VERIFIER_PROMPT | llm | StrOutputParser()
            verified = verifier_chain.invoke({
                "context": context_chunks_text[:3000],
                "draft": draft
            })
            return verified
        except Exception:
            return draft

    return draft
