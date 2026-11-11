"""
Offline Ingestion Script for Government Scheme Documents
Phase 1: PDF Documents -> PyPDFLoader -> RecursiveCharacterSplitter -> ChromaDB Vector Store
Indexes 15 Central and State government schemes with rich metadata.
"""
import os
import sys
import json
import datetime
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from config import get_embeddings, CHROMA_PERSIST_DIR, DATA_DIR

# Scheme metadata registry for automatic tagging (15 schemes)
SCHEME_METADATA_MAP = {
    "pm_kisan": {
        "scheme": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "short_name": "PM-KISAN",
        "category": "Agriculture & Income Support",
        "level": "Central",
        "target_group": "Farmers, Landholders",
        "source_url": "https://pmkisan.gov.in"
    },
    "ayushman_bharat": {
        "scheme": "Ayushman Bharat PM-JAY (Pradhan Mantri Jan Arogya Yojana)",
        "short_name": "Ayushman Bharat",
        "category": "Healthcare & Health Insurance",
        "level": "Central",
        "target_group": "BPL, Rural Deprived, Low-Income Families",
        "source_url": "https://pmjay.gov.in"
    },
    "raitha_vidya": {
        "scheme": "Karnataka Raitha Vidya Nidhi",
        "short_name": "Raitha Vidya Nidhi",
        "category": "Education & Scholarship",
        "level": "State (Karnataka)",
        "target_group": "Children of Farmers in Karnataka",
        "source_url": "https://raitamitra.karnataka.gov.in"
    },
    "pm_awas": {
        "scheme": "Pradhan Mantri Awas Yojana - Gramin (PMAY-G)",
        "short_name": "PMAY-G",
        "category": "Housing & Rural Development",
        "level": "Central",
        "target_group": "Homeless, Kutcha House Dwellers, Rural Poor",
        "source_url": "https://pmayg.nic.in"
    },
    "pm_svanidhi": {
        "scheme": "PM SVANidhi (PM Street Vendor's AtmaNirbhar Nidhi)",
        "short_name": "PM SVANidhi",
        "category": "Livelihood & Micro-Credit",
        "level": "Central",
        "target_group": "Urban Street Vendors, Hawkers",
        "source_url": "https://pmsvanidhi.mohua.gov.in"
    },
    "pm_fasal_bima": {
        "scheme": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "short_name": "PM Fasal Bima",
        "category": "Agriculture & Insurance",
        "level": "Central",
        "target_group": "Farmers, Sharecroppers, Tenant Farmers",
        "source_url": "https://pmfby.gov.in"
    },
    "sukanya_samriddhi": {
        "scheme": "Sukanya Samriddhi Yojana (SSY)",
        "short_name": "Sukanya Samriddhi",
        "category": "Girl Child & Financial Savings",
        "level": "Central",
        "target_group": "Parents of Girl Children under 10 years",
        "source_url": "https://www.indiapost.gov.in"
    },
    "pm_mudra": {
        "scheme": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "short_name": "PM Mudra",
        "category": "MSME, Livelihood & Business Loans",
        "level": "Central",
        "target_group": "Micro-entrepreneurs, Small Businesses, Artisans",
        "source_url": "https://www.mudra.org.in"
    },
    "atal_pension": {
        "scheme": "Atal Pension Yojana (APY)",
        "short_name": "Atal Pension",
        "category": "Social Security & Pension",
        "level": "Central",
        "target_group": "Unorganized Sector Workers aged 18-40",
        "source_url": "https://www.npscra.nsdl.co.in"
    },
    "pmegp": {
        "scheme": "Prime Minister's Employment Generation Programme (PMEGP)",
        "short_name": "PMEGP",
        "category": "Employment & Self-Employment Subsidy",
        "level": "Central",
        "target_group": "Aspiring Entrepreneurs aged 18+",
        "source_url": "https://www.kviconline.gov.in"
    },
    "e_shram": {
        "scheme": "e-Shram Portal (National Database of Unorganised Workers)",
        "short_name": "e-Shram",
        "category": "Labour Welfare & Social Security",
        "level": "Central",
        "target_group": "Unorganised Workers aged 16-59",
        "source_url": "https://eshram.gov.in"
    },
    "pm_jan_dhan": {
        "scheme": "Pradhan Mantri Jan-Dhan Yojana (PMJDY)",
        "short_name": "PM Jan Dhan",
        "category": "Banking & Financial Inclusion",
        "level": "Central",
        "target_group": "All Unbanked Citizens aged 10+",
        "source_url": "https://pmjdy.gov.in"
    },
    "nfsa_ration": {
        "scheme": "National Food Security Act (NFSA) - Ration Card",
        "short_name": "NFSA Ration Card",
        "category": "Food Security & Social Welfare",
        "level": "Central & State",
        "target_group": "BPL, AAY, Priority Households",
        "source_url": "https://nfsa.gov.in"
    },
    "senior_citizen": {
        "scheme": "Senior Citizen Savings Scheme (SCSS)",
        "short_name": "Senior Citizen Savings",
        "category": "Senior Citizens & Retirement Savings",
        "level": "Central",
        "target_group": "Senior Citizens aged 60+ (or 55+ VRS)",
        "source_url": "https://www.indiapost.gov.in"
    },
    "ladli_behna": {
        "scheme": "Mukhyamantri Ladli Behna Yojana (MP)",
        "short_name": "Ladli Behna",
        "category": "Women Empowerment & Direct Income Support",
        "level": "State (Madhya Pradesh)",
        "target_group": "Women aged 21-60 in MP with income < 2.5L",
        "source_url": "https://cmladlibehna.mp.gov.in"
    }
}

