# ==============================================================================
# File: app/ingest.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 3 - Data ingestion and cleaning pipeline that validates raw
#              documents, uses pandas for quality checks, and outputs data/records.json.
# ==============================================================================

import os
import sys
import json
import logging
from typing import List, Dict, Any
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Record
from data.sample_records import SAMPLE_RECORDS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ingest")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
OUTPUT_JSON = os.path.join(DATA_DIR, "records.json")

REQUIRED_FIELDS = [
    "id",
    "document_title",
    "issuing_body",
    "date_issued",
    "topic",
    "key_rule",
    "source_url"
]


def clean_text(text: Any) -> str:
    """Normalize text: strip leading/trailing whitespace and collapse internal spaces."""
    if not isinstance(text, str):
        return ""
    return " ".join(text.strip().split())


def process_records(raw_records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Clean, validate, and convert raw record dictionaries into a pandas DataFrame.
    Uses try/except blocks to gracefully handle and skip corrupt entries.
    """
    valid_rows: List[Dict[str, Any]] = []

    for idx, item in enumerate(raw_records, start=1):
        try:
            # Validate required fields presence
            missing = [f for f in REQUIRED_FIELDS if f not in item]
            if missing:
                raise ValueError(f"Record index {idx} missing required fields: {missing}")

            cleaned_row = {
                "id": int(item["id"]),
                "document_title": clean_text(item["document_title"]),
                "issuing_body": clean_text(item["issuing_body"]),
                "date_issued": clean_text(item["date_issued"]),
                "topic": clean_text(item["topic"]),
                "key_rule": clean_text(item["key_rule"]),
                "source_url": clean_text(item["source_url"]),
            }

            # Enforce non-empty content
            for key, val in cleaned_row.items():
                if key != "id" and not val:
                    raise ValueError(f"Record ID {cleaned_row['id']} has empty field: {key}")

            valid_rows.append(cleaned_row)

        except Exception as e:
            logger.error(f"❌ Error processing record row {idx}: {e}. Skipping row.")

    df = pd.DataFrame(valid_rows)
    return df


def inspect_with_pandas(df: pd.DataFrame) -> None:
    """Run pandas inspection routines and print summary statistics."""
    logger.info("--- PANDAS DATA QUALITY INSPECTION ---")
    logger.info(f"Total Cleaned Records: {len(df)}")
    logger.info(f"DataFrame Shape: {df.shape}")
    logger.info(f"Missing Values Check:\n{df.isnull().sum().to_dict()}")

    logger.info("\nRecords Breakdown by Issuing Body:")
    for issuer, count in df["issuing_body"].value_counts().items():
        logger.info(f" • {issuer}: {count} records")

    logger.info("\nRecords Breakdown by Issue Date:")
    for date_val, count in df["date_issued"].value_counts().items():
        logger.info(f" • {date_val}: {count} records")


def run_pipeline(output_path: str = OUTPUT_JSON) -> int:
    """
    Execute end-to-end data ingestion pipeline:
    1. Read verified scheme records
    2. Process and validate with pandas
    3. Verify Record dataclass conversion
    4. Save to data/records.json
    """
    logger.info(f"Reading raw scheme records ({len(SAMPLE_RECORDS)} input items)...")
    
    # Process into pandas DataFrame
    df = process_records(SAMPLE_RECORDS)
    
    # Run inspections
    inspect_with_pandas(df)

    # Convert DataFrame rows into strongly-typed Record dataclasses
    records_list: List[Record] = [
        Record.from_dict(row.to_dict()) for _, row in df.iterrows()
    ]
    logger.info(f"Successfully converted {len(records_list)} rows to Record dataclass objects.")

    # Serialize to JSON
    records_dicts = [r.to_dict() for r in records_list]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records_dicts, f, indent=2, ensure_ascii=False)

    logger.info(f"💾 Ingestion complete! Saved {len(records_dicts)} verified records to {output_path}.")
    return len(records_dicts)


if __name__ == "__main__":
    run_pipeline()
