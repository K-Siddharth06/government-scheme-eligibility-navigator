"""
Application Agent
Extracts required document checklists and step-by-step application instructions from retrieved documents.
"""
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

APPLICATION_SYSTEM_PROMPT = """You are the Application Guidance Agent for Indian Government Schemes.
Your responsibility is to extract practical, accurate application steps and document requirements from official scheme guidelines.

CRITICAL INSTRUCTIONS:
1. Document Checklist: Break documents into Mandatory (e.g. Aadhaar, Bank Passbook, Land RTC) and Supporting (e.g. Income Certificate, Ration Card, Student ID).
2. Step-by-Step Procedure: Provide clear numbering (Step 1, Step 2, etc.) for both:
   - Online mode (official portals, direct registration)
   - Offline / Assisted mode (Common Service Centres (CSC), Gram Panchayat, Taluk office, Ayushman Mitra)
3. Grounding: Rely strictly on the provided context chunks. Include official portal URLs and local touchpoints mentioned in the documents."""

APPLICATION_USER_PROMPT = """OFFICIAL SCHEME CONTEXT:
{context}

ELIGIBILITY FINDINGS:
{eligibility_findings}

USER'S INQUIRY:
{user_message}

Provide clear application instructions:
1. List of Required Documents (Mandatory vs Optional)
2. Online Application Steps (with official website/links if in context)
3. Offline / In-Person Application Options (e.g., CSC, Panchayat, Hospital Helpdesk)
4. Key verification or eKYC requirements to keep in mind."""

APPLICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", APPLICATION_SYSTEM_PROMPT),
    ("human", APPLICATION_USER_PROMPT)
])

def generate_application_guide(user_message: str, eligibility_findings: str, context: str, llm) -> str:
    """Executes Application Guidance generation via LCEL."""
    chain = APPLICATION_PROMPT | llm | StrOutputParser()
    return chain.invoke({
        "user_message": user_message,
        "eligibility_findings": eligibility_findings,
        "context": context
    })
