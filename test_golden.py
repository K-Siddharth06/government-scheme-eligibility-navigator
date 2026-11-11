"""
Golden Evaluation Test Suite for Government Scheme Eligibility Navigator
Tests retrieval precision over 12 cases covering all intents and scheme types.
Outputs Precision@4 score and saves results to test_golden_results.json.
"""
import sys
import json
import os

# Ensure project root is on path
sys.path.insert(0, r"C:\Users\User\OneDrive\Desktop\scheme_navigator")

from memory import CitizenProfile
from agents.retrieval_agent import RetrievalAgent

# ---------------------------------------------------------------------------
# Golden test cases
# ---------------------------------------------------------------------------
GOLDEN_CASES = [
    {
        "id": 1,
        "profile": {"age": 45, "state": "Karnataka", "occupation": "farmer",
                    "landholding_acres": 2.0, "annual_income": 90000},
        "query": "What schemes can I get?",
        "expected_schemes": ["PM-KISAN", "Karnataka Raitha Vidya Nidhi"],
        "expected_intent": "scheme_discovery"
    },
    {
        "id": 2,
        "profile": {"age": 35, "state": "Maharashtra", "occupation": "farmer",
                    "landholding_acres": 1.5, "annual_income": 75000},
        "query": "Am I eligible for PM-KISAN?",
        "expected_schemes": ["PM-KISAN"],
        "expected_intent": "eligibility_check"
    },
    {
        "id": 3,
        "profile": {"age": 32, "state": "Punjab", "occupation": "street vendor",
                    "annual_income": 60000},
        "query": "What schemes are available for street vendors?",
        "expected_schemes": ["PM SVANidhi"],
        "expected_intent": "scheme_discovery"
    },
    {
        "id": 4,
        "profile": {"age": 28, "state": "Bihar", "occupation": "daily wage worker",
                    "annual_income": 50000},
        "query": "How do I apply for PM Jan Dhan Yojana?",
        "expected_schemes": ["PM Jan Dhan Yojana"],
        "expected_intent": "application_guidance"
    },
    {
        "id": 5,
        "profile": {"age": 55, "state": "Tamil Nadu", "occupation": "farmer",
                    "landholding_acres": 3.0, "annual_income": 110000},
        "query": "Am I eligible for PM Fasal Bima Yojana?",
        "expected_schemes": ["PM Fasal Bima Yojana"],
        "expected_intent": "eligibility_check"
    },
    {
        "id": 6,
        "profile": {"age": 38, "state": "Rajasthan", "occupation": "small business owner",
                    "annual_income": 200000},
        "query": "Can I get a Mudra loan?",
        "expected_schemes": ["PM Mudra Yojana"],
        "expected_intent": "eligibility_check"
    },
    {
        "id": 7,
        "profile": {"age": 42, "state": "Uttar Pradesh", "occupation": "construction worker",
                    "annual_income": 80000},
        "query": "What health insurance schemes can I avail?",
        "expected_schemes": ["Ayushman Bharat PM-JAY"],
        "expected_intent": "scheme_discovery"
    },
    {
        "id": 8,
        "profile": {"age": 20, "state": "Karnataka", "occupation": "student",
                    "annual_income": 40000},
        "query": "What scholarship or education schemes can a student get in Karnataka?",
        "expected_schemes": ["Raitha Vidya Nidhi"],
        "expected_intent": "scheme_discovery"
    },
    {
        "id": 9,
        "profile": {"age": 30, "state": "Madhya Pradesh", "occupation": "homemaker",
                    "annual_income": 180000},
        "query": "Am I eligible for Ladli Behna scheme?",
        "expected_schemes": ["Ladli Behna Yojana"],
        "expected_intent": "eligibility_check"
    },
    {
        "id": 10,
        "profile": {"age": 62, "state": "Gujarat", "occupation": "retired",
                    "annual_income": 120000},
        "query": "What savings schemes are available for senior citizens?",
        "expected_schemes": ["Senior Citizen Savings Scheme"],
        "expected_intent": "scheme_discovery"
    },
    {
        "id": 11,
        "profile": {"age": 29, "state": "West Bengal", "occupation": "auto driver",
                    "annual_income": 72000},
        "query": "How do I register for e-Shram card?",
        "expected_schemes": ["e-Shram Card"],
        "expected_intent": "application_guidance"
    },
    {
        "id": 12,
        "profile": {"age": 48, "state": "Odisha", "occupation": "BPL household",
                    "annual_income": 35000},
        "query": "How can I get subsidised ration under food security scheme?",
        "expected_schemes": ["NFSA Ration Card"],
        "expected_intent": "scheme_discovery"
    },
]


