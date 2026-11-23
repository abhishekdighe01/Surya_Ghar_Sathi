# ==============================================================================
# File: app/embed.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 7 - Text embedding generator for semantic representation
#              and cosine similarity calculations.
# ==============================================================================

import math
from typing import List, Union
import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class EmbeddingGenerator:
    """
    Generates high-dimensional numerical embeddings for text chunks and queries.
    Uses a normalized 128-dimensional feature projection to ensure fast,
    deterministic, and dependency-safe vector generation.
    """

    def __init__(self, n_features: int = 128):
        self.n_features = n_features
        # HashingVectorizer converts arbitrary text to fixed-size normalized vectors
        self.vectorizer = HashingVectorizer(
            n_features=n_features,
            alternate_sign=False,
            norm="l2",
            ngram_range=(1, 2)
        )

    def embed_text(self, text: str) -> List[float]:
        """Convert a single text string into a normalized embedding vector."""
        if not text.strip():
            return [0.0] * self.n_features
        matrix = self.vectorizer.transform([text])
        return matrix.toarray()[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert a list of text strings into a list of normalized embedding vectors."""
        if not texts:
            return []
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray().tolist()

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Calculate cosine similarity between two float vectors."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(dot / (norm_a * norm_b))


# Global singleton instance
embedder = EmbeddingGenerator()


if __name__ == "__main__":
    print("=" * 75)
    print("🧠 TESTING EMBEDDING GENERATOR (app/embed.py)")
    print("=" * 75)

    s1 = "PM Surya Ghar rooftop solar subsidy calculation"
    s2 = "Central Financial Assistance for residential rooftop panels"
    s3 = "MSEDCL annual electricity tariff for Maharashtra"

    v1 = embedder.embed_text(s1)
    v2 = embedder.embed_text(s2)
    v3 = embedder.embed_text(s3)

    sim_1_2 = embedder.cosine_similarity(v1, v2)
    sim_1_3 = embedder.cosine_similarity(v1, v3)

    print(f"Vector Dimensions: {len(v1)}")
    print(f"Similarity between (Subsidy S1) and (CFA S2): {sim_1_2:.4f} (High conceptual overlap)")
    print(f"Similarity between (Subsidy S1) and (Tariff S3): {sim_1_3:.4f} (Lower conceptual overlap)")
    print("=" * 75)
