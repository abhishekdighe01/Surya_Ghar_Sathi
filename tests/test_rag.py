from app.rag import rag_pipeline


def test_rag_answerable_question():
    res = rag_pipeline.answer_question("What is the central subsidy for 3 kW solar system?")
    assert "answer" in res
    assert len(res["answer"]) > 20
    assert len(res["citations"]) > 0
    assert res["confidence"] in ("high", "medium")


def test_rag_unanswerable_q6_refusal():
    res = rag_pipeline.answer_question("What will MSEDCL's electricity tariff per unit be next year?")
    assert "cannot confirm this from the available official documents" in res["answer"].lower()
    assert res["confidence"] == "low"
    assert len(res["citations"]) == 0
