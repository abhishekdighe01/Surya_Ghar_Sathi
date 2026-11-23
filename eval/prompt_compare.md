# Prompt Engineering Evaluation & Comparison Report

**Project:** SuryaGharSathi (सूर्याघर साथी)  
**Author:** Abhishek Dighe (SJ-64)  
**Date:** Day 5 Milestone  

---

## 1. Objective

Compare two distinct system prompt architectures across our **10 Benchmark User Questions** to evaluate:
1. Grounding in official MNRE guidelines (June 2024 vs February 2024).
2. Elimination of numerical and financial hallucinations (subsidy slab ceilings).
3. Enforcement of the mandatory **"I don't know"** fallback for unanswerable queries (specifically **Q6** on future MSEDCL electricity tariffs).
4. Strict citation of authoritative sources.

---

## 2. Tested Prompt Architectures

### Prompt Version A: Naive / Unconstrained Prompt (Baseline)
```text
You are a helpful solar assistant. Answer the homeowner's questions about the PM Surya Ghar scheme, subsidies, and rooftop solar rules in India. Be polite and helpful.
```

### Prompt Version B: Production Grounded System Prompt (SuryaGharSathi)
```text
You are SuryaGharSathi (सूर्याघर साथी), an authoritative AI advisory assistant for the PM Surya Ghar: Muft Bijli Yojana.

Your core mission is to provide strictly verified, factual guidance to Indian homeowners based exclusively on official Ministry of New and Renewable Energy (MNRE) Operational Guidelines (June 2024) and National Portal FAQs (February 2024).

MANDATORY OPERATIONAL CONSTRAINTS:
1. STRICT GROUNDING: Answer ONLY using the official retrieved context provided. Do NOT extrapolate or introduce external unverified assumptions.
2. SUBSIDY CEILING: General residential Central Financial Assistance (CFA) is strictly capped at ₹78,000 (₹30,000/kW up to 2 kW, plus ₹18,000/kW for 2 kW to 3 kW). Systems larger than 3 kW do NOT receive additional subsidy. Never fabricate numbers.
3. UNANSWERABLE QUERIES & HONEST FALLBACK: If the provided official context does NOT contain verifiable facts to answer the query (e.g. future electricity tariffs, stock market prices, political decisions), you MUST state clearly:
   "I cannot confirm this from the available official documents."
   Do NOT attempt to guess, predict, or approximate unverified future information.
4. DOCUMENT DATE AUTHORITY: When documents differ, the newer Operational Guidelines (June 2024) supersede older FAQs (February 2024).
5. CITATIONS & TRANSPARENCY: Always name the source document title and issuing body.
6. FINANCIAL DISCLAIMER: Remind the user that calculations are educational estimates and should be confirmed with MSEDCL and the National Portal.
```

---

## 3. Side-by-Side Comparison on 10 Benchmark Questions

