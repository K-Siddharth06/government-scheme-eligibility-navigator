"""
Retrieval Agent: Semantic Search in ChromaDB
Performs similarity search over indexed official scheme guidelines with metadata citations.
"""
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from config import get_embeddings, CHROMA_PERSIST_DIR

class RetrievalAgent:
    def __init__(self):
        self.embeddings = get_embeddings()
        self.vector_db = Chroma(
            collection_name="schemes_catalog",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PERSIST_DIR
        )

    def retrieve(self, query: str, top_k: int = 4, filter_dict: dict = None) -> List[Dict[str, Any]]:
        """
        Executes similarity search in ChromaDB.
        Returns retrieved document chunks accompanied by scores and metadata.
        """
        try:
            results_with_scores = self.vector_db.similarity_search_with_score(
                query=query,
                k=top_k,
                filter=filter_dict
            )
        except Exception as e:
            # Fallback without filter if filter syntax raises
            results_with_scores = self.vector_db.similarity_search_with_score(query=query, k=top_k)

        formatted_chunks = []
        for doc, score in results_with_scores:
            meta = doc.metadata or {}
            formatted_chunks.append({
                "content": doc.page_content,
                "scheme": meta.get("scheme", "Unknown Scheme"),
                "short_name": meta.get("short_name", "Scheme"),
                "category": meta.get("category", "General"),
                "level": meta.get("level", "Central/State"),
                "source_file": meta.get("source_file", "Official Document"),
                "source_url": meta.get("source_url", "https://india.gov.in"),
                "page": meta.get("page_number", 1),
                "distance": round(float(score), 4)
            })

        return formatted_chunks

    def retrieve_with_quality_check(
        self,
        query: str,
        top_k: int = 4,
        distance_threshold: float = 1.2,
        filter_dict: dict = None
    ) -> Dict[str, Any]:
        """
        Retrieves chunks and applies a relevance quality gate.
        Returns a dict with:
          - {"no_relevant_docs": True,  "query": query, "best_distance": float|None}  if below threshold
          - {"no_relevant_docs": False, "chunks": List[Dict]}                          if above threshold
        """
        chunks = self.retrieve(query, top_k=top_k, filter_dict=filter_dict)

        best_distance = chunks[0]["distance"] if chunks else None

        if len(chunks) == 0 or (best_distance is not None and best_distance > distance_threshold):
            return {
                "no_relevant_docs": True,
                "query": query,
                "best_distance": best_distance
            }

        return {
            "no_relevant_docs": False,
            "chunks": chunks
        }

    def format_context_for_prompt(self, chunks: List[Dict[str, Any]]) -> str:
        """Formats chunks into an unambiguous context block with explicit source citations."""
        if not chunks:
            return "No matching official scheme documents found in the database."

        formatted_text = []
        for idx, chunk in enumerate(chunks, 1):
            formatted_text.append(
                f"--- DOCUMENT CHUNK {idx} ---\n"
                f"Scheme: {chunk['scheme']}\n"
                f"Category: {chunk['category']} | Level: {chunk['level']}\n"
                f"Source Document: {chunk['source_file']} (Page {chunk['page']})\n"
                f"Official Portal: {chunk['source_url']}\n"
                f"Content:\n{chunk['content']}\n"
            )
        return "\n".join(formatted_text)