# ---------------------------------------------------------------------------
# Evaluation runner
# ---------------------------------------------------------------------------
def run_golden_evaluation():
    retriever = RetrievalAgent()
    results = []
    hits = 0

    print("=" * 70)
    print("Golden Evaluation — Precision@4 Test")
    print("=" * 70)

    for case in GOLDEN_CASES:
        # Build profile (only fields present in the test dict)
        p = CitizenProfile()
        for field, value in case["profile"].items():
            if hasattr(p, field):
                setattr(p, field, value)

        # Enrich query with occupation and state for better retrieval
        occupation = case["profile"].get("occupation", "")
        state = case["profile"].get("state", "")
        enriched_query = " ".join(filter(None, [case["query"], occupation, state]))

        # Retrieve top-4 chunks
        try:
            chunks = retriever.retrieve(enriched_query, top_k=4)
        except Exception as exc:
            chunks = []
            print(f"  [WARN] Retrieval error for case {case['id']}: {exc}")

        # Check if any expected scheme appears in retrieved chunks
        retrieved_names = set()
        for chunk in chunks:
            retrieved_names.add(chunk.get("scheme", "").lower())
            retrieved_names.add(chunk.get("short_name", "").lower())

        matched_schemes = []
        for expected in case["expected_schemes"]:
            expected_lower = expected.lower()
            # Partial / substring match to handle naming variations
            found = any(
                expected_lower in name or name in expected_lower
                for name in retrieved_names
                if name
            )
            if found:
                matched_schemes.append(expected)

        is_hit = len(matched_schemes) > 0
        if is_hit:
            hits += 1

        result_entry = {
            "id": case["id"],
            "query": case["query"],
            "expected_schemes": case["expected_schemes"],
            "expected_intent": case["expected_intent"],
            "retrieved_schemes": [
                {"scheme": c.get("scheme"), "short_name": c.get("short_name"),
                 "distance": c.get("distance")}
                for c in chunks
            ],
            "matched_schemes": matched_schemes,
            "hit": is_hit
        }
        results.append(result_entry)

        status = "HIT ✓" if is_hit else "MISS ✗"
        print(f"\nCase {case['id']:>2} [{status}] — {case['query'][:55]}")
        print(f"           Expected : {case['expected_schemes']}")
        print(f"           Retrieved: {[c.get('scheme') for c in chunks]}")
        if matched_schemes:
            print(f"           Matched  : {matched_schemes}")

    precision_at_4 = hits / len(GOLDEN_CASES)
    print("\n" + "=" * 70)
    print(f"Precision@4: {hits}/{len(GOLDEN_CASES)} cases found expected schemes in top-4 results")
    print(f"Score: {precision_at_4:.2%}")
    print("=" * 70)

    # Save results
    output = {
        "precision_at_4": f"{hits}/{len(GOLDEN_CASES)}",
        "score": round(precision_at_4, 4),
        "cases": results
    }
    output_path = r"C:\Users\User\OneDrive\Desktop\scheme_navigator\test_golden_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")
    return output


if __name__ == "__main__":
    run_golden_evaluation()
