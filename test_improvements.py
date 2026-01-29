#!/usr/bin/env python3
"""Test the improvements to the takeoff system.

This script tests:
1. Auto-detection of sheet pages
2. Enhanced Demo extraction
3. Enhanced Technology extraction
4. Linear LED and Pendant counting
5. ProjectConfig creation
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from takeoff_system.pdf_extractor import (
    detect_sheet_pages,
    extract_demo_items_enhanced,
    extract_technology_enhanced,
    extract_all_from_pdf,
    count_linear_leds_from_floor_plans,
    count_pendants_from_floor_plans,
)
from takeoff_system.config import ProjectConfig, create_config_from_pdf
from takeoff_system.ground_truth import (
    GROUND_TRUTH_DEMO,
    GROUND_TRUTH_TECHNOLOGY,
    GROUND_TRUTH_LINEAR,
    GROUND_TRUTH_PENDANTS,
    ALL_GROUND_TRUTH,
)


def test_sheet_detection(pdf_path: str):
    """Test auto-detection of sheet pages."""
    print("\n" + "=" * 60)
    print("TEST 1: Sheet Page Detection")
    print("=" * 60)

    try:
        sheet_map = detect_sheet_pages(pdf_path)
        print(f"Detected {len(sheet_map)} sheets:")
        for sheet, page in sorted(sheet_map.items()):
            print(f"  {sheet}: page {page}")

        # Check expected sheets
        expected = ["E100", "E200", "E201", "E600", "E700", "T200"]
        found = [s for s in expected if s in sheet_map]
        print(f"\nFound {len(found)}/{len(expected)} expected sheets")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False


def test_demo_extraction(pdf_path: str):
    """Test enhanced demo extraction."""
    print("\n" + "=" * 60)
    print("TEST 2: Demo Extraction (E100)")
    print("=" * 60)

    try:
        demo = extract_demo_items_enhanced(pdf_path)
        print("Extracted demo items:")

        total_correct = 0
        total_items = 0

        for item, expected in GROUND_TRUTH_DEMO.items():
            actual = demo.get(item, 0)
            status = "OK" if actual == expected else ("CLOSE" if abs(actual - expected) <= 3 else "MISS")
            if status in ["OK", "CLOSE"]:
                total_correct += 1
            total_items += 1
            print(f"  {item}: {actual} (expected {expected}) [{status}]")

        accuracy = total_correct / total_items * 100 if total_items > 0 else 0
        print(f"\nDemo accuracy: {accuracy:.1f}% ({total_correct}/{total_items} correct/close)")
        return accuracy
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_technology_extraction(pdf_path: str):
    """Test enhanced technology extraction."""
    print("\n" + "=" * 60)
    print("TEST 3: Technology Extraction (T200)")
    print("=" * 60)

    try:
        tech = extract_technology_enhanced(pdf_path)
        print("Extracted technology items:")

        # Focus on Cat 6 Jack count
        actual_jacks = tech.get("Cat 6 Jack", 0)
        expected_jacks = GROUND_TRUTH_TECHNOLOGY.get("Cat 6 Jack", 92)

        accuracy = min(actual_jacks, expected_jacks) / max(actual_jacks, expected_jacks) * 100 if expected_jacks > 0 else 0

        print(f"  Cat 6 Jack: {actual_jacks} (expected {expected_jacks})")
        print(f"\nTechnology accuracy: {accuracy:.1f}%")
        return accuracy
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_full_extraction(pdf_path: str):
    """Test the complete extraction pipeline."""
    print("\n" + "=" * 60)
    print("TEST 4: Full Extraction Pipeline")
    print("=" * 60)

    try:
        results = extract_all_from_pdf(pdf_path)

        print("Extraction results:")
        for category, items in results.items():
            if items:
                print(f"\n  {category.upper()}:")
                for item, count in items.items():
                    expected = ALL_GROUND_TRUTH.get(item, "?")
                    status = ""
                    if expected != "?":
                        if count == expected:
                            status = " [OK]"
                        elif abs(count - expected) <= 3:
                            status = " [CLOSE]"
                        else:
                            status = f" [expected {expected}]"
                    print(f"    {item}: {count}{status}")

        return True
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_creation(pdf_path: str):
    """Test ProjectConfig creation from PDF."""
    print("\n" + "=" * 60)
    print("TEST 5: ProjectConfig Creation")
    print("=" * 60)

    try:
        config = create_config_from_pdf(pdf_path)

        print(f"Created config for: {config.name}")
        print(f"  Floor count: {config.floor_count}")
        print(f"  Building sqft: {config.building_sqft}")
        print(f"  Sheet map: {config.sheet_map}")
        print(f"  Fixture definitions: {len(config.fixture_definitions)} types")

        return True
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def calculate_overall_accuracy(pdf_path: str):
    """Calculate overall accuracy improvement."""
    print("\n" + "=" * 60)
    print("OVERALL ACCURACY SUMMARY")
    print("=" * 60)

    results = extract_all_from_pdf(pdf_path)

    # Flatten all results
    all_extracted = {}
    for category, items in results.items():
        all_extracted.update(items)

    exact = 0
    close = 0
    miss = 0

    for item, expected in ALL_GROUND_TRUTH.items():
        actual = all_extracted.get(item, 0)
        if actual == expected:
            exact += 1
        elif abs(actual - expected) <= max(3, expected * 0.15):  # Within 3 or 15%
            close += 1
        else:
            miss += 1

    total = exact + close + miss
    accuracy = (exact + close) / total * 100 if total > 0 else 0

    print(f"Exact matches: {exact}")
    print(f"Close matches: {close}")
    print(f"Misses: {miss}")
    print(f"\nOverall accuracy: {accuracy:.1f}% ({exact + close}/{total} correct/close)")
    print(f"  (Target: 60%, Previous: 28%)")

    return accuracy


def main():
    """Run all tests."""
    pdf_path = "Electrical Plans IVCC CETLA.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    print("Testing Takeoff System Improvements")
    print("=" * 60)
    print(f"PDF: {pdf_path}")

    # Run tests
    test_sheet_detection(pdf_path)
    test_demo_extraction(pdf_path)
    test_technology_extraction(pdf_path)
    test_config_creation(pdf_path)
    test_full_extraction(pdf_path)

    # Calculate overall accuracy
    accuracy = calculate_overall_accuracy(pdf_path)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if accuracy >= 60:
        print(f"SUCCESS: Achieved {accuracy:.1f}% accuracy (target: 60%)")
    else:
        print(f"PROGRESS: Achieved {accuracy:.1f}% accuracy (target: 60%)")
        print("  Further improvements needed.")


if __name__ == "__main__":
    main()
