# ==============================================================================
# File: app/graph.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 9 - LangGraph StateGraph agent for SuryaGharSathi.
#              Features stateful conversation memory across turns, tool nodes,
#              conditional routing, and a Human-in-the-Loop approval gate for >10 kW systems.
# ==============================================================================

import logging
import os
import re
import sys
from typing import Any, TypedDict

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.tools import rag_search_tool, solar_cfa_calculator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("graph_agent")


# ------------------------------------------------------------------------------
# LangGraph Agent State Definition
# ------------------------------------------------------------------------------
class SolarAgentState(TypedDict):
    """
    Central state container managed by LangGraph across graph execution nodes.
    """
    question: str
    user_name: str
    monthly_bill: float
    terrace_sqm: float
    capacity_kw: float | None
    intent: str
    requires_approval: bool
    approved: bool
    steps: list[str]
    calculation: dict[str, Any] | None
    rag_result: dict[str, Any] | None
    answer: str
    citations: list[str]


# ------------------------------------------------------------------------------
# Graph Nodes
# ------------------------------------------------------------------------------
def analyze_intent_node(state: SolarAgentState) -> dict[str, Any]:
    """
    Node 1: Evaluates homeowner inquiry, extracts parameters, and identifies
    commercial-scale capacity (>10 kW) requiring human approval.
    """
    q = state.get("question", "")
    q_lower = q.lower()
    steps = list(state.get("steps", []))
    steps.append("[Node 1: analyze_intent] Parsing user inquiry and extracting solar parameters.")

    # Extract capacity
    capacity = state.get("capacity_kw")
    cap_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kw|kilo\s*watt|kilowatt)", q, re.IGNORECASE)
    if cap_match:
        try:
            capacity = float(cap_match.group(1))
        except ValueError:
            pass

    # Extract electricity bill if specified
    bill = state.get("monthly_bill") or 2000.0
    bill_match = re.search(r"(?:rs\.?|₹|inr|bill\s*(?:of)?)\s*(\d+(?:,\d+)*(?:\.\d+)?)", q, re.IGNORECASE)
    if bill_match:
        try:
            bill = float(bill_match.group(1).replace(",", ""))
        except ValueError:
            pass

    # Extract terrace area if specified
    terrace = state.get("terrace_sqm") or 40.0
    sqm_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq(?:uare)?\s*m(?:etre|eter)?|sqm|m2)", q, re.IGNORECASE)
    if sqm_match:
        try:
            terrace = float(sqm_match.group(1))
        except ValueError:
            pass

    # Human-in-the-loop safety check:
    # Systems > 10 kW exceed standard residential single-phase connection limits and subsidy slabs.
    requires_approval = False
    if capacity and capacity > 10.0 and not state.get("approved", False):
        requires_approval = True
        steps.append(f"[Safety Gate] System capacity ({capacity} kW) > 10 kW threshold. Pausing for homeowner approval.")

    # Determine tool intent
    wants_calc = any(k in q_lower for k in ["calculate", "subsidy", "cost", "price", "payback", "terrace", "area", "kw", "saving", "how much"])
    wants_rag = any(k in q_lower for k in ["rule", "guideline", "warranty", "vendor", "discom", "msedcl", "meter", "portal", "process", "apply"])

    if wants_calc and wants_rag:
        intent = "both"
    elif wants_calc:
        intent = "calculator"
    elif wants_rag:
        intent = "rag"
    else:
        intent = "both" if capacity else "rag"

    return {
        "capacity_kw": capacity,
        "monthly_bill": bill,
        "terrace_sqm": terrace,
        "intent": intent,
        "requires_approval": requires_approval,
        "steps": steps
    }


def approval_gate_node(state: SolarAgentState) -> dict[str, Any]:
    """
    Node 2 (Approval Notice): Explains policy limits for >10 kW systems and requests confirmation.
    """
    cap = state.get("capacity_kw", 10.0)
    steps = list(state.get("steps", []))
    steps.append("[Node 2: approval_gate] Human approval required before processing commercial-scale advisory.")

    notice = (
        f"⚠️ **Commercial-Scale Capacity Alert ({cap} kW)**\n\n"
        f"Under official PM Surya Ghar: Muft Bijli Yojana rules, Central Financial Assistance (CFA) "
        f"is strictly capped at 3 kW (maximum ₹78,000 subsidy). Systems exceeding 10 kW require "
        f"three-phase line sanctions, technical feasibility approval from MSEDCL, and commercial net-metering contracts.\n\n"
        f"Would you like SuryaGharSathi to proceed with estimating this commercial installation? "
        f"*(Please reply or confirm with `approved=True` to continue)*."
    )
    return {
        "answer": notice,
        "steps": steps,
        "citations": ["PM Surya Ghar Operational Guidelines (June 2024) - Clause 4.2 (Capacity Slabs)"]
    }


