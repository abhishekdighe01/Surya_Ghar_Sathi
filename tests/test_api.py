import pytest
from fastapi import HTTPException

from app.main import (
    AgentRequest,
    AskRequest,
    QuestionCreate,
    ask_solar_assistant,
    get_health,
    get_record,
    list_records,
    run_solar_agent,
    search_records,
    submit_question,
)


def test_api_health():
    res = get_health()
    assert res.status == "ok"
    assert res.app == "SuryaGharSathi"
    assert res.records_count == 20


def test_api_list_records():
    records = list_records(limit=5)
    assert len(records) == 5
    assert records[0]["id"] == 1


def test_api_get_record_valid():
    record = get_record(1)
    assert record["id"] == 1
    assert "MNRE" in record["issuing_body"] or "Ministry" in record["issuing_body"]



def test_api_get_record_not_found():
    with pytest.raises(HTTPException) as exc_info:
        get_record(999)
    assert exc_info.value.status_code == 404


def test_api_search():
    matches = search_records(q="subsidy structure", limit=2)
    assert isinstance(matches, list)
    assert len(matches) <= 2
    if matches:
        assert "similarity_score" in matches[0]


def test_api_questions_post():
    payload = QuestionCreate(question="Can I install 3 kW solar?", user_name="Test Homeowner")
    res = submit_question(payload)
    assert res.question == "Can I install 3 kW solar?"
    assert res.user_name == "Test Homeowner"


def test_api_ask_rag_answerable():
    payload = AskRequest(question="What is the subsidy for a 3 kW solar system?", user_name="Abhishek Dighe")
    res = ask_solar_assistant(payload)
    assert len(res.answer) > 20
    assert len(res.citations) > 0


def test_api_ask_rag_unanswerable():
    payload = AskRequest(question="What will MSEDCL's electricity tariff per unit be next year?", user_name="Abhishek Dighe")
    res = ask_solar_assistant(payload)
    assert "cannot confirm this" in res.answer.lower()
    assert len(res.citations) == 0


def test_api_agent_residential():
    payload = AgentRequest(
        question="Can I install a 3 kW solar plant on my 40 sq m roof in Kopargaon?",
        user_name="Abhishek Dighe",
        monthly_bill=2000.0,
        terrace_sqm=40.0
    )
    res = run_solar_agent(payload)
    assert res.requires_approval is False
    assert res.calculation is not None
    assert res.calculation["eligible_subsidy_inr"] == 78000.0
