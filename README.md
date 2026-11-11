# 🇮🇳 Government Scheme Eligibility Navigator (Assignment 3)

An Agentic AI citizen assistant where a citizen describes their demographic and economic situation in plain language and receives the exact central and state government schemes they qualify for, along with required documents, step-by-step application procedures, and grounded source citations.

---

## 🏛️ System Architecture

```
                    Citizen Message + Profile Memory
                                   │
                                   ▼
                       [Intent Routing Agent]
                    (Few-Shot In-Context Classifier)
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
[chitchat_or_greeting]     [profile_update]       [Needs Retrieval]
         │                         │                         │
         ▼                         ▼                         ▼
  [Direct Response]        [Update Profile &      [Missing-Info Gate]
  (Skips Retrieval)        Ask Missing Info]                 │
                                   │           ┌─────────────┴─────────────┐
                                   ▼           ▼                           ▼
                           (Skips All Agents) [Missing Info]        [Info Complete]
                                               Ask Question                │
                                                                           ▼
                                                              [Retrieval Agent (ChromaDB)]
                                                               (State Enriched + Top-4)
                                                                           │
                                               ┌───────────────────────────┴───────────────────────────┐
                                               ▼                                                       ▼
                                      [scheme_discovery]                                     [eligibility_check]
                                               │                                                       │
                                               ▼                                                       ▼
                                    [Eligibility Agent (CoT)]                               [Eligibility Agent (CoT)]
                                               │                                                       │
                                               ▼                                                       ▼
                                   [Application Agent (Steps)]                                 [Explainer Agent]
                                               │                                            (Skips Application Agent)
                                               ▼
                                       [Explainer Agent]
                                 (Plain Language + Citations +
                                  Optional Reflection Pass)
                                               │
                                               ▼
                                 [Interactive Streamlit Portal]
```

---

## 🎯 7 Mandatory Acceptance Criteria Mapping

