# ==============================================================================
# File: day01_menu.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 1 - Interactive while-loop console menu demonstrating control flow,
#              conditional statements (if/elif/else), and basic solar rule verification.
# ==============================================================================

def main():
    print("=" * 70)
    print("☀️ Welcome to SuryaGharSathi Interactive Console ☀️")
    print("Your trusted assistant for PM Surya Ghar: Muft Bijli Yojana")
    print("=" * 70)

    # Start the continuous menu loop
    while True:
        print("\n" + "=" * 45)
        print("                 MAIN MENU")
        print("=" * 45)
        print("1. About SuryaGharSathi & Scheme Summary")
        print("2. View Sample Solar Questions & Answers")
        print("3. Check Rooftop Solar Eligibility (Quick Check)")
        print("0. Exit SuryaGharSathi")
        print("=" * 45)
        
        choice = input("Enter your choice (0-3): ").strip()

        # ----------------------------------------------------------------------
        # Option 1: About the product
        # ----------------------------------------------------------------------
        if choice == "1":
            print("\n--- 📖 ABOUT SURYAGHARSATHI ---")
            print("SuryaGharSathi is designed for Indian homeowners (specifically in regions")
            print("like Kopargaon served by MSEDCL) who want clear, verified advice on")
            print("rooftop solar installations under the PM Surya Ghar scheme.")
            print("\nKey Scheme Highlights:")
            print("• Up to 300 units of free electricity every month through solar.")
            print("• Direct Central Financial Assistance (CFA) subsidy credited to your bank.")
            print("• ₹30,000/kW for systems up to 2 kW, and ₹18,000/kW between 2 and 3 kW.")
            print("• Maximum general residential central subsidy capped at ₹78,000.")

        # ----------------------------------------------------------------------
        # Option 2: Sample questions
        # ----------------------------------------------------------------------
        elif choice == "2":
            print("\n--- ❓ FREQUENTLY ASKED QUESTIONS ---")
            print("\nQ1: How much central subsidy will I receive for a 3 kW rooftop solar system?")
            print("A1: Under official MNRE guidelines:")
            print("    • First 2 kW = 2 × ₹30,000 = ₹60,000")
            print("    • Next 1 kW  = 1 × ₹18,000 = ₹18,000")
            print("    • Total Central Subsidy = ₹78,000 (Maximum cap for standard residential).")
            
            print("\nQ2: How much terrace area is required for a 1 kW solar system?")
            print("A2: According to the National Portal FAQ, approximately 10 sq metres")
            print("    (around 100 sq ft) of unshaded, shadow-free roof space is required")
            print("    per 1 kW of installed capacity.")

        # ----------------------------------------------------------------------
        # Option 3: Solar Eligibility & Rule Check (if / elif / else demonstration)
        # ----------------------------------------------------------------------
        elif choice == "3":
            print("\n--- 🔍 ROOFTOP SOLAR ELIGIBILITY & CAPACITY CHECK ---")
            try:
                area_input = input("Enter your shadow-free terrace area (in square metres, e.g., 40): ").strip()
                terrace_area = float(area_input)
                
                bill_input = input("Enter your average monthly electricity bill in ₹ (e.g., 2000): ").strip()
                monthly_bill = float(bill_input)

                print("\n📊 Assessment Results:")
                if terrace_area < 10:
                    print("❌ Insufficient Terrace Space:")
                    print("   A minimum of 10 sq metres of shadow-free roof area is required for a 1 kW setup.")
                elif terrace_area < 20:
                    print("✅ Suitable for a 1 kW System:")
                    print("   • Estimated generation: ~120 units/month")
                    print("   • Central Subsidy: ₹30,000")
                elif terrace_area < 30:
                    print("✅ Suitable for a 2 kW System:")
                    print("   • Estimated generation: ~240 units/month")
                    print("   • Central Subsidy: ₹60,000")
                else:
                    print("🌟 Highly Recommended: 3 kW System (Optimal for Kopargaon Homeowners):")
                    print("   • Terrace area needed: ~30 sq metres (You have ample space!)")
                    print("   • Estimated generation: ~360 units/month")
                    print("   • Central Subsidy: ₹78,000 (Maximum residential subsidy)")
                    if monthly_bill >= 2000:
                        print("   • Since your bill is ₹2,000+, a 3 kW system can bring your bill down to near zero!")
                    else:
                        print("   • A 2 kW or 3 kW system will comfortably cover your current electricity consumption.")
            except ValueError:
                print("⚠️ Invalid numerical input! Please enter valid positive numbers for area and bill.")

        # ----------------------------------------------------------------------
        # Option 0: Exit
        # ----------------------------------------------------------------------
        elif choice == "0":
            print("\nThank you for exploring SuryaGharSathi! Have a sun-powered day! 🌞")
            break

        # ----------------------------------------------------------------------
        # Fallback for unrecognized commands
        # ----------------------------------------------------------------------
        else:
            print("⚠️ Invalid option selected. Please choose 1, 2, 3, or 0.")

if __name__ == "__main__":
    main()
