# ==============================================================================
# File: app/tools.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 9 - Deterministic tools for SuryaGharSathi AI Agent.
#              Includes official MNRE CFA Subsidy & Rooftop Feasibility Calculator
#              and Grounded RAG Knowledge Retrieval Tool.
# ==============================================================================

import os
import sys
from typing import Dict, Any, Optional

# Ensure project root is available for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag import rag_pipeline

# ------------------------------------------------------------------------------
# Official MNRE Scheme Constants (Operational Guidelines June 2024)
# ------------------------------------------------------------------------------
SUBSIDY_FIRST_2KW_PER_KW = 30000.0   # ₹30,000 per kW for first 2 kW
SUBSIDY_ADDITIONAL_PER_KW = 18000.0  # ₹18,000 per kW for 2 kW to 3 kW
MAX_SUBSIDY_CAP = 78000.0           # Capped at ₹78,000 for > 3 kW
SQM_PER_KW = 10.0                   # ~10 sq m shadow-free rooftop per kW
AVG_DAILY_UNITS_PER_KW = 4.0        # ~4 units (kWh) per kW per day
BENCHMARK_COST_PER_KW = 50000.0     # ~₹50,000 per kW residential benchmark
MSEDCL_AVG_TARIFF_PER_UNIT = 7.50   # ~₹7.50 / unit average residential tariff


def solar_cfa_calculator(
    capacity_kw: float,
    monthly_bill: float = 2000.0,
    available_terrace_sqm: float = 40.0
) -> Dict[str, Any]:
    """
    Deterministic solar subsidy, area feasibility, and payback calculator.
    
    Adheres strictly to MNRE PM Surya Ghar Operational Guidelines (June 2024):
    - First 2 kW: ₹30,000 per kW
    - 2 kW to 3 kW: ₹18,000 per kW
    - Above 3 kW: Fixed maximum cap of ₹78,000
    - Rooftop Area: ~10 sq m per kW
    
    Args:
        capacity_kw: Proposed solar plant capacity in kilowatts (kW).
        monthly_bill: Current monthly electricity bill in INR (₹).
        available_terrace_sqm: Usable shadow-free terrace area in square metres.
        
    Returns:
        Structured dictionary containing precise subsidy, area feasibility,
        estimated cost, monthly generation, annual savings, and payback period.
    """
    if capacity_kw <= 0:
        raise ValueError("Solar capacity must be greater than 0 kW.")

    # 1. Calculate Central Financial Assistance (CFA) Subsidy
    if capacity_kw <= 2.0:
        subsidy = capacity_kw * SUBSIDY_FIRST_2KW_PER_KW
    elif capacity_kw <= 3.0:
        subsidy = (2.0 * SUBSIDY_FIRST_2KW_PER_KW) + ((capacity_kw - 2.0) * SUBSIDY_ADDITIONAL_PER_KW)
    else:
        subsidy = MAX_SUBSIDY_CAP

    # 2. System Capital Cost & Consumer Net Outlay
    estimated_total_cost = capacity_kw * BENCHMARK_COST_PER_KW
    net_cost_to_consumer = max(0.0, estimated_total_cost - subsidy)

    # 3. Rooftop Area Requirement & Feasibility Check
    required_area_sqm = capacity_kw * SQM_PER_KW
    is_area_sufficient = available_terrace_sqm >= required_area_sqm
    area_surplus_deficit = available_terrace_sqm - required_area_sqm

    # 4. Energy Generation & Electricity Bill Offset
    monthly_generation_units = capacity_kw * AVG_DAILY_UNITS_PER_KW * 30.0  # kWh / month
    estimated_monthly_consumption_units = monthly_bill / MSEDCL_AVG_TARIFF_PER_UNIT
    
    # Savings cannot exceed electricity bill consumption
    bill_offset_units = min(monthly_generation_units, estimated_monthly_consumption_units)
    monthly_savings = bill_offset_units * MSEDCL_AVG_TARIFF_PER_UNIT
    annual_savings = monthly_savings * 12.0

    # 5. Approximate Payback Period (years)
    payback_years = round(net_cost_to_consumer / annual_savings, 1) if annual_savings > 0 else 0.0

    return {
        "capacity_kw": capacity_kw,
        "eligible_subsidy_inr": round(subsidy, 2),
        "subsidy_breakdown": (
            f"₹60,000 (first 2 kW) + ₹{round(subsidy - 60000, 2):,} (additional)"
            if capacity_kw > 2.0 and capacity_kw <= 3.0
            else f"₹{round(subsidy, 2):,} (capped at ₹78,000)" if capacity_kw > 3.0
            else f"₹{round(subsidy, 2):,} (₹30,000/kW)"
        ),
        "estimated_total_cost_inr": round(estimated_total_cost, 2),
        "net_cost_to_consumer_inr": round(net_cost_to_consumer, 2),
        "required_terrace_sqm": round(required_area_sqm, 1),
        "available_terrace_sqm": round(available_terrace_sqm, 1),
        "is_area_sufficient": is_area_sufficient,
        "terrace_margin_sqm": round(area_surplus_deficit, 1),
        "monthly_generation_units_kwh": round(monthly_generation_units, 1),
        "monthly_bill_inr": round(monthly_bill, 2),
        "estimated_monthly_savings_inr": round(monthly_savings, 2),
        "estimated_annual_savings_inr": round(annual_savings, 2),
        "payback_period_years": payback_years,
        "citation": "PM Surya Ghar Operational Guidelines (June 2024) - Clause 4 (CFA Component)"
    }