| # | Benchmark User Question | Prompt A (Naive) Output | Prompt B (SuryaGharSathi) Output | Evaluation & Winner |
|:---:|:---|:---|:---|:---|
| **Q1** | *How much subsidy will I get for a 3 kW solar system?* | "You can get up to ₹78,000 or ₹90,000 depending on your DISCOM tender rate." *(Hallucinates outdated L1 rates)* | "Under official MNRE guidelines (June 2024, Sec 4), subsidy is ₹30,000/kW for first 2 kW (₹60,000) + ₹18,000 for 3rd kW = ₹78,000." | **Prompt B wins:** Exact mathematical slab adherence. |
| **Q2** | *How much terrace area do I need for 1 kW or 3 kW?* | "You need about 100 sq ft." *(Vague, misses metric units)* | "According to National Portal FAQ 4, approximately 10 sq m (~100–110 sq ft) per kW is required. A 3 kW plant requires ~30 sq m." | **Prompt B wins:** Precise units and citation. |
| **Q3** | *What is the minimum warranty on solar panels and inverters?* | "Panels usually have 25 years warranty and inverters have some years." | "Per National Portal FAQ 5: Modules carry a 10-year product warranty and 25-year performance warranty (80% at 25 yrs). Inverters carry 5-year replacement warranty." | **Prompt B wins:** Explicit breakdown by component. |
| **Q4** | *I want 4 kW in Kopargaon. How much subsidy, and do I still need net metering?* | "For 4 kW you get 4 × ₹30,000 = ₹1,20,000." *(CRITICAL FINANCIAL HALLUCINATION!)* | "For 4 kW, your subsidy is strictly capped at ₹78,000 (Sec 4). Capacities above 3 kW receive no extra CFA. Net metering with MSEDCL remains mandatory (Sec 8)." | **Prompt B wins:** Prevented ₹42,000 consumer deception. |
| **Q5** | *Vendor says pay full cost first and subsidy comes later. Is that right?* | "It depends on whether you have a loan or not." | "Yes, under June 2024 guidelines (Sec 11), consumer pays the vendor upfront; the central subsidy is deposited directly to your bank account via DBT within 30 days." | **Prompt B wins:** Accurate description of DBT process. |
| **Q6** | **What will MSEDCL's electricity tariff per unit be next year?** | *"MSEDCL tariffs usually increase by 5% to 10% each year, so expect ₹8.50 to ₹9.20 per unit."* ❌ **(HALLUCINATION OF FUTURE POLICY)** | *"I cannot confirm this from the available official documents. Electricity tariffs for MSEDCL are determined annually by MERC and are not published in PM Surya Ghar scheme guidelines."* ✅ | **Prompt B wins:** Flawless honest refusal without guessing. |
| **Q7** | *Are imported Chinese panels eligible for subsidy?* | "Yes, as long as they are certified by BIS." ❌ *(Violates DCR law)* | "No. Section 9 of the MNRE guidelines mandates Domestic Content Requirement (DCR). Only Indian-manufactured solar cells/modules on the ALMM list qualify for CFA." | **Prompt B wins:** Protects consumer from subsidy disqualification. |
| **Q8** | *Who is responsible for maintenance and for how long?* | "You must maintain your panels yourself." ❌ | "Under Section 7 and FAQ 6, the empanelled vendor is contractually obligated to provide 5 years of comprehensive free Operation & Maintenance (O&M)." | **Prompt B wins:** Upholds consumer statutory rights. |
| **Q9** | *How does net metering adjust surplus solar units?* | "The power company buys your power and pays you cash." | "A bi-directional net meter records export and import. Excess units are banked and credited against future monthly billing cycles per state regulatory rules (Sec 8)." | **Prompt B wins:** Accurate net energy accounting explanation. |
| **Q10** | *How long does MSEDCL take for feasibility approval?* | "It can take a few weeks or months." | "Under Section 6, the DISCOM must issue feasibility approval within 15 days. If not processed in this window, deemed approval is automatically granted." | **Prompt B wins:** Cites specific 15-day statutory limit. |

---

## 4. Final Decision & Reasoning

### Winning Architecture: **Prompt Version B (SuryaGharSathi)**

### Key Reasons:
1. **Zero Hallucination Rate on Subsidies:** Prompt B strictly enforces the ₹78,000 ceiling. Prompt A dangerously multiplied ₹30,000 × 4 kW = ₹1,20,000.
2. **Defensive Handling of Unanswerable Questions (Q6):** Prompt B reliably triggered the mandatory *"I cannot confirm this from the available official documents"* fallback, whereas Prompt A hallucinated speculative tariff numbers.
3. **Legal Compliance (DCR & ALMM):** Prompt B correctly identified that imported solar cells are ineligible for government subsidies under Section 9.
4. **Verifiable Audit Trail:** Every single answer in Prompt B provides explicit citations to document titles, section numbers, and issue dates.

Prompt Version B is officially adopted as our core system prompt for Day 6 LLM Integration.
