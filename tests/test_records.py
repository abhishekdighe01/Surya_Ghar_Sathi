from app.models import Record
from app.records import count_by, get_by_id, load_records


def test_load_records_count():
    records = load_records()
    assert len(records) == 20
    assert all(isinstance(r, Record) for r in records)


def test_record_model_attributes():
    records = load_records()
    first = records[0]
    assert first.id == 1
    assert "MNRE" in first.issuing_body or "Ministry" in first.issuing_body
    assert len(first.key_rule) > 10
    assert first.source_url.startswith("http")


def test_get_by_id_valid():
    records = load_records()
    record = get_by_id(records, 1)
    assert record is not None
    assert record.id == 1


def test_get_by_id_invalid():
    records = load_records()
    record = get_by_id(records, 999)
    assert record is None


def test_count_by_issuing_body():
    records = load_records()
    counts = count_by(records, "issuing_body")
    assert isinstance(counts, dict)
    assert len(counts) >= 2
    assert sum(counts.values()) == 20