def rag_search_tool(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Query the SuryaGharSathi ChromaDB knowledge base for official scheme rules.
    
    Args:
        query: Specific policy, warranty, or procedure question.
        top_k: Number of relevant chunks to retrieve.
        
    Returns:
        Grounded answer with citations and confidence metrics.
    """
    return rag_pipeline.answer_question(question=query, top_k=top_k)


# ------------------------------------------------------------------------------
# Tool Schemas for Model Function Calling
# ------------------------------------------------------------------------------
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "solar_cfa_calculator",
            "description": (
                "Calculate official PM Surya Ghar subsidy (CFA), net cost, rooftop area feasibility, "
                "and payback period for residential solar installations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "capacity_kw": {
                        "type": "number",
                        "description": "Proposed solar plant capacity in kW (e.g., 2.0, 3.0, 5.0)."
                    },
                    "monthly_bill": {
                        "type": "number",
                        "description": "Current monthly electricity bill in INR (e.g. 2000.0)."
                    },
                    "available_terrace_sqm": {
                        "type": "number",
                        "description": "Available shadow-free terrace area in square metres (e.g. 40.0)."
                    }
                },
                "required": ["capacity_kw"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rag_search_tool",
            "description": (
                "Search verified official PM Surya Ghar scheme guidelines, warranty terms, "
                "vendor empanelment rules, and national portal procedures."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Specific question about scheme rules, warranties, or application steps."
                    }
                },
                "required": ["query"]
            }
        }
    }
]


if __name__ == "__main__":
    print("=" * 75)
    print("🛠️ TESTING AGENT TOOLS (app/tools.py)")
    print("=" * 75)
    
    # Test Kopargaon Homeowner persona: 3 kW system, ₹2,000 bill, 40 sq m terrace
    calc_result = solar_cfa_calculator(capacity_kw=3.0, monthly_bill=2000.0, available_terrace_sqm=40.0)
    print("\n[Tool: solar_cfa_calculator (3 kW in Kopargaon)]")
    print(f" • Capacity: {calc_result['capacity_kw']} kW")
    print(f" • Eligible CFA Subsidy: ₹{calc_result['eligible_subsidy_inr']:,} ({calc_result['subsidy_breakdown']})")
    print(f" • Estimated Gross Cost: ₹{calc_result['estimated_total_cost_inr']:,}")
    print(f" • Net Cost to Homeowner: ₹{calc_result['net_cost_to_consumer_inr']:,}")
    print(f" • Required Terrace Area: {calc_result['required_terrace_sqm']} sq m (Available: {calc_result['available_terrace_sqm']} sq m -> Feasible: {calc_result['is_area_sufficient']})")
    print(f" • Monthly Generation: {calc_result['monthly_generation_units_kwh']} kWh (~₹{calc_result['estimated_monthly_savings_inr']:,}/month saved)")
    print(f" • Estimated Payback: {calc_result['payback_period_years']} years")
    
    # Test RAG Tool
    print("\n[Tool: rag_search_tool]")
    rag_res = rag_search_tool("What is the warranty period on solar panels?")
    print(f" • Answer snippet: {rag_res['answer'][:120]}...")
    print(f" • Citations count: {len(rag_res['citations'])}")
    print("=" * 75)