def execute_tools_node(state: SolarAgentState) -> dict[str, Any]:
    """
    Node 3: Executes deterministic calculation and/or grounded RAG search.
    """
    steps = list(state.get("steps", []))
    intent = state.get("intent", "both")
    cap = state.get("capacity_kw") or 3.0
    bill = state.get("monthly_bill", 2000.0)
    terrace = state.get("terrace_sqm", 40.0)
    q = state.get("question", "")

    calc_res = None
    rag_res = None

    if intent in ("calculator", "both"):
        steps.append(f"[Node 3: execute_tools] Executing 'solar_cfa_calculator' (capacity={cap} kW, bill=₹{bill:,.0f}, terrace={terrace} sq m).")
        try:
            calc_res = solar_cfa_calculator(
                capacity_kw=cap,
                monthly_bill=bill,
                available_terrace_sqm=terrace
            )
        except Exception as e:
            logger.error(f"Error in solar_cfa_calculator: {e}")

    if intent in ("rag", "both"):
        steps.append("[Node 3: execute_tools] Executing 'rag_search_tool' via ChromaDB.")
        try:
            rag_res = rag_search_tool(query=q)
        except Exception as e:
            logger.error(f"Error in rag_search_tool: {e}")

    return {
        "calculation": calc_res,
        "rag_result": rag_res,
        "steps": steps
    }


def synthesize_response_node(state: SolarAgentState) -> dict[str, Any]:
    """
    Node 4: Synthesizes final comprehensive homeowner response with citations.
    """
    steps = list(state.get("steps", []))
    steps.append("[Node 4: synthesize_response] Assembling grounded homeowner advisory.")

    user_name = state.get("user_name", "Homeowner")
    calc = state.get("calculation")
    rag = state.get("rag_result")

    citations: list[str] = []
    lines: list[str] = [f"Hello {user_name}!"]

    if calc:
        citations.append(calc["citation"])
        status_badge = "✅ **Feasible (Adequate Area)**" if calc["is_area_sufficient"] else "⚠️ **Insufficient Terrace Area**"
        lines.append(
            f"\n### ☀️ Solar System Sizing & Economics ({calc['capacity_kw']} kW System)\n"
            f"- **Central Government Subsidy (CFA):** ₹{calc['eligible_subsidy_inr']:,} ({calc['subsidy_breakdown']})\n"
            f"- **Estimated Benchmark Gross Cost:** ₹{calc['estimated_total_cost_inr']:,}\n"
            f"- **Net Cost Payable by Homeowner:** ₹{calc['net_cost_to_consumer_inr']:,}\n"
            f"- **Rooftop Shadow-Free Area:** {calc['required_terrace_sqm']} sq m needed vs {calc['available_terrace_sqm']} sq m available — {status_badge}\n"
            f"- **Monthly Generation:** ~{calc['monthly_generation_units_kwh']} units (kWh)\n"
            f"- **Estimated Monthly Savings:** ~₹{calc['estimated_monthly_savings_inr']:,}/month (~₹{calc['estimated_annual_savings_inr']:,}/year)\n"
            f"- **Estimated Payback Period:** ~{calc['payback_period_years']} years"
        )

    if rag and rag.get("answer"):
        if rag.get("citations"):
            citations.extend(rag["citations"])
        ans_text = rag["answer"]
        if ans_text.startswith("Hello"):
            ans_text = re.sub(r"^Hello [^!]+!\s*", "", ans_text)
        lines.append(f"\n### 📜 Official Scheme Guidelines & Technical Specifications\n{ans_text}")

    deduped_citations = list(dict.fromkeys(citations))
    return {
        "answer": "\n".join(lines).strip(),
        "citations": deduped_citations,
        "steps": steps
    }


# ------------------------------------------------------------------------------
# Build and Compile LangGraph StateGraph
# ------------------------------------------------------------------------------
def route_after_intent(state: SolarAgentState) -> str:
    """Conditional edge router."""
    if state.get("requires_approval", False) and not state.get("approved", False):
        return "approval_gate_node"
    return "execute_tools_node"


