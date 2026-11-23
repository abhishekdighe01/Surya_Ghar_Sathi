# ==============================================================================
# File: day01_intro.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 1 - Foundational introduction script demonstrating Python variables,
#              f-strings, and basic terminal input/output.
# ==============================================================================

def main():
    # --------------------------------------------------------------------------
    # 1. Project Information Variables
    # --------------------------------------------------------------------------
    product_name = "SuryaGharSathi (सूर्याघर साथी)"
    
    product_description = (
        "An AI-powered solar advisory assistant that explains PM Surya Ghar: "
        "Muft Bijli Yojana rules, computes exact central government subsidies (CFA), "
        "checks rooftop suitability, and projects financial payback periods."
    )
    
    target_user = (
        "Homeowner in Kopargaon, Maharashtra with a monthly MSEDCL electricity bill "
        "of approximately ₹2,000 and 40 sq m of available terrace space, evaluating "
        "a 2 kW or 3 kW rooftop solar installation."
    )
    
    problem_statement = (
        "Indian homeowners struggle to navigate rooftop solar scheme regulations, "
        "calculate tiered central financial assistance (CFA) accurately, understand "
        "net metering requirements with DISCOMs like MSEDCL, and evaluate true payback "
        "periods without falling victim to vendor misinformation or outdated portal rates."
    )
    
    data_sources = (
        "1. Ministry of New and Renewable Energy (MNRE) Operational Guidelines (June 2024)\n"
        "2. PM Surya Ghar National Portal FAQs (February 2024)"
    )

    # --------------------------------------------------------------------------
    # 2. Display Project Card using f-strings
    # --------------------------------------------------------------------------
    print("=" * 80)
    print(f"🌟 WELCOME TO {product_name.upper()} 🌟")
    print("=" * 80)
    print(f"\n📌 Project Overview:\n{product_description}")
    print(f"\n🎯 Target User Profile:\n{target_user}")
    print(f"\n⚠️ Problem Statement:\n{problem_statement}")
    print(f"\n📚 Official Data Sources:\n{data_sources}")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # 3. Interactive User Input Section
    # --------------------------------------------------------------------------
    print("\n👋 Let's get to know you!")
    user_name = input("Please enter your name: ").strip()
    
    if not user_name:
        user_name = "Valued Homeowner"
        
    print(f"\nHello, {user_name}! It's great to connect with you.")
    user_question = input("What would you like to know about rooftop solar under PM Surya Ghar? ").strip()
    
    print("\n" + "-" * 80)
    print(f"Thank you, {user_name}!")
    print(f"We received your question: \"{user_question}\"")
    print(f"As we build SuryaGharSathi over the next 15 days, our AI engine will "
          f"retrieve verified answers directly from official MNRE documents!")
    print("-" * 80 + "\n")

if __name__ == "__main__":
    main()
