"""
Intent Router & Agentic Decision Engine
Detects user intent (Scheme Discovery, Eligibility Check, Application Guidance, Profile Update, Greeting),
decides whether vector retrieval is required, and checks for missing profile fields.
"""
import json
import re
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

ROUTER_SYSTEM_PROMPT = """You are the Intent Routing Agent for the Indian Government Scheme Eligibility Navigator.
Analyze the user's message in the context of their known profile and chat history.

Your tasks:
1. Classify the user's intent into ONE of:
   - "scheme_discovery": User is describing their situation, asking what schemes they can get, or seeking general scheme recommendations.
     Example: "I am a 45-year-old farmer in Karnataka with 2 acres of land and ₹90,000 income. What schemes can I get?"
   - "eligibility_check": User is asking whether they qualify for a specific scheme.
     Example: "Am I eligible for PM-KISAN?", "Can I get Ayushman Bharat?"
   - "application_guidance": User is asking how to apply or what documents are needed for a scheme.
     Example: "How do I apply for Ayushman Bharat?", "What documents do I need for PM-KISAN?"
   - "profile_update": User is solely providing personal demographic/income details without an explicit question.
     Example: "My income is 90000 rupees", "I have 2 acres of land", "I live in Karnataka"
   - "chitchat_or_greeting": Salutations, gratitude, or off-topic conversation not requiring scheme database search.
     Example: "Hello", "Thank you", "Who created you?", "What is my current profile?"

2. Determine if document retrieval from the vector database is required:
   - "needs_retrieval": true for "scheme_discovery", "eligibility_check", and "application_guidance".
   - "needs_retrieval": false for "chitchat_or_greeting" and pure "profile_update".

3. Formulate an optimized "search_query" for vector similarity search (if needs_retrieval is true).

4. Detect if crucial profile information is missing for an accurate eligibility evaluation:
   - For a farmer/discovery check, key fields are: age, state, occupation, land size, annual income.
   - If key information is missing, list the specific missing fields.

Output ONLY a JSON object in this format:
{{
    "intent": "scheme_discovery" | "eligibility_check" | "application_guidance" | "profile_update" | "chitchat_or_greeting",
    "target_scheme": "<Specific scheme name if mentioned, otherwise null>",
    "needs_retrieval": true | false,
    "search_query": "<Semantic search query string>",
    "missing_fields": ["<field1>", "<field2>"],
    "reasoning": "<Short chain-of-thought explanation for this routing decision>"
}}
Do NOT output code blocks or other text outside the JSON."""

ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ROUTER_SYSTEM_PROMPT),
    ("human", "Known Citizen Profile: {profile_summary}\n\nRecent Chat Context: {chat_context}\n\nUser Message: {user_message}\n\nRouting Decision JSON:")
])

def route_user_intent(user_message: str, profile_summary: str, chat_context: str, llm) -> Dict[str, Any]:
    """LCEL-based routing chain with Chain-of-Thought decision making."""
    chain = ROUTER_PROMPT | llm | StrOutputParser()
    try:
        raw = chain.invoke({
            "profile_summary": profile_summary,
            "chat_context": chat_context,
            "user_message": user_message
        })
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        data = json.loads(cleaned)
        return data
    except Exception as e:
        # Fallback rule-based routing if LLM parsing fails
        lower = user_message.lower()
        if any(w in lower for w in ["what schemes", "which scheme", "suggest scheme", "recommend scheme", "schemes for me", "schemes can i get"]):
            intent = "scheme_discovery"
            needs_retrieval = True
        elif any(w in lower for w in ["how to apply", "application", "documents required", "portal"]):
            intent = "application_guidance"
            needs_retrieval = True
        elif any(w in lower for w in ["eligible", "qualify", "can i get", "am i eligible"]):
            intent = "eligibility_check"
            needs_retrieval = True
        elif any(w in lower for w in ["hello", "hi", "hey", "thanks", "thank you"]):
            intent = "chitchat_or_greeting"
            needs_retrieval = False
        else:
            intent = "scheme_discovery"
            needs_retrieval = True

        return {
            "intent": intent,
            "target_scheme": None,
            "needs_retrieval": needs_retrieval,
            "search_query": user_message,
            "missing_fields": [],
            "reasoning": f"Rule-based fallback route triggered: {str(e)}"
        }
