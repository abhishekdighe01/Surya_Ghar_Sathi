# ==============================================================================
# File: app/main.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 4 - Production-grade FastAPI backend service exposing REST endpoints
#              for health checks, record retrieval, TF-IDF smart search, and user question logging.
# ==============================================================================

import json
import os
import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph import langgraph_agent
from app.llm import llm_engine
from app.rag import rag_pipeline
from app.records import get_by_id, load_records
from app.smart_search import smart_search_engine
from app.vectorstore import vector_store

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "questions.json")

# ------------------------------------------------------------------------------
# FastAPI Application Configuration
# ------------------------------------------------------------------------------
app = FastAPI(
    title="SuryaGharSathi API (सूर्याघर साथी)",
    description=(
        "Production REST API for PM Surya Ghar Muft Bijli Yojana advisory services. "
        "Provides official scheme rules, TF-IDF smart search, and user query logging."
    ),
    version="1.0.0",
    contact={
        "name": "Abhishek Dighe (SJ-64)",
        "email": "abhishekdighe54@gmail.com",
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable Cross-Origin Resource Sharing (CORS) for UI integration (Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# Pydantic Schemas for Requests and Responses
# ------------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    app: str = Field(..., json_schema_extra={"example": "SuryaGharSathi"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    records_count: int = Field(..., json_schema_extra={"example": 20})
    server_time: str = Field(..., json_schema_extra={"example": "2026-11-23T21:30:00"})


class RecordResponse(BaseModel):
    id: int
    document_title: str
    issuing_body: str
    date_issued: str
    topic: str
    key_rule: str
    source_url: str


class SearchRecordResponse(RecordResponse):
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")


class QuestionCreate(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, json_schema_extra={"example": "How much subsidy do I get for a 3 kW solar plant?"})
    user_name: str | None = Field(default="Anonymous Homeowner", json_schema_extra={"example": "Abhishek Dighe"})


class QuestionResponse(BaseModel):
    id: int
    user_name: str
    question: str
    saved_at: str
    message: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, json_schema_extra={"example": "How much central subsidy will I get for a 3 kW solar system?"})
    user_name: str | None = Field(default="Homeowner", json_schema_extra={"example": "Abhishek Dighe"})


class ChatResponse(BaseModel):
    answer: str
    confidence: str
    follow_up: str
    citations: list[str]


class SemanticChunkResponse(BaseModel):
    chunk_id: str
    text: str
    metadata: dict
    similarity_score: float


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, json_schema_extra={"example": "How much central subsidy will I get for a 3 kW solar system?"})
    user_name: str | None = Field(default="Homeowner", json_schema_extra={"example": "Abhishek Dighe"})
    top_k: int | None = Field(default=3, ge=1, le=10)


class AskResponse(BaseModel):
    question: str
    answer: str
    confidence: str
    retrieval_score: float
    follow_up: str
    citations: list[str]
    sources: list[dict]


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, json_schema_extra={"example": "Can I install a 3 kW solar plant on my 40 sq m roof in Kopargaon?"})
    user_name: str | None = Field(default="Homeowner", json_schema_extra={"example": "Abhishek Dighe"})
    monthly_bill: float | None = Field(default=2000.0, json_schema_extra={"example": 2000.0})
    terrace_sqm: float | None = Field(default=40.0, json_schema_extra={"example": 40.0})
    approved: bool | None = Field(default=False, description="Approval flag for systems > 10 kW")
    thread_id: str | None = Field(default="default_session", description="Conversation thread identifier for memory")



class AgentResponse(BaseModel):
    question: str
    answer: str
    steps: list[str]
    calculation: dict | None = None
    citations: list[str]
    requires_approval: bool
    approved: bool
    thread_id: str



# ------------------------------------------------------------------------------
# REST API Endpoints
# ------------------------------------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Service Health Check"
)
def get_health():
    """Verify that the FastAPI service is healthy and records are loaded into memory."""
    records = load_records()
    return HealthResponse(
        status="ok",
        app="SuryaGharSathi",
        version="1.0.0",
        records_count=len(records),
        server_time=datetime.now().isoformat()
    )


@app.get(
    "/records",
    response_model=list[RecordResponse],
    tags=["Scheme Records"],
    summary="List Official Scheme Records"
)
def list_records(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return")
):
    """Retrieve all official PM Surya Ghar scheme records up to the specified limit."""
    records = load_records()
    return [r.to_dict() for r in records[:limit]]