def resolve_metadata(filename: str):
    lower_fn = filename.lower()
    for key, meta in SCHEME_METADATA_MAP.items():
        if key in lower_fn:
            return meta
    return {
        "scheme": Path(filename).stem.replace("_", " ").title(),
        "short_name": Path(filename).stem.replace("_", " ").title(),
        "category": "General Welfare",
        "level": "Central/State",
        "target_group": "Citizens",
        "source_url": "https://india.gov.in"
    }

def ingest_documents(force_reindex: bool = False):
    print("=" * 70)
    print("GOVERNMENT SCHEME ELIGIBILITY NAVIGATOR - INGESTION PIPELINE")
    print("=" * 70)

    pdf_files = list(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {DATA_DIR}!")
        return None

    print(f"Found {len(pdf_files)} PDF document(s) in {DATA_DIR}...")

    all_docs = []
    for pdf_path in pdf_files:
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        meta = resolve_metadata(pdf_path.name)
        
        for idx, page_doc in enumerate(pages):
            page_doc.metadata.update({
                "scheme": meta["scheme"],
                "short_name": meta["short_name"],
                "category": meta["category"],
                "level": meta["level"],
                "target_group": meta["target_group"],
                "source_url": meta["source_url"],
                "source_file": pdf_path.name,
                "page_number": idx + 1
            })
            all_docs.append(page_doc)

    print(f"Total loaded pages across all schemes: {len(all_docs)}")

    # Chunking: chunk_size=800, overlap=100
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(all_docs)
    print(f"Created {len(chunks)} text chunks with overlap=100")

    # Embed and store in ChromaDB
    print("\nGenerating embeddings and storing in ChromaDB...")
    embeddings = get_embeddings()

    # Re-create/overwrite collection
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name="schemes_catalog"
    )

    # Save index metadata for UI and auditing
    meta_path = Path(CHROMA_PERSIST_DIR) / "index_meta.json"
    meta_info = {
        "last_indexed": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pdf_count": len(pdf_files),
        "chunk_count": len(chunks),
        "schemes": [meta["short_name"] for meta in SCHEME_METADATA_MAP.values()]
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=2)

    print(f"\nSuccessfully indexed {len(chunks)} chunks from {len(pdf_files)} schemes into ChromaDB at:")
    print(f"-> {CHROMA_PERSIST_DIR}")
    print(f"Metadata saved to {meta_path}")
    print("=" * 70)
    return vector_db

if __name__ == "__main__":
    ingest_documents()