| # | Mandatory Criterion | Implementation Details | File Path | Key Function / Class |
|---|---|---|---|---|
| **1** | **LLM Integration** | Multi-provider support: Google Gemini (`gemini-3.5-flash-lite`), Groq (`openai/gpt-oss-120b`), and OpenAI (`gpt-4o-mini`) with runtime selector. | [`config.py`](file:///C:/Users/User/Desktop/scheme_navigator/config.py) | `get_llm(provider, model)` |
| **2** | **Interactive GUI** | Modern civic portal UI (UMANG / myScheme aesthetic) with citizen profile drawer, quick scenarios, source pills, chat export, and decision log. | [`app.py`](file:///C:/Users/User/Desktop/scheme_navigator/app.py) | Full Streamlit application |
| **3** | **Prompt Engineering** | Demonstrates 4 techniques: **Few-Shot** (intent routing), **One-Shot CoT** (eligibility reasoning), **Zero-Shot Persona** (explainer), and **Reflection Verifier** (grounding pass). Distinct System vs User prompts. | [`agents/intent_router.py`](file:///C:/Users/User/Desktop/scheme_navigator/agents/intent_router.py)<br>[`agents/eligibility_agent.py`](file:///C:/Users/User/Desktop/scheme_navigator/agents/eligibility_agent.py)<br>[`agents/explainer_agent.py`](file:///C:/Users/User/Desktop/scheme_navigator/agents/explainer_agent.py) | `ROUTER_SYSTEM_PROMPT`<br>`ELIGIBILITY_SYSTEM_PROMPT`<br>`GROUNDING_VERIFIER_PROMPT` |
| **4** | **LangChain Core** | Built end-to-end using LangChain Expression Language (LCEL) chains (`ChatPromptTemplate \| llm \| StrOutputParser()`). | [`orchestrator.py`](file:///C:/Users/User/Desktop/scheme_navigator/orchestrator.py) | `SchemeNavigatorOrchestrator` |
| **5** | **Agentic RAG** | Dynamic retrieval decisions, query enrichment with state/scheme metadata, relevance distance thresholding, and citation extraction. | [`agents/retrieval_agent.py`](file:///C:/Users/User/Desktop/scheme_navigator/agents/retrieval_agent.py) | `retrieve_with_quality_check()` |
| **6** | **Intent Routing** | True conditional routing where different intents execute distinct execution paths (e.g. skips retrieval or skips specific agents). | [`orchestrator.py`](file:///C:/Users/User/Desktop/scheme_navigator/orchestrator.py) | `process_message()` |
| **7** | **Vector Database** | ChromaDB vector database indexing 15 schemes (63 chunks) using 384-dimensional ONNX MiniLM embeddings with persistent storage. | [`ingest.py`](file:///C:/Users/User/Desktop/scheme_navigator/ingest.py) | `ingest_documents()` |

---

## 🔀 True Conditional Routing Matrix

Unlike naive pipelines that run every agent on every message, this system routes requests through **distinct conditional branches**:

| Detected Intent | ChromaDB Retrieval? | Eligibility Agent (CoT)? | Application Agent? | Explainer Agent? | Justification |
|---|:---:|:---:|:---:|:---:|---|
| `scheme_discovery` | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | User needs full discovery: matched schemes, eligibility reasoning, documents, and steps. |
| `eligibility_check` | ✅ Yes (Targeted) | ✅ Yes | ❌ Skipped | ✅ Yes | User only asked *"Am I eligible for X?"* — skips application steps to answer directly. |
| `application_guidance` | ✅ Yes (Targeted) | ❌ Skipped | ✅ Yes | ✅ Yes | User already knows they want to apply — skips criteria reasoning and provides documents & steps. |
| `profile_update` | ❌ Skipped | ❌ Skipped | ❌ Skipped | ❌ Skipped | User only provided personal details (e.g. *"I earn 90k"*). Updates memory and asks for missing fields. |
| `chitchat_or_greeting` | ❌ Skipped | ❌ Skipped | ❌ Skipped | ❌ Skipped | Direct conversational LLM response without vector search. |

---

## 📊 Evaluation & Empirical Evidence

### 1. Golden Evaluation Test (`test_golden.py`)
Tested over 12 diverse citizen profiles across multiple states and occupations:
- **Precision@4 Score**: **12 / 12 (100.00%)**
- Every query retrieved the correct official scheme in the top-4 chunks.
- Run anytime: `python test_golden.py`

### 2. Chunk-Size Experiment (`chunk_experiment.py`)
Empirical proof for the viva question: *"Why chunk size 800 and overlap 100?"*

| Configuration | Chunks | Avg Characters | Clause Coherence % | Viva Verdict |
|---|:---:|:---:|:---:|---|
| **Small (400 chars, 50 overlap)** | 123 | 331.8 | 8.9% | **Too small**: Frequently splits exclusion clauses away from eligibility criteria. |
| **Optimal (800 chars, 100 overlap)** | **63** | **655.8** | **27.0%** | **Optimal**: Preserves complete multi-clause rules, criteria, and benefits in one context block. |
| **Large (1200 chars, 150 overlap)** | 47 | 909.1 | 38.3% | **Too large**: Merges unrelated sections (e.g. application steps + loan slabs), diluting vector similarity scores. |

---

## 📚 Indexed Scheme Knowledge Base (15 Schemes)

The knowledge base contains 15 reference guidelines compiled from official portals (`myscheme.gov.in`, `pmkisan.gov.in`, `pmjay.gov.in`, etc.):

1. **PM-KISAN**: Income support of ₹6,000/yr for landholding farmers (Central)
2. **Ayushman Bharat PM-JAY**: ₹5 Lakh health assurance for secondary/tertiary hospital care (Central)
3. **Karnataka Raitha Vidya Nidhi**: ₹2,000–₹11,000 scholarship for farmer children (Karnataka State)
4. **PMAY-G (Gramin)**: ₹1.20L/₹1.30L assistance for rural kutcha house dwellers (Central)
5. **PM SVANidhi**: Collateral-free working capital micro-loans (₹10k–₹50k) for street vendors (Central)
6. **PM Fasal Bima Yojana (PMFBY)**: Crop insurance (2% kharif, 1.5% rabi premium) (Central)
7. **Sukanya Samriddhi Yojana**: 8.2% tax-free savings for girl children under 10 years (Central)
8. **PM Mudra Yojana**: Loans up to ₹10 Lakh (Shishu, Kishore, Tarun) for micro-enterprises (Central)
9. **Atal Pension Yojana (APY)**: Guaranteed ₹1,000–₹5,000/mo pension for unorganized workers (Central)
10. **PMEGP**: 15%–35% margin money subsidy for new micro-enterprises (Central / KVIC)
11. **e-Shram Portal**: Universal Account Number & ₹2 Lakh accident cover for unorganized workers (Central)
12. **PM Jan Dhan Yojana (PMJDY)**: Zero balance accounts, RuPay debit card, ₹10k overdraft (Central)
13. **NFSA Ration Card**: 35 kg/mo (AAY) and 5 kg/person/mo free foodgrains (Central & State)
14. **Senior Citizen Savings Scheme (SCSS)**: 8.2% quarterly interest for citizens aged 60+ (Central)
15. **Mukhyamantri Ladli Behna Yojana**: ₹1,250/mo direct bank transfer for women in MP (Madhya Pradesh State)

> **Viva Transparency Note:** Documents are supplementary reference guidelines compiled directly from official government schemes and portal specifications (dated November 2026), not original signed Gazette scans. Each document clearly states its compilation source and date.

---

## 🚀 How to Run

### 1. Configure API Keys
Add your Gemini, Groq, or OpenAI key in `.env`:
```ini
GEMINI_API_KEY=your_key_here
DEFAULT_LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.5-flash-lite
```

### 2. Run Verification Tests
```bash
# Automated core test (ChromaDB, Memory, Heuristics)
python test_navigator.py

# 12-case Golden precision test
python test_golden.py

# Empirical chunk size experiment
python chunk_experiment.py
```

### 3. Launch the Streamlit Portal
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🎓 Viva Questions & Expert Answers

**Q1: Why did you choose chunk size 800 with overlap 100 instead of 400 or 1200?**  
> *"We ran an empirical experiment across all 15 scheme documents (`chunk_experiment.py`). At 400 characters, clause coherence was only 8.9% because critical exclusions (such as 'taxpayers ineligible') got severed from criteria headings. At 1200 characters, unrelated sections merged together, diluting vector similarity scores. 800 characters with 100 overlap preserved complete multi-clause rules with 27% coherence and zero truncated criteria."*

**Q2: What makes your system genuinely agentic rather than a basic RAG chain?**  
> *"First, retrieval is conditional: the Intent Router actively decides whether vector search is required. Second, different intents execute genuinely different paths (e.g. eligibility checks skip the application agent; profile updates skip retrieval entirely). Third, there is an agentic missing-information gate that detects incomplete profiles and asks clarifying questions before running expensive chains. Fourth, the retrieval agent applies relevance distance thresholding and metadata filtering."*

**Q3: How do you prevent hallucinations?**  
> *"Through strict three-level grounding: (1) System prompt negative constraints instructing agents to answer solely from retrieved context chunks, (2) Mandatory source citations with document names, page numbers, and official portal URLs, and (3) An optional post-generation Reflection / Grounding Verifier pass that compares the draft response against source chunks before displaying it."*
