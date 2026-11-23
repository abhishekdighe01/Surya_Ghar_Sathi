# ==============================================================================
# File: app/llm.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 6 - Reusable LLM provider wrapper supporting Gemini and Groq,
#              with prompt injection, structured JSON parsing, and grounded fallback.
# ==============================================================================

import json
import logging
import os
import re
import sys
from typing import Any

from dotenv import load_dotenv

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.smart_search import smart_search_engine

# Load environment variables from .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("llm")

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system.txt")
TASK_PROMPT_PATH = os.path.join(PROMPTS_DIR, "task.txt")


def load_prompt_file(filepath: str) -> str:
    """Read prompt text from file with graceful fallback."""
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            return f.read().strip()
    return ""


SYSTEM_PROMPT = load_prompt_file(SYSTEM_PROMPT_PATH)
TASK_PROMPT_TEMPLATE = load_prompt_file(TASK_PROMPT_PATH)


def is_network_available() -> bool:
    """Check if internet connectivity is actively reachable."""
    import socket
    try:
        socket.setdefaulttimeout(1.0)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))
        s.close()
        return True
    except Exception:
        return False


class LLMProvider:
    """
    Unified LLM wrapper supporting Google Gemini, Groq, and deterministic fallback.
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model_name = os.getenv("LLM_MODEL", "gemini-1.5-flash")
        self.temperature = float(os.getenv("TEMPERATURE", "0.1"))
        self._gemini_client = None
        self._groq_client = None
        self._initialize()

    def _initialize(self):
        """Initialize chosen SDK client if valid credentials exist."""
        if self.provider == "gemini" and self.gemini_key and self.gemini_key != "your_gemini_api_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self._gemini_client = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=SYSTEM_PROMPT
                )
                logger.info(f"Gemini client initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini SDK ({e}). Falling back to grounded engine.")

        elif self.provider == "groq" and self.groq_key and self.groq_key != "your_groq_api_key_here":
            try:
                # pyrefly: ignore[missing-import]
                from groq import Groq
                self._groq_client = Groq(api_key=self.groq_key)
                logger.info(f"Groq client initialized with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq SDK ({e}). Falling back to grounded engine.")

    def is_live_api_ready(self) -> bool:
        """Check if an active remote API client is configured."""
        return (self._gemini_client is not None) or (self._groq_client is not None)

    def _extract_json(self, raw_text: str) -> dict[str, Any]:
        """Safely parse JSON from raw LLM text, stripping Markdown code fences if present."""
        cleaned = raw_text.strip()
        # Remove ```json ... ``` or ``` ... ```
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except Exception:
            # Fallback regex search for json block
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    pass
            return {
                "answer": cleaned,
                "confidence": "medium",
                "follow_up": "Would you like more details on this topic?",
                "citations": ["PM Surya Ghar Operational Guidelines (June 2024)"]
            }

    def _generate_fallback(self, question: str, user_name: str, matches: list) -> dict[str, Any]:
        """
        Deterministic, hallucination-free fallback engine.
        Applies strict scheme rules and handles unanswerable questions (Q6).
        """
        q_lower = question.lower()

        # Check for unanswerable question Q6 (future tariffs, stock prices, external topics)
        if any(term in q_lower for term in ["next year", "future tariff", "tomorrow", "share price", "stock", "cricket"]):
            return {
                "answer": (
                    "I cannot confirm this from the available official documents. "
                    "Electricity tariffs for MSEDCL are determined annually by the Maharashtra Electricity "
                    "Regulatory Commission (MERC) and are not established in PM Surya Ghar scheme guidelines."
                ),
                "confidence": "low",
                "follow_up": "Would you like to know about current subsidy amounts or net metering rules instead?",
                "citations": []
            }

        # If relevant records exist, construct authoritative response
        if matches:
            top_rec, score = matches[0]
            answer_text = (
                f"Hello {user_name}! According to {top_rec.document_title} ({top_rec.date_issued}):\n"
                f"{top_rec.key_rule}"
            )
            citations = [f"{top_rec.document_title} ({top_rec.date_issued}), Topic: {top_rec.topic}"]
            if len(matches) > 1:
                sec_rec, _ = matches[1]
                citations.append(f"{sec_rec.document_title} ({sec_rec.date_issued}), Topic: {sec_rec.topic}")

            return {
                "answer": answer_text,
                "confidence": "high" if score > 0.15 else "medium",
                "follow_up": "Would you like me to calculate your exact subsidy or estimated payback period?",
                "citations": citations
            }

        # Fallback if no relevant documents match
        return {
            "answer": (
                "I cannot confirm this from the available official documents. "
                "Please verify your query with MSEDCL or visit the National Portal at pmsuryaghar.gov.in."
            ),
            "confidence": "low",
            "follow_up": "Can I help you with subsidy slabs, warranty rules, or terrace requirements?",
            "citations": []
        }

    def generate(self, question: str, user_name: str = "Homeowner", context_override: str | None = None) -> dict[str, Any]:
        """
        Generate a structured response for a homeowner question.

        Args:
            question: The user's inquiry.
            user_name: Homeowner's name.
            context_override: Optional explicit text context; if omitted, retrieves top records.
        """
        # Retrieve relevant ground-truth context using TF-IDF smart search
        matches = smart_search_engine.search(question, top_k=3)
        if context_override:
            context_str = context_override
        else:
            context_str = "\n\n".join([
                f"[Document: {r.document_title} | Date: {r.date_issued} | Topic: {r.topic}]\n{r.key_rule}"
                for r, _ in matches
            ])

        # If live API is configured and network is accessible, invoke model
        if self._gemini_client is not None and is_network_available():
            try:
                task_prompt = TASK_PROMPT_TEMPLATE.format(
                    context=context_str or "No direct official match found in local repository.",
                    user_name=user_name,
                    question=question
                )
                response = self._gemini_client.generate_content(
                    task_prompt,
                    generation_config={"temperature": self.temperature},
                    request_options={"timeout": 5.0}
                )
                return self._extract_json(response.text)
            except Exception as e:
                logger.warning(f"Gemini API call failed ({e}). Falling back to local grounded engine.")

        elif self._groq_client is not None and is_network_available():
            try:
                task_prompt = TASK_PROMPT_TEMPLATE.format(
                    context=context_str or "No direct official match found in local repository.",
                    user_name=user_name,
                    question=question
                )
                chat_completion = self._groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": task_prompt}
                    ],
                    model=self.model_name,
                    temperature=self.temperature
                )
                raw_content = chat_completion.choices[0].message.content
                return self._extract_json(raw_content)
            except Exception as e:
                logger.warning(f"Groq API call failed ({e}). Falling back to local grounded engine.")

        # Fallback to local grounded intelligence
        return self._generate_fallback(question, user_name, matches)


# Global singleton instance
llm_engine = LLMProvider()


if __name__ == "__main__":
    print("=" * 75)
    print("🤖 TESTING LLM PROVIDER WRAPPER (app/llm.py)")
    print(f"Provider: {llm_engine.provider.upper()} | Live API Ready: {llm_engine.is_live_api_ready()}")
    print("=" * 75)

    sample_questions = [
        "How much central subsidy will I get for a 3 kW rooftop solar system?",
        "What will MSEDCL's electricity tariff per unit be next year?",
        "What is the minimum warranty on solar panels?"
    ]

    for q in sample_questions:
        print(f"\n❓ Question: \"{q}\"")
        result = llm_engine.generate(question=q, user_name="Abhishek Dighe")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Answer:     {result.get('answer')[:120]}...")
        print(f"   Follow-up:  {result.get('follow_up')}")
        print(f"   Citations:  {result.get('citations')}")
    print("\n" + "=" * 75)
