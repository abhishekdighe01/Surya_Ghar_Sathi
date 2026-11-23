# ==============================================================================
# File: app/records.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 2 - Data operations module for loading, searching, counting,
#              and retrieving structured solar scheme records.
# ==============================================================================

import json
import os
from typing import List, Dict, Optional, Any
from app.models import Record
from data.sample_records import SAMPLE_RECORDS


def load_records(json_path: Optional[str] = None) -> List[Record]:
    """
    Load records into Record dataclass objects.
    
    Reads from a JSON file if specified and exists; otherwise loads from
    data/sample_records.py as the foundational dataset.
    """
    if json_path and os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            return [Record.from_dict(item) for item in raw_data]

    # Default to sample_records dataset
    return [Record.from_dict(item) for item in SAMPLE_RECORDS]


def search(records: List[Record], keyword: str) -> List[Record]:
    """
    Search records case-insensitively across topic, key_rule, and document_title.
    
    Args:
        records: List of Record dataclass objects.
        keyword: String keyword or phrase to search for.
        
    Returns:
        List of matching Record objects.
    """
    cleaned_query = keyword.strip().lower()
    if not cleaned_query:
        return []

    results = []
    for record in records:
        text_corpus = f"{record.topic} {record.key_rule} {record.document_title}".lower()
        if cleaned_query in text_corpus:
            results.append(record)
    return results


def count_by(records: List[Record], field: str = "issuing_body") -> Dict[str, int]:
    """
    Count records grouped by a specified attribute name.
    
    Args:
        records: List of Record dataclass objects.
        field: Name of the Record attribute to group by.
        
    Returns:
        Dictionary mapping field values to record counts.
    """
    counts: Dict[str, int] = {}
    for record in records:
        val = getattr(record, field, "Unknown")
        counts[str(val)] = counts.get(str(val), 0) + 1
    return counts


def get_by_id(records: List[Record], record_id: int) -> Optional[Record]:
    """
    Retrieve a single record matching the given numerical ID.
    
    Args:
        records: List of Record dataclass objects.
        record_id: Numerical identifier to find.
        
    Returns:
        The matching Record object if found, otherwise None.
    """
    for record in records:
        if record.id == record_id:
            return record
    return None
