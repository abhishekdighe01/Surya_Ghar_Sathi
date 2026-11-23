# ==============================================================================
# File: app/cli.py
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Day 2 - Command-line interface to interactively search, count,
#              and inspect structured scheme records.
# ==============================================================================

import sys
import os

# Ensure the project root directory is on the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.records import load_records, search, count_by, get_by_id


def format_record(record) -> str:
    """Format a single record nicely for terminal display."""
    separator = "-" * 80
    return (
        f"{separator}\n"
        f"🆔 Record ID: {record.id}\n"
        f"📌 Topic:     {record.topic}\n"
        f"🏛️ Issuing:   {record.issuing_body} ({record.date_issued})\n"
        f"📄 Document:  {record.document_title}\n"
        f"📜 Key Rule:\n   {record.key_rule}\n"
        f"🔗 Source:    {record.source_url}\n"
        f"{separator}"
    )


def main():
    records = load_records()
    print("=" * 80)
    print("☀️ SURYAGHARSATHI — SCHEME RECORDS EXPLORER ☀️")
    print(f"Loaded {len(records)} official records from MNRE Guidelines and Portal FAQs.")
    print("=" * 80)

    while True:
        print("\n" + "=" * 45)
        print("             RECORDS MENU")
        print("=" * 45)
        print("1. Display All Records")
        print("2. Search Records by Keyword")
        print("3. Count Records by Category / Field")
        print("4. Retrieve Record by ID")
        print("0. Exit Explorer")
        print("=" * 45)

        choice = input("Select an option (0-4): ").strip()

        # ----------------------------------------------------------------------
        # Option 1: Display All Records
        # ----------------------------------------------------------------------
        if choice == "1":
            print(f"\nDisplaying all {len(records)} records:\n")
            for r in records:
                print(f"[{r.id:2d}] {r.topic} ({r.date_issued}) - {r.issuing_body[:35]}...")
            print(f"\nTip: Use Option 4 with a record ID (1-{len(records)}) to see the full details.")

        # ----------------------------------------------------------------------
        # Option 2: Search Records by Keyword
        # ----------------------------------------------------------------------
        elif choice == "2":
            query = input("\nEnter search keyword (e.g. 'subsidy', 'warranty', 'terrace'): ").strip()
            if not query:
                print("⚠️ Please enter a non-empty search keyword.")
                continue

            matches = search(records, query)
            print(f"\nFound {len(matches)} matching records for '{query}':\n")
            for m in matches:
                print(format_record(m))

        # ----------------------------------------------------------------------
        # Option 3: Count Records by Field
        # ----------------------------------------------------------------------
        elif choice == "3":
            print("\nCount records by which field?")
            print("a. Issuing Body")
            print("b. Document Title")
            print("c. Issue Date")
            sub_choice = input("Enter choice (a/b/c): ").strip().lower()

            field_map = {
                "a": "issuing_body",
                "b": "document_title",
                "c": "date_issued"
            }
            target_field = field_map.get(sub_choice, "issuing_body")
            counts = count_by(records, target_field)

            print(f"\nRecord counts grouped by '{target_field}':")
            for val, cnt in counts.items():
                print(f" • {val}: {cnt} record(s)")

        # ----------------------------------------------------------------------
        # Option 4: Retrieve Record by ID
        # ----------------------------------------------------------------------
        elif choice == "4":
            id_input = input(f"\nEnter Record ID (1 to {len(records)}): ").strip()
            try:
                rec_id = int(id_input)
                record = get_by_id(records, rec_id)
                if record:
                    print(format_record(record))
                else:
                    print(f"❌ No record found with ID {rec_id}.")
            except ValueError:
                print("⚠️ Invalid ID format. Please enter an integer.")

        # ----------------------------------------------------------------------
        # Option 0: Exit
        # ----------------------------------------------------------------------
        elif choice == "0":
            print("\nExiting Records Explorer. Happy Solar Learning! 🌞")
            break

        else:
            print("⚠️ Invalid option. Please select 0, 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