@app.get(
    "/records/{id}",
    response_model=RecordResponse,
    tags=["Scheme Records"],
    summary="Get Scheme Record by ID"
)
def get_record(id: int):
    """Retrieve a single official scheme record by its unique ID (1 to 20)."""
    records = load_records()
    record = get_by_id(records, id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with ID {id} does not exist in the official dataset."
        )
    return record.to_dict()


@app.get(
    "/search",
    response_model=list[SearchRecordResponse],
    tags=["Smart Search"],
    summary="Smart Search with TF-IDF and Cosine Similarity"
)
def search_records(
    q: str = Query(..., min_length=2, description="Search query or question"),
    limit: int = Query(default=3, ge=1, le=10, description="Number of ranked results")
):
    """
    Rank and return the most relevant scheme records using TF-IDF feature extraction
    and Cosine Similarity scoring.
    """
    matches = smart_search_engine.search(query=q, top_k=limit)
    response_list = []
    for record, score in matches:
        rec_dict = record.to_dict()
        rec_dict["similarity_score"] = score
        response_list.append(rec_dict)
    return response_list


@app.get(
    "/search/semantic",
    response_model=list[SemanticChunkResponse],
    tags=["Semantic Search"],
    summary="Semantic Vector Search using ChromaDB"
)
def search_semantic(
    q: str = Query(..., min_length=2, description="Semantic search query or question"),
    limit: int = Query(default=3, ge=1, le=10, description="Number of nearest chunks")
):
    """
    Search and retrieve official scheme document chunks using ChromaDB vector database
    and dense embedding similarity.
    """
    hits = vector_store.query(query_text=q, n_results=limit)
    return hits


@app.post(
    "/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User Interactions"],
    summary="Submit and Log User Question"
)
def submit_question(payload: QuestionCreate):
    """Accept and log a homeowner's solar question to data/questions.json."""
    os.makedirs(os.path.dirname(QUESTIONS_FILE), exist_ok=True)

    # Read existing questions if file exists
    existing_questions = []
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, encoding="utf-8") as f:
                existing_questions = json.load(f)
        except Exception:
            existing_questions = []

    new_id = len(existing_questions) + 1
    timestamp = datetime.now().isoformat()
    record_entry = {
        "id": new_id,
        "user_name": payload.user_name.strip() or "Anonymous Homeowner",
        "question": payload.question.strip(),
        "saved_at": timestamp
    }

    existing_questions.append(record_entry)

    # Save to questions.json
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_questions, f, indent=2, ensure_ascii=False)

    return QuestionResponse(
        id=new_id,
        user_name=record_entry["user_name"],
        question=record_entry["question"],
        saved_at=timestamp,
        message="Your question has been securely recorded for SuryaGharSathi AI analysis."
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["AI Assistant"],
    summary="Chat with SuryaGharSathi AI"
)
def chat_with_assistant(payload: ChatRequest):
    """
    Accept homeowner questions, query the LLM provider with official MNRE grounding,
    and return structured JSON with citations and follow-up guidance.
    """
    try:
        response_data = llm_engine.generate(
            question=payload.question,
            user_name=payload.user_name or "Homeowner"
        )
        return ChatResponse(
            answer=response_data.get("answer", "Unable to generate response."),
            confidence=response_data.get("confidence", "medium"),
            follow_up=response_data.get("follow_up", "Would you like to know more?"),
            citations=response_data.get("citations", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {e!s}"
        )


@app.post(
    "/ask",
    response_model=AskResponse,
    tags=["RAG"],
    summary="Grounded RAG Solar Advisory"
)
def ask_solar_assistant(payload: AskRequest):
    """
    Day 8 - Grounded RAG query endpoint.
    Retrieves dense semantic chunks from ChromaDB and synthesizes an authoritative,
    hallucination-free answer with exact citations and confidence ratings.
    """
    try:
        result = rag_pipeline.answer_question(
            question=payload.question,
            user_name=payload.user_name or "Homeowner",
            top_k=payload.top_k or 3
        )
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG processing failed: {e!s}"
        )


@app.post(
    "/agent",
    response_model=AgentResponse,
    tags=["AI Agent"],
    summary="LangGraph Multi-Step Solar Advisory Agent"
)
def run_solar_agent(payload: AgentRequest):
    """
    Day 9 - LangGraph Solar Agent with memory, tool routing, and human-in-the-loop approval.
    """
    try:
        result = langgraph_agent.run(
            question=payload.question,
            user_name=payload.user_name or "Homeowner",
            monthly_bill=payload.monthly_bill or 2000.0,
            terrace_sqm=payload.terrace_sqm or 40.0,
            approved=payload.approved or False,
            thread_id=payload.thread_id or "default_session"
        )
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow failed: {e!s}"
        )


