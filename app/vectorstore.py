# ==============================================================================
# File: app/vectorstore.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 7 - Persistent ChromaDB vector database manager for storing,
#              indexing, and retrieving document chunks with source metadata.
# ==============================================================================

import logging
import os
import sys
from typing import Any

import chromadb

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.chunking import chunk_records
from app.embed import embedder
from app.records import load_records

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("vectorstore")

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")
COLLECTION_NAME = "suryaghar_knowledge_base"


class ChromaVectorStore:
    """
    Manages persistent ChromaDB vector storage and semantic retrieval.
    """

    def __init__(self, persist_dir: str = DB_DIR, collection_name: str = COLLECTION_NAME):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        os.makedirs(persist_dir, exist_ok=True)

        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._ensure_indexed()

    def _ensure_indexed(self) -> None:
        """Populate collection with chunked official documents if empty."""
        current_count = self.collection.count()
        if current_count == 0:
            logger.info("ChromaDB collection is empty. Building index from official records...")
            records = load_records()
            chunks = chunk_records(records, chunk_size=350, chunk_overlap=50)
            self.add_chunks(chunks)
        else:
            logger.info(f"Loaded existing ChromaDB collection with {current_count} indexed chunks.")

    def add_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """
        Embed and insert chunks with metadata and content hashing to avoid duplication.
        """
        if not chunks:
            return 0

        ids = [c["chunk_id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Generate vectors
        embeddings = embedder.embed_batch(texts)

        # Upsert into Chroma collection
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Indexed {len(ids)} chunks into Chroma collection '{self.collection_name}'.")
        return len(ids)

    def query(
        self,
        query_text: str,
        n_results: int = 3,
        where_filter: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute semantic nearest-neighbor search.

        Args:
            query_text: The user's question or search phrase.
            n_results: Number of nearest chunks to retrieve.
            where_filter: Optional metadata filtering (e.g., by issuing_body or date).

        Returns:
            List of matching chunk dictionaries with similarity scores and metadata.
        """
        cleaned = query_text.strip()
        if not cleaned:
            return []

        query_vec = embedder.embed_text(cleaned)

        results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=min(n_results, self.collection.count() or 1),
            where=where_filter
        )

        matches: list[dict[str, Any]] = []
        if results and results.get("ids") and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

            for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
                # Cosine distance to similarity: similarity = 1 - distance
                similarity = round(max(0.0, 1.0 - dist), 4)
                matches.append({
                    "chunk_id": chunk_id,
                    "text": doc,
                    "metadata": meta,
                    "similarity_score": similarity
                })

        return matches


# Global singleton instance
vector_store = ChromaVectorStore()


if __name__ == "__main__":
    print("=" * 75)
    print("🗄️ TESTING CHROMA VECTOR STORE (app/vectorstore.py)")
    print(f"Total Chunks in Collection: {vector_store.collection.count()}")
    print("=" * 75)

    test_queries = [
        "How much subsidy is available for a 3 kW solar system?",
        "What are the minimum warranties on modules and inverters?",
        "How much terrace area is required for rooftop solar?"
    ]

    for q in test_queries:
        print(f"\n❓ Semantic Query: \"{q}\"")
        hits = vector_store.query(q, n_results=2)
        for h in hits:
            print(f"   [Score: {h['similarity_score']:.4f}] Chunk: {h['chunk_id']}")
            print(f"   Topic: {h['metadata'].get('topic')} ({h['metadata'].get('date_issued')})")
            print(f"   Excerpt: {h['text'][:100]}...")
    print("\n" + "=" * 75)
