# ==============================================================================
# File: app/rag.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 8 - Production Retrieval-Augmented Generation (RAG) pipeline
#              integrating ChromaDB retrieval, prompt augmentation, and grounded synthesis.
# ==============================================================================

import logging
import os
import sys
from typing import Any

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.llm import llm_engine
from app.vectorstore import vector_store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("rag")


class RAGPipeline:
    """
    Retrieval-Augmented Generation (RAG) orchestrator.
    Retrieves nearest official document chunks from ChromaDB, constructs
    an augmented grounded prompt, and synthesizes answers with source citations.
    """

    def __init__(self, default_top_k: int = 3, similarity_threshold: float = 0.18):
        self.default_top_k = default_top_k
        self.similarity_threshold = similarity_threshold

    def answer_question(
        self,
        question: str,
        user_name: str = "Homeowner",
        top_k: int | None = None
    ) -> dict[str, Any]:
        """
        Execute full RAG workflow for a user question.

        Steps:
        1. Query ChromaDB for top-k semantically relevant chunks.
        2. Evaluate retrieval quality (similarity score).
        3. Augment prompt with retrieved official chunks and issue dates.
        4. Generate grounded synthesis with citations and honest fallback for Q6.
        """
        k = top_k or self.default_top_k
        cleaned_query = question.strip()

        # Step 1: Retrieve relevant chunks from ChromaDB
        hits = vector_store.query(query_text=cleaned_query, n_results=k)

        # Step 2: Quality indicator
        top_score = hits[0]["similarity_score"] if hits else 0.0

        # Step 3: Augment Context
        context_blocks = []
        citations = []
        sources = []

        for h in hits:
            meta = h["metadata"]
            citation_str = f"{meta.get('document_title')} ({meta.get('date_issued')}), Topic: {meta.get('topic')}"
            citations.append(citation_str)
            sources.append({
                "chunk_id": h["chunk_id"],
                "document_title": meta.get("document_title"),
                "date_issued": meta.get("date_issued"),
                "topic": meta.get("topic"),
                "source_url": meta.get("source_url"),
                "similarity_score": h["similarity_score"]
            })
            context_blocks.append(
                f"[Source: {meta.get('document_title')} | Date: {meta.get('date_issued')} | Topic: {meta.get('topic')}]\n"
                f"{h['text']}"
            )

        augmented_context = "\n\n".join(context_blocks)

        # Step 4: Generate Grounded Answer via LLM Engine
        llm_result = llm_engine.generate(
            question=cleaned_query,
            user_name=user_name,
            context_override=augmented_context
        )

        answer_text = llm_result.get("answer", "")
        confidence = llm_result.get("confidence", "medium")

        # Refusal check for unanswerable queries (Q6)
        if "cannot confirm this from the available official documents" in answer_text.lower():
            confidence = "low"
            citations = []
            sources = []
        elif top_score >= self.similarity_threshold and confidence != "low":
            confidence = "high"

        return {
            "question": cleaned_query,
            "answer": answer_text,
            "confidence": confidence,
            "retrieval_score": top_score,
            "follow_up": llm_result.get("follow_up", "Would you like more information?"),
            "citations": citations,
            "sources": sources
        }


# Global singleton instance
rag_pipeline = RAGPipeline()


if __name__ == "__main__":
    print("=" * 75)
    print("🚀 TESTING COMPLETE RAG PIPELINE (app/rag.py)")
    print("=" * 75)

    test_queries = [
        "How much central subsidy will I get for a 3 kW rooftop solar system?",
        "What will MSEDCL's electricity tariff per unit be next year?",
        "How much terrace space is required per kW of solar panels?"
    ]

    for q in test_queries:
        print(f"\n❓ User Question: \"{q}\"")
        res = rag_pipeline.answer_question(q, user_name="Abhishek Dighe")
        print(f"   Confidence:      {res['confidence']} (Score: {res['retrieval_score']})")
        print(f"   Answer:          {res['answer'][:110]}...")
        print(f"   Citations Count: {len(res['citations'])}")
        for c in res['citations']:
            print(f"    • {c}")
    print("\n" + "=" * 75)
