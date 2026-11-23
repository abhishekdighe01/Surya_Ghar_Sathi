from app.smart_search import smart_search_engine
from app.vectorstore import vector_store


def test_tfidf_search_basic():
    matches = smart_search_engine.search("subsidy for solar installation", top_k=3)
    assert len(matches) > 0
    top_record, score = matches[0]
    assert score > 0.0
    assert hasattr(top_record, "key_rule")


def test_tfidf_search_empty():
    matches = smart_search_engine.search("", top_k=3)
    assert isinstance(matches, list)


def test_vectorstore_query():
    hits = vector_store.query("What is the required rooftop area?", n_results=2)
    assert len(hits) == 2
    for hit in hits:
        assert "chunk_id" in hit
        assert "text" in hit
        assert "similarity_score" in hit
        assert "metadata" in hit
        assert "document_title" in hit["metadata"]
