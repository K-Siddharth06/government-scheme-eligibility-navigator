"""
Citizen Profile & Memory Management
Tracks citizen demographic and financial attributes across chat turns.
"""
from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any
import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

@dataclass
class CitizenProfile:
    age: Optional[int] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    landholding_acres: Optional[float] = None
    annual_income: Optional[float] = None
    category: Optional[str] = None  # e.g., "Farmer", "Street Vendor", "Student", "BPL", "Rural"
    housing_type: Optional[str] = None  # e.g., "Kutcha house", "Pucca house", "Homeless"
    is_taxpayer: Optional[bool] = None
    is_gov_employee: Optional[bool] = None
    extra_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}

    def summary_text(self) -> str:
        parts = []
        if self.age is not None:
            parts.append(f"Age: {self.age} years")
        if self.state:
            parts.append(f"State: {self.state}")
        if self.occupation:
            parts.append(f"Occupation: {self.occupation}")
        if self.landholding_acres is not None:
            parts.append(f"Landholding: {self.landholding_acres} acres")
        if self.annual_income is not None:
            parts.append(f"Annual Income: ₹{self.annual_income:,.0f}")
        if self.category:
            parts.append(f"Category: {self.category}")
        if self.housing_type:
            parts.append(f"Housing: {self.housing_type}")
        if self.is_taxpayer is not None:
            parts.append(f"Taxpayer: {'Yes' if self.is_taxpayer else 'No'}")
        if self.is_gov_employee is not None:
            parts.append(f"Govt Employee: {'Yes' if self.is_gov_employee else 'No'}")
        
        if not parts:
            return "No profile details provided yet."
        return ", ".join(parts)

    def missing_fields_for_eligibility(self) -> list[str]:
        missing = []
        if self.occupation is None:
            missing.append("occupation (e.g., farmer, street vendor, student, worker)")
        if self.state is None:
            missing.append("state of residence (e.g., Karnataka, Maharashtra, etc.)")
        if self.annual_income is None:
            missing.append("approximate annual household income")
        if self.age is None:
            missing.append("age")
        return missing

    def update_from_extracted(self, extracted: Dict[str, Any]):
        for key, value in extracted.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)


# LCEL Chain for Profile Extraction
EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an accurate entity extraction assistant for an Indian Government Scheme Navigator.
Extract citizen profile details from the user's message.
Update or fill in any newly mentioned attributes.

Return ONLY a valid JSON object matching these optional fields (null if not mentioned):
{{
    "age": <integer or null>,
    "state": <string or null, e.g. "Karnataka", "Tamil Nadu">,
    "occupation": <string or null, e.g. "farmer", "street vendor", "student", "daily wage worker">,
    "landholding_acres": <float or null, e.g. 2.0>,
    "annual_income": <float or null in INR rupees, e.g. 90000>,
    "category": <string or null, e.g. "small farmer", "BPL", "rural">,
    "housing_type": <string or null, e.g. "kutcha house", "homeless">,
    "is_taxpayer": <boolean or null>,
    "is_gov_employee": <boolean or null>
}}
Do NOT output markdown blocks or explanations, only valid JSON."""),
    ("human", "Current known profile: {current_profile}\n\nUser Message: {user_message}\n\nExtracted JSON:")
])

def extract_profile_updates(user_message: str, current_profile: CitizenProfile, llm) -> Dict[str, Any]:
    """Uses LCEL to extract structured citizen profile attributes from conversational input."""
    chain = EXTRACTION_PROMPT | llm | StrOutputParser()
    try:
        raw_output = chain.invoke({
            "current_profile": json.dumps(current_profile.to_dict()),
            "user_message": user_message
        })
        # Clean JSON markdown if wrapped
        cleaned = re.sub(r"^```(?:json)?\s*", "", raw_output.strip())
        cleaned = re.sub(r"\s*```$", "", cleaned)
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        # Fallback heuristic regex extraction if LLM formatting fails
        extracted = {}
        # Heuristic for age
        age_m = re.search(r"(\d{1,2})\s*(?:years? old|yr|yo)", user_message, re.IGNORECASE)
        if age_m:
            extracted["age"] = int(age_m.group(1))
        # Heuristic for land
        land_m = re.search(r"([\d\.]+)\s*(?:acres?|hectares?)", user_message, re.IGNORECASE)
        if land_m:
            extracted["landholding_acres"] = float(land_m.group(1))
        # Heuristic for income
        inc_m = re.search(r"(?:rs\.?|₹|inr)?\s*([\d,]+)(?:\s*(?:lakh|lac|k|thousand))?\s*(?:income|annual|per year|annually)?", user_message, re.IGNORECASE)
        if "farmer" in user_message.lower():
            extracted["occupation"] = "farmer"
        if "karnataka" in user_message.lower():
            extracted["state"] = "Karnataka"
        return extracted
