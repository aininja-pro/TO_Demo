#!/usr/bin/env python3
"""Test script for PDF extraction functionality.

Run this to verify the pdfplumber-based extraction is working correctly.
Expected results from E200 (page 3, 0-indexed: 2):
  F2=6, F3=10, F4=10, F7=3, F8=1

Usage:
    python3 test_pdf_extraction.py
"""
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Ground truth for validation
EXPECTED_FIXTURES = {
    'F2': 6,
    'F3': 10,
    'F4': 10,
    'F4E': 2,
    'F5': 8,
    'F7': 3,
    'F7E': 2,
    'F8': 1,
    'F9': 6,
    'X1': 5,
    'X2': 1,
}


def test_fixture_extraction():
    """Test fixture count extraction from E200."""
    print("=" * 60)
    print("TEST: PDF Fixture Extraction")
    print("=" * 60)

    try:
        from takeoff_system.pdf_extractor import extract_fixture_counts
    except ImportError as e:
        print(f"ERROR: Could not import pdf_extractor: {e}")
        print("Make sure pdfplumber is installed: pip install pdfplumber")
        return False

    pdf_path = "Electrical Plans IVCC CETLA.pdf"

    if not Path(pdf_path).exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return False

    print(f"\nExtracting from: {pdf_path}")
    print("Page 3 (E200 - Lighting Floor Plan)")
    print("-" * 60)

    # E200 is page 3 (0-indexed: 2)
    counts = extract_fixture_counts(pdf_path, 2)

    print("\nExtracted counts:")
    for fixture, count in sorted(counts.items()):
        expected = EXPECTED_FIXTURES.get(fixture, "?")
        status = "OK" if count == expected else "MISMATCH"
        print(f"  {fixture}: {count} (expected: {expected}) [{status}]")

    # Calculate accuracy
    correct = 0
    total = len(EXPECTED_FIXTURES)
    for fixture, expected in EXPECTED_FIXTURES.items():
        if counts.get(fixture, 0) == expected:
            correct += 1

    accuracy = (correct / total) * 100
    print(f"\nAccuracy: {correct}/{total} ({accuracy:.1f}%)")

    return accuracy >= 70  # Pass if at least 70% accurate


def test_table_extraction():
    """Test schedule table extraction from E600."""
    print("\n" + "=" * 60)
    print("TEST: Schedule Table Extraction")
    print("=" * 60)

    try:
        from takeoff_system.pdf_extractor import extract_schedule_tables
    except ImportError as e:
        print(f"ERROR: Could not import: {e}")
        return False

    pdf_path = "Electrical Plans IVCC CETLA.pdf"

    if not Path(pdf_path).exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return False

    print(f"\nExtracting tables from: {pdf_path}")
    print("Page 5 (E600 - Fixture Schedule)")
    print("-" * 60)

    # E600 is page 5 (0-indexed: 4)
    tables = extract_schedule_tables(pdf_path, 4)

    print(f"\nFound {len(tables)} tables")

    for i, table in enumerate(tables):
        print(f"\nTable {i + 1}: {len(table)} rows")
        if table and len(table) > 0:
            # Show first few rows
            for row_idx, row in enumerate(table[:3]):
                print(f"  Row {row_idx}: {row[:4] if row else '(empty)'}...")

    return len(tables) > 0


def test_vector_extraction():
    """Test vector path extraction for conduit lengths."""
    print("\n" + "=" * 60)
    print("TEST: Vector Path Extraction")
    print("=" * 60)

    try:
        from takeoff_system.pdf_extractor import analyze_drawing_elements
    except ImportError as e:
        print(f"ERROR: Could not import: {e}")
        return False

    try:
        import fitz
    except ImportError:
        print("WARNING: PyMuPDF not installed. Install with: pip install pymupdf")
        print("Skipping vector extraction test.")
        return True  # Not a failure, just skip

    pdf_path = "Electrical Plans IVCC CETLA.pdf"

    if not Path(pdf_path).exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return False

    print(f"\nAnalyzing drawing elements from: {pdf_path}")
    print("Page 3 (E200 - Lighting Floor Plan)")
    print("-" * 60)

    # E200 is page 3 (0-indexed: 2)
    stats = analyze_drawing_elements(pdf_path, 2)

    if 'error' in stats:
        print(f"ERROR: {stats['error']}")
        return False

    print(f"\nDrawing element statistics:")
    print(f"  Total drawings: {stats['total_drawings']}")
    print(f"  Line counts by width: {stats['line_counts_by_width']}")
    print(f"  Colors used: {len(stats['colors_used'])} unique colors")

    return stats['total_drawings'] > 0


def test_integration():
    """Test integration with main pipeline."""
    print("\n" + "=" * 60)
    print("TEST: Main Pipeline Integration")
    print("=" * 60)

    try:
        from takeoff_system.pdf_extractor import extract_floor_plan_data
    except ImportError as e:
        print(f"ERROR: Could not import: {e}")
        return False

    pdf_path = "Electrical Plans IVCC CETLA.pdf"

    if not Path(pdf_path).exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return False

    print(f"\nExtracting from multiple floor plans...")
    print("-" * 60)

    # Test with both E200 and E201
    counts = extract_floor_plan_data(pdf_path, {'E200': 2, 'E201': 3})

    print(f"\nCombined fixture counts: {counts.fixtures}")

    return len(counts.fixtures) > 0


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("MEP TAKEOFF SYSTEM - PDF EXTRACTION TESTS")
    print("=" * 70)

    results = []

    results.append(("Fixture Extraction", test_fixture_extraction()))
    results.append(("Table Extraction", test_table_extraction()))
    results.append(("Vector Extraction", test_vector_extraction()))
    results.append(("Integration", test_integration()))

    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("-" * 70)
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
