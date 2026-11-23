# ==============================================================================
# File: app/chunking.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 7 - Metadata-preserving document chunking module for
#              PM Surya Ghar scheme rules and FAQs.
# ==============================================================================

import os
import sys
from typing import Any

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Record
from app.records import load_records


def split_text_with_overlap(text: str, chunk_size: int = 350, chunk_overlap: int = 50) -> list[str]:
    """
    Split a long string into overlapping character chunks without cutting words where possible.

    Args:
        text: The input text to chunk.
        chunk_size: Maximum target character length for each chunk.
        chunk_overlap: Number of characters shared between consecutive chunks.

    Returns:
        List of text chunks.
    """
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    text_len = len(cleaned)

    while start < text_len:
        end = start + chunk_size

        # If not at the very end of text, find the nearest space to avoid cutting a word
        if end < text_len:
            space_idx = cleaned.rfind(" ", start, end)
            if space_idx > start:
                end = space_idx

        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move the sliding window forward by chunk_size - chunk_overlap
        step = chunk_size - chunk_overlap
        if step <= 0:
            step = chunk_size
        start += step

        if end >= text_len:
            break

    return chunks


def chunk_records(
    records: list[Record] | None = None,
    chunk_size: int = 350,
    chunk_overlap: int = 50
) -> list[dict[str, Any]]:
    """
    Chunk official scheme records while strictly preserving source metadata.

    Every resulting chunk preserves:
    - document_title
    - issuing_body
    - date_issued
    - topic
    - source_url
    - record_id
    - chunk_index
    """
    if records is None:
        records = load_records()

    chunked_docs: list[dict[str, Any]] = []

    for record in records:
        full_content = f"Topic: {record.topic}. Rule: {record.key_rule}"
        text_slices = split_text_with_overlap(full_content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        for idx, slice_text in enumerate(text_slices):
            chunk_id = f"doc_{record.id}_c{idx + 1}"
            chunked_docs.append({
                "chunk_id": chunk_id,
                "text": slice_text,
                "metadata": {
                    "record_id": record.id,
                    "chunk_index": idx + 1,
                    "document_title": record.document_title,
                    "issuing_body": record.issuing_body,
                    "date_issued": record.date_issued,
                    "topic": record.topic,
                    "source_url": record.source_url
                }
            })

    return chunked_docs


if __name__ == "__main__":
    print("=" * 75)
    print("✂️ TESTING DOCUMENT CHUNKING MODULE (app/chunking.py)")
    print("=" * 75)

    all_records = load_records()
    chunks = chunk_records(all_records, chunk_size=300, chunk_overlap=40)
    print(f"Total Input Records: {len(all_records)}")
    print(f"Total Chunks Created: {len(chunks)}")
    print("\nSample Chunk Preview:")
    sample = chunks[3]
    print(f"Chunk ID:  {sample['chunk_id']}")
    print(f"Text:      {sample['text']}")
    print(f"Metadata:  {sample['metadata']}")
    print("=" * 75)
