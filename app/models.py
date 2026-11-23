# ==============================================================================
# File: app/models.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 2 - Domain data models using Python dataclasses.
# ==============================================================================

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Record:
    """
    Represents an official rule or FAQ entry from PM Surya Ghar documents.

    Attributes:
        id: Unique numerical identifier for the record.
        document_title: Official name of the publication or regulatory document.
        issuing_body: Government ministry, department, or organization that issued the document.
        date_issued: Date of document publication (YYYY-MM-DD).
        topic: Specific subject, section title, or FAQ question.
        key_rule: Exact regulatory rule, policy guideline, or official answer text.
        source_url: Authoritative URL where the document or FAQ is hosted.
    """
    id: int
    document_title: str
    issuing_body: str
    date_issued: str
    topic: str
    key_rule: str
    source_url: str

    def to_dict(self) -> dict[str, Any]:
        """Convert the Record instance into a standard Python dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Record":
        """Instantiate a Record object from a dictionary."""
        return cls(
            id=int(data["id"]),
            document_title=str(data["document_title"]),
            issuing_body=str(data["issuing_body"]),
            date_issued=str(data["date_issued"]),
            topic=str(data["topic"]),
            key_rule=str(data["key_rule"]),
            source_url=str(data["source_url"]),
        )
