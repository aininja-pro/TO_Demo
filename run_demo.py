#!/usr/bin/env python3
"""
MEP TakeOff System - Demo Script

This script demonstrates the takeoff system on the IVCC CETLA project.
It can run in full mode (with API) or demo mode (showing architecture without API calls).
"""
import os
import sys
from pathlib import Path

# Add the project directory to path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))


def run_demo_mode():
    """Run without API calls - demonstrates the system architecture."""
    print("=" * 70)
    print("MEP TAKEOFF SYSTEM - DEMO MODE")
    print("(Running without API - shows system architecture)")
    print("=" * 70)

    from takeoff_system.models import DeviceCounts, SheetType
    from takeoff_system.pdf_processor import IVCC_SHEET_MAP, classify_sheet_number
    from takeoff_system.business_rules import derive_all_materials
    from takeoff_system.validator import validate_counts, print_validation_report
    from takeoff_system.output_generator import generate_material_list_text
    from takeoff_system.ground_truth import (
        GROUND_TRUTH_FIXTURES, GROUND_TRUTH_LINEAR, GROUND_TRUTH_CONTROLS,
        GROUND_TRUTH_POWER, GROUND_TRUTH_DEMO, GROUND_TRUTH_TECHNOLOGY
    )

    # Step 1: Show sheet classification
    print("\n📋 STEP 1: Sheet Classification")
    print("-" * 50)
    for page, (sheet_num, title, sheet_type) in IVCC_SHEET_MAP.items():
        print(f"  Page {page:2d}: {sheet_num} ({sheet_type.value:9}) - {title}")

    # Step 2: Simulate AI vision counts (using ground truth as example)
    print("\n🔍 STEP 2: Symbol Counting (simulated)")
    print("-" * 50)
    print("  In full mode, Claude Vision would analyze each sheet image.")
    print("  For demo, using ground truth values to show the workflow.")

    # Simulated counts (this would come from AI in production)
    simulated_counts = {
        **GROUND_TRUTH_FIXTURES,
        **GROUND_TRUTH_LINEAR,
        **GROUND_TRUTH_CONTROLS,
        **GROUND_TRUTH_POWER,
        **GROUND_TRUTH_TECHNOLOGY
    }

    print("\n  Sample NEW counts:")
    for item, count in list(GROUND_TRUTH_FIXTURES.items())[:5]:
        print(f"    {item}: {count}")
    print("    ...")

    # Step 3: Business rules derivation
    print("\n⚙️  STEP 3: Apply Business Rules")
    print("-" * 50)

    derived = derive_all_materials(simulated_counts)

    print("  Derived materials from device counts:")
    print(f"    Power Packs: (16 ceiling + 3 wall sensors) × 0.74 = {derived.get('Power Pack', 0)}")
    print(f"    Cat 6 Cable: 92 jacks × 10 ft = {derived.get('Cat 6 Cable (ft)', 0)} ft")
    print(f"    J-Hooks: {derived.get('Cat 6 Cable (ft)', 0)} ft ÷ 4 = {derived.get('J-Hooks', 0)}")
    print(f"    Fixture Whips: {GROUND_TRUTH_FIXTURES['F2']} F2 + {GROUND_TRUTH_FIXTURES['F8']} F8 = {derived.get('Fixture Whip', 0)}")

    # Step 4: Validation
    print("\n✅ STEP 4: Validation Against Ground Truth")
    print("-" * 50)

    # For demo, include demo counts in validation
    all_counts = {**simulated_counts, **GROUND_TRUTH_DEMO}
    results = validate_counts(all_counts)
    exact, close, miss = print_validation_report(results)

    # Step 5: Output generation
    print("\n📄 STEP 5: Generate Material List")
    print("-" * 50)

    output = generate_material_list_text(
        simulated_counts,
        GROUND_TRUTH_DEMO,
        derived,
        "IVCC CETLA Program Renovation"
    )
    print(output)

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("""
To run with actual AI vision analysis:

1. Set your Anthropic API key:
   export ANTHROPIC_API_KEY='your-key-here'

2. Install dependencies:
   pip install anthropic pdf2image Pillow

3. Run full pipeline:
   python run_demo.py --full

Or in Python:
   from takeoff_system.main import run_full_pipeline
   system = run_full_pipeline('/path/to/drawings.pdf')
""")


def run_full_mode():
    """Run with actual API calls."""
    pdf_path = os.path.join(PROJECT_DIR, "Electrical Plans IVCC CETLA.pdf")
    output_dir = os.path.join(PROJECT_DIR, "takeoff_output")

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    from takeoff_system.main import run_full_pipeline
    run_full_pipeline(pdf_path, output_dir, api_key)


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        run_full_mode()
    else:
        run_demo_mode()


if __name__ == "__main__":
    main()
