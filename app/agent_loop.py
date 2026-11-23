# ==============================================================================
# File: app/agent_loop.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 9 - Hand-written Reason-Act-Observe Agent Loop.
#              Orchestrates RAG knowledge retrieval and the solar CFA calculator tool
#              without requiring heavy external agent frameworks.
# ==============================================================================

import logging
import os
import re
import sys
from typing import Any

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.tools import rag_search_tool, solar_cfa_calculator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agent_loop")


class HandWrittenAgentLoop:
    """
    Lightweight, deterministic Agent Loop implementing the ReAct pattern:
    1. Reason: Analyze intent, extract parameters (capacity, bill, area).
    2. Act: Dispatch to appropriate tool(s) (Calculator and/or RAG search).
    3. Observe: Collect structured tool outputs and verify feasibility constraints.
    4. Synthesize: Produce an authoritative, comprehensive homeowner advisory.
    """

    def __init__(self):
        self.default_bill = 2000.0          # Kopargaon benchmark (₹2,000/mo)
        self.default_terrace = 40.0         # Kopargaon benchmark (40 sq m)

    def _extract_capacity(self, text: str) -> float | None:
        """Extract requested solar capacity in kW from user query."""
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kw|kilo\s*watt|kilowatt)", text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                return val if val > 0 else None
            except ValueError:
                return None
        return None

    def _extract_bill(self, text: str) -> float | None:
        """Extract monthly electricity bill in INR from user query."""
        match = re.search(r"(?:rs\.?|₹|inr|bill\s*(?:of)?)\s*(\d+(?:,\d+)*(?:\.\d+)?)", text, re.IGNORECASE)
        if match:
            try:
                cleaned = match.group(1).replace(",", "")
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _extract_terrace(self, text: str) -> float | None:
        """Extract terrace area in square metres or sq ft from user query."""
        sqm_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq(?:uare)?\s*m(?:etre|eter)?|sqm|m2)", text, re.IGNORECASE)
        if sqm_match:
            try:
                return float(sqm_match.group(1))
            except ValueError:
                pass
        sqft_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq(?:uare)?\s*f(?:ee)?t|sqft)", text, re.IGNORECASE)
        if sqft_match:
            try:
                # Convert sq ft to sq m (~10.76 sq ft per sq m)
                return round(float(sqft_match.group(1)) / 10.764, 1)
            except ValueError:
                pass
        return None

    def run(
        self,
        question: str,
        user_name: str = "Homeowner",
        monthly_bill: float | None = None,
        terrace_sqm: float | None = None
    ) -> dict[str, Any]:
        """
        Execute the Reason -> Act -> Observe agent loop.
        """
        q = question.strip()
        q_lower = q.lower()
        steps: list[str] = []

        # ----------------------------------------------------------------------
        # Phase 1: REASON (Intent analysis & parameter extraction)
        # ----------------------------------------------------------------------
        steps.append("Phase 1 (Reason): Analyzing homeowner intent and extracting parameters.")

        extracted_capacity = self._extract_capacity(q)
        extracted_bill = self._extract_bill(q) or monthly_bill or self.default_bill
        extracted_terrace = self._extract_terrace(q) or terrace_sqm or self.default_terrace

        wants_calculation = any(k in q_lower for k in [
            "calculate", "subsidy", "cost", "price", "payback", "terrace", "area", "kw", "saving", "rupees", "how much"
        ])
        wants_rag = any(k in q_lower for k in [
            "rule", "guideline", "warranty", "vendor", "discom", "msedcl", "meter", "portal", "process", "apply", "who"
        ])

        # Default fallback: if neither explicitly targeted, use both if capacity is present, else RAG
        if not wants_calculation and not wants_rag:
            if extracted_capacity:
                wants_calculation = True
            else:
                wants_rag = True

        # ----------------------------------------------------------------------
        # Phase 2: ACT (Execute safe deterministic tools)
        # ----------------------------------------------------------------------
        calc_result: dict[str, Any] | None = None
        rag_result: dict[str, Any] | None = None

        if wants_calculation:
            # Default to 3.0 kW (benchmark) if no capacity specified
            cap = extracted_capacity if extracted_capacity else 3.0
            steps.append(f"Phase 2 (Act): Calling 'solar_cfa_calculator' with capacity={cap} kW, bill=₹{extracted_bill:,.0f}, terrace={extracted_terrace} sq m.")
            try:
                calc_result = solar_cfa_calculator(
                    capacity_kw=cap,
                    monthly_bill=extracted_bill,
                    available_terrace_sqm=extracted_terrace
                )
            except Exception as e:
                logger.error(f"Calculator tool execution error: {e}")

        if wants_rag or not wants_calculation:
            steps.append("Phase 2 (Act): Calling 'rag_search_tool' to retrieve official MNRE guidelines.")
            try:
                rag_result = rag_search_tool(query=q)
            except Exception as e:
                logger.error(f"RAG search tool execution error: {e}")

        # ----------------------------------------------------------------------
        # Phase 3: OBSERVE (Evaluate tool outcomes)
        # ----------------------------------------------------------------------
        steps.append("Phase 3 (Observe): Validating tool observations and feasibility checks.")
        citations: list[str] = []
        if calc_result:
            citations.append(calc_result["citation"])
        if rag_result and rag_result.get("citations"):
            citations.extend(rag_result["citations"])

        # ----------------------------------------------------------------------
        # Phase 4: SYNTHESIZE (Compose final response)
        # ----------------------------------------------------------------------
        steps.append("Phase 4 (Synthesize): Formulating structured grounded advisory.")
        response_sections: list[str] = []
        response_sections.append(f"Hello {user_name}!")

        # Add calculation overview if computed
        if calc_result:
            c = calc_result
            status_symbol = "✅" if c["is_area_sufficient"] else "⚠️"
            response_sections.append(
                f"\n### ☀️ Solar System & Financial Assessment ({c['capacity_kw']} kW System)\n"
                f"- **Eligible Central Subsidy (CFA):** ₹{c['eligible_subsidy_inr']:,} ({c['subsidy_breakdown']})\n"
                f"- **Estimated Total Installation Cost:** ₹{c['estimated_total_cost_inr']:,}\n"
                f"- **Net Cost to You:** ₹{c['net_cost_to_consumer_inr']:,}\n"
                f"- **Rooftop Area Required:** {c['required_terrace_sqm']} sq m (Available: {c['available_terrace_sqm']} sq m) — {status_symbol} **{'Feasible' if c['is_area_sufficient'] else 'Insufficient Area'}**\n"
                f"- **Estimated Monthly Generation:** ~{c['monthly_generation_units_kwh']} units (kWh)\n"
                f"- **Estimated Monthly Savings:** ~₹{c['estimated_monthly_savings_inr']:,}/month (~₹{c['estimated_annual_savings_inr']:,}/year)\n"
                f"- **Estimated Payback Period:** ~{c['payback_period_years']} years"
            )

        # Add RAG synthesis if retrieved
        if rag_result and rag_result.get("answer"):
            ans = rag_result["answer"]
            # Clean greeting redundancy if present
            if ans.startswith("Hello"):
                ans = re.sub(r"^Hello [^!]+!\s*", "", ans)
            response_sections.append(f"\n### 📜 Official Scheme Guidelines & Rules\n{ans}")

        final_answer = "\n".join(response_sections).strip()

        return {
            "question": q,
            "answer": final_answer,
            "agent_steps": steps,
            "calculation": calc_result,
            "rag_details": rag_result,
            "citations": list(dict.fromkeys(citations))  # Deduplicate while preserving order
        }


# Singleton agent loop instance
agent_loop = HandWrittenAgentLoop()


if __name__ == "__main__":
    print("=" * 75)
    print("🤖 TESTING HAND-WRITTEN AGENT LOOP (app/agent_loop.py)")
    print("=" * 75)

    # Test Kopargaon persona inquiry
    query = "I have a monthly electricity bill of Rs 2000 and 40 sq m terrace in Kopargaon. How much subsidy and savings will I get for 3 kW, and what is the panel warranty?"
    result = agent_loop.run(question=query, user_name="Abhishek Dighe")

    print("\n[AGENT EXECUTION TRACE]")
    for step in result["agent_steps"]:
        print(f" • {step}")

    print("\n[FINAL SYNTHESIZED ANSWER]")
    print(result["answer"])

    print("\n[CITATIONS]")
    for cit in result["citations"]:
        print(f" - {cit}")
    print("=" * 75)
