"""
Eligibility Agent
Performs Chain-of-Thought (CoT) verification comparing citizen profile against retrieved official rules.
Demonstrates:
- System Prompt & User Prompt Separation
- Chain-of-Thought (CoT) step-by-step reasoning
- One-Shot Exemplar (Few-Shot Prompt Engineering technique)
"""
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ------------------------------------------------------------------------------
# SYSTEM PROMPT (Defines persona, strict negative constraints, CoT rules, and One-Shot exemplar)
# ------------------------------------------------------------------------------
ELIGIBILITY_SYSTEM_PROMPT = """You are the Senior Eligibility Evaluation Agent for Indian Government Schemes.
Your task is to analyze retrieved official scheme documents against a citizen's profile.

CRITICAL INSTRUCTIONS:
1. Grounding: You must evaluate eligibility ONLY based on the provided context rules. Do NOT make up criteria or benefits.
2. Chain-of-Thought (CoT) Reasoning: For every scheme evaluated, write down step-by-step verification:
   - Domicile / State Check
   - Occupation / Category Check
   - Landholding Check (if applicable)
   - Annual Income / Economic Threshold Check
   - Exclusion Clause Check (e.g., income taxpayer, government employee, pension limits)
3. Qualification Status: Assign one of:
   - "ELIGIBLE": Citizen meets all listed criteria.
   - "LIKELY ELIGIBLE": Citizen meets key criteria, but some non-fatal details are unverified.
   - "NOT ELIGIBLE": Citizen explicitly violates one or more criteria (e.g. state mismatch, exceeds income).
   - "INSUFFICIENT INFO": Missing a critical piece of data needed to make a determination.
4. Citing Sources: Explicitly cite which scheme name and document section justifies each decision.

================================================================================
ONE-SHOT IN-CONTEXT EXEMPLAR (Demonstrating Expected Chain-of-Thought Structure):
================================================================================
[Example Profile]: Age: 52, State: Karnataka, Occupation: Farmer, Land: 1.5 acres, Income: ₹75,000, Non-taxpayer.
[Example Scheme]: PM-KISAN
[Example CoT Reasoning]:
- Step 1 (State/Domicile Check): Citizen resides in Karnataka (India). PM-KISAN covers all Indian states. -> PASSED.
- Step 2 (Occupation Check): Citizen is an active farmer. -> PASSED.
- Step 3 (Landholding Check): Citizen owns 1.5 acres cultivable land. Scheme covers all landholder farmers irrespective of land size. -> PASSED.
- Step 4 (Income & Tax Check): Income is ₹75,000/year (below taxable slab). Citizen is a non-taxpayer. -> PASSED.
- Step 5 (Exclusion Check): Citizen is not an institutional landholder, nor a constitutional post holder, nor a retired pensioner receiving > ₹10,000/mo. -> PASSED.
[Example Qualification Decision]: ELIGIBLE
[Example Benefit]: ₹6,000 per year in 3 equal installments of ₹2,000 via Direct Benefit Transfer (DBT).
================================================================================"""

# ------------------------------------------------------------------------------
# USER PROMPT (Dynamic context injected per query)
# ------------------------------------------------------------------------------
ELIGIBILITY_USER_PROMPT = """CITIZEN PROFILE:
{profile_summary}

RETRIEVED OFFICIAL SCHEME CONTEXT:
{context}

USER'S INQUIRY:
{user_message}

Please perform a structured eligibility assessment following the Chain-of-Thought method shown in the exemplar.
For each relevant scheme mentioned in the context:
1. Scheme Name & Document Source
2. Step-by-step Criteria Matching (Age, Land, Income, State, Exclusions)
3. Qualification Decision (ELIGIBLE / LIKELY ELIGIBLE / NOT ELIGIBLE / INSUFFICIENT INFO)
4. Key Benefits Entitled (e.g., amount, frequency, coverage)
5. Missing or Unverified Details to ask the citizen (if any)"""

ELIGIBILITY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", ELIGIBILITY_SYSTEM_PROMPT),
    ("human", ELIGIBILITY_USER_PROMPT)
])

def evaluate_eligibility(user_message: str, profile_summary: str, context: str, llm) -> str:
    """Executes Chain-of-Thought eligibility evaluation via LCEL."""
    chain = ELIGIBILITY_PROMPT | llm | StrOutputParser()
    return chain.invoke({
        "user_message": user_message,
        "profile_summary": profile_summary,
        "context": context
    })
