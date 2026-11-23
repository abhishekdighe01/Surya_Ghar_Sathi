# ==============================================================================
# File: app/smart_search.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 4 - Lexical relevance ranking engine using TF-IDF vectorization
#              and Cosine Similarity to find and rank relevant scheme records.
# ==============================================================================

import os
import sys

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Record
from app.records import load_records


class SmartSearchEngine:
    """
    Ranks scheme records against user queries using TF-IDF and Cosine Similarity.

    TF-IDF (Term Frequency - Inverse Document Frequency) reflects how important
    a word is to a document in a collection. Cosine similarity calculates the
    cosine of the angle between query and document vectors in multi-dimensional space.
    """

    def __init__(self, records: list[Record] | None = None):
        self.records: list[Record] = records if records is not None else load_records()
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),  # unigrams and bigrams for phrases like 'net metering'
            sublinear_tf=True
        )
        self._tfidf_matrix = None
        self._fit()

    def _build_corpus(self) -> list[str]:
        """Combine topic, key_rule, and document_title into a searchable text block."""
        corpus = []
        for r in self.records:
            doc_text = f"{r.topic} {r.key_rule} {r.document_title}"
            corpus.append(doc_text)
        return corpus

    def _fit(self) -> None:
        """Fit TF-IDF vectorizer and compute feature matrix for all records."""
        corpus = self._build_corpus()
        if corpus:
            self._tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 3, min_score: float = 0.05) -> list[tuple[Record, float]]:
        """
        Rank records against the query using cosine similarity.

        Args:
            query: The user search question or phrase.
            top_k: Maximum number of top records to return.
            min_score: Minimum cosine similarity score required for inclusion.

        Returns:
            List of tuples: (Record, similarity_score_float).
        """
        cleaned_query = query.strip()
        if not cleaned_query or self._tfidf_matrix is None:
            return []

        # Vectorize the incoming user query
        query_vec = self.vectorizer.transform([cleaned_query])

        # Compute cosine similarity between query and all record vectors
        scores = cosine_similarity(query_vec, self._tfidf_matrix).flatten()

        # Get indices sorted by similarity score in descending order
        ranked_indices = scores.argsort()[::-1]

        results: list[tuple[Record, float]] = []
        for idx in ranked_indices:
            score = float(scores[idx])
            if score >= min_score:
                results.append((self.records[idx], round(score, 4)))
            if len(results) >= top_k:
                break

        return results


# Global singleton instance for easy import across endpoints
smart_search_engine = SmartSearchEngine()


if __name__ == "__main__":
    print("=" * 70)
    print("🔎 TESTING SMART SEARCH ENGINE (TF-IDF + COSINE SIMILARITY)")
    print("=" * 70)

    test_queries = [
        "How much subsidy do I get for a 3 kW solar system?",
        "What is the required roof terrace area per kW?",
        "How does net metering work with MSEDCL?",
        "What is the minimum warranty on solar panels?"
    ]

    for q in test_queries:
        print(f"\n❓ Query: \"{q}\"")
        matches = smart_search_engine.search(q, top_k=2)
        if not matches:
            print("   No relevant records found.")
        for r, score in matches:
            print(f"   [Score: {score:.4f}] Record #{r.id}: {r.topic}")
            print(f"   Rule excerpt: {r.key_rule[:95]}...")
    print("\n" + "=" * 70)
