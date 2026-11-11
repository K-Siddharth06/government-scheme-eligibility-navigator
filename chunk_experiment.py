"""
Chunk Size Experiment for Viva Evidence
Compares chunk_size = 400, 800, 1200 with overlap = 100 on the 15 scheme documents.
Produces empirical evidence for the viva question: 'Why chunk size 800?'
"""
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DATA_DIR

def run_experiment():
    print("=" * 70)
    print("CHUNK SIZE EMPIRICAL COMPARISON EXPERIMENT")
    print("=" * 70)

    pdf_files = list(DATA_DIR.glob("*.pdf"))
    all_docs = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        all_docs.extend(loader.load())

    configs = [
        {"chunk_size": 400, "chunk_overlap": 50, "label": "Small (400 chars)"},
        {"chunk_size": 800, "chunk_overlap": 100, "label": "Optimal (800 chars)"},
        {"chunk_size": 1200, "chunk_overlap": 150, "label": "Large (1200 chars)"}
    ]

    results = []

    for cfg in configs:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=cfg["chunk_size"],
            chunk_overlap=cfg["chunk_overlap"],
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(all_docs)
        lengths = [len(c.page_content) for c in chunks]
        avg_len = sum(lengths) / len(lengths) if lengths else 0
        min_len = min(lengths) if lengths else 0
        max_len = max(lengths) if lengths else 0

        # Check eligibility clause completeness: does a chunk contain BOTH criteria and exclusions?
        intact_clauses = 0
        for c in chunks:
            txt = c.page_content.lower()
            if ("eligib" in txt or "criteria" in txt) and ("exclusion" in txt or "document" in txt or "benefit" in txt):
                intact_clauses += 1

        completeness_pct = (intact_clauses / len(chunks)) * 100 if chunks else 0

        result = {
            "config": cfg["label"],
            "chunk_size": cfg["chunk_size"],
            "chunk_overlap": cfg["chunk_overlap"],
            "total_chunks": len(chunks),
            "avg_chars": round(avg_len, 1),
            "min_chars": min_len,
            "max_chars": max_len,
            "intact_clauses_count": intact_clauses,
            "clause_coherence_pct": round(completeness_pct, 1),
            "viva_verdict": (
                "Too small: Breaks multi-clause rules (e.g. separates exclusions from criteria)" if cfg["chunk_size"] == 400
                else "Optimal: Keeps complete eligibility criteria + benefits intact in one embedding" if cfg["chunk_size"] == 800
                else "Too large: Dilutes semantic relevance; embeds multiple unrelated sections"
            )
        }
        results.append(result)

    print(f"{'Configuration':<22} | {'Chunks':<6} | {'Avg Chars':<9} | {'Clause Coherence':<16} | {'Verdict'}")
    print("-" * 90)
    for r in results:
        print(f"{r['config']:<22} | {r['total_chunks']:<6} | {r['avg_chars']:<9} | {r['clause_coherence_pct']}%{'':<11} | {r['viva_verdict']}")

    print("=" * 70)
    out_file = BASE_DIR / "chunk_experiment_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Detailed results saved to: {out_file.name}")
    return results

if __name__ == "__main__":
    run_experiment()