def build_solar_agent_graph():
    """Constructs the compiled LangGraph workflow with in-memory checkpointer."""
    workflow = StateGraph(SolarAgentState)

    # Add Nodes
    workflow.add_node("analyze_intent_node", analyze_intent_node)
    workflow.add_node("approval_gate_node", approval_gate_node)
    workflow.add_node("execute_tools_node", execute_tools_node)
    workflow.add_node("synthesize_response_node", synthesize_response_node)

    # Add Edges
    workflow.add_edge(START, "analyze_intent_node")
    workflow.add_conditional_edges(
        "analyze_intent_node",
        route_after_intent,
        {
            "approval_gate_node": "approval_gate_node",
            "execute_tools_node": "execute_tools_node"
        }
    )
    workflow.add_edge("approval_gate_node", END)
    workflow.add_edge("execute_tools_node", "synthesize_response_node")
    workflow.add_edge("synthesize_response_node", END)

    # In-memory checkpointer for cross-turn session memory
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


# Compiled application graph instance
solar_agent_graph = build_solar_agent_graph()


class LangGraphAgentRunner:
    """Convenient runtime facade for invoking the compiled LangGraph agent."""

    def __init__(self, graph=solar_agent_graph):
        self.graph = graph

    def run(
        self,
        question: str,
        user_name: str = "Homeowner",
        monthly_bill: float = 2000.0,
        terrace_sqm: float = 40.0,
        approved: bool = False,
        thread_id: str = "default_session"
    ) -> dict[str, Any]:
        """Execute a graph invocation turn with session memory."""
        initial_state: SolarAgentState = {
            "question": question,
            "user_name": user_name,
            "monthly_bill": monthly_bill,
            "terrace_sqm": terrace_sqm,
            "capacity_kw": None,
            "intent": "both",
            "requires_approval": False,
            "approved": approved,
            "steps": [],
            "calculation": None,
            "rag_result": None,
            "answer": "",
            "citations": []
        }

        config = {"configurable": {"thread_id": thread_id}}
        final_state = self.graph.invoke(initial_state, config=config)

        return {
            "question": question,
            "answer": final_state.get("answer", ""),
            "steps": final_state.get("steps", []),
            "calculation": final_state.get("calculation"),
            "citations": final_state.get("citations", []),
            "requires_approval": final_state.get("requires_approval", False),
            "approved": final_state.get("approved", False),
            "thread_id": thread_id
        }


# Global agent runner instance
langgraph_agent = LangGraphAgentRunner()


if __name__ == "__main__":
    print("=" * 75)
    print("🕸️ TESTING LANGGRAPH SOLAR AGENT (app/graph.py)")
    print("=" * 75)

    # Scenario 1: Standard Kopargaon Homeowner (3 kW, 40 sq m roof, ₹2,000 bill)
    print("\n--- TEST SCENARIO 1: Standard 3 kW Residential Inquiry ---")
    s1_res = langgraph_agent.run(
        question="Can I install a 3 kW solar plant on my 40 sq m roof in Kopargaon with Rs 2000 bill?",
        user_name="Abhishek Dighe",
        thread_id="test_user_01"
    )
    print("Approval Needed:", s1_res["requires_approval"])
    print("Steps Taken:")
    for s in s1_res["steps"]:
        print(f"  • {s}")
    print("\nAnswer Snippet:")
    print(s1_res["answer"][:300], "...")

    # Scenario 2: Large Commercial Request (15 kW) triggering Human-in-the-loop gate
    print("\n--- TEST SCENARIO 2: Commercial 15 kW System (Trigger Approval) ---")
    s2_res = langgraph_agent.run(
        question="I want to install a 15 kW solar system on my commercial building.",
        user_name="Abhishek Dighe",
        approved=False,
        thread_id="test_user_02"
    )
    print("Approval Needed:", s2_res["requires_approval"])
    print("Answer:")
    print(s2_res["answer"])

    # Scenario 3: Approved commercial request
    print("\n--- TEST SCENARIO 3: Approved 15 kW System ---")
    s3_res = langgraph_agent.run(
        question="I want to install a 15 kW solar system on my commercial building.",
        user_name="Abhishek Dighe",
        approved=True,
        thread_id="test_user_02"
    )
    print("Approval Needed:", s3_res["requires_approval"])
    print("Approved:", s3_res["approved"])
    print("Calculation Subsidy:", s3_res["calculation"]["eligible_subsidy_inr"] if s3_res["calculation"] else "None")
    print("=" * 75)
