"""Validation and comparison tools for generated counts vs ground truth."""
from typing import Dict, List, Tuple

from .models import ValidationResult
from .ground_truth import ALL_GROUND_TRUTH


def validate_counts(
    generated: Dict[str, int],
    ground_truth: Dict[str, int] = None
) -> List[ValidationResult]:
    """
    Compare generated counts against ground truth.

    Args:
        generated: Dictionary of generated item counts
        ground_truth: Dictionary of expected counts (defaults to ALL_GROUND_TRUTH)

    Returns:
        List of ValidationResult objects
    """
    if ground_truth is None:
        ground_truth = ALL_GROUND_TRUTH

    results = []

    # Get all unique items from both dictionaries
    all_items = set(generated.keys()) | set(ground_truth.keys())

    for item in sorted(all_items):
        expected = ground_truth.get(item, 0)
        actual = generated.get(item, 0)
        difference = actual - expected

        # Calculate accuracy percentage
        if expected == 0:
            if actual == 0:
                accuracy = 100.0
            else:
                accuracy = 0.0  # Generated items that shouldn't exist
        else:
            accuracy = max(0, (1 - abs(difference) / expected) * 100)

        # Determine status
        if actual == expected:
            status = "exact"
        elif abs(difference) <= 2:
            status = "close"
        elif accuracy >= 80:
            status = "acceptable"
        else:
            status = "miss"

        results.append(ValidationResult(
            item=item,
            expected=expected,
            actual=actual,
            difference=difference,
            accuracy_pct=round(accuracy, 1),
            status=status
        ))

    return results


def print_validation_report(results: List[ValidationResult]) -> Tuple[int, int, int]:
    """
    Print a formatted validation report.

    Returns:
        Tuple of (exact_matches, close_matches, misses)
    """
    exact = 0
    close = 0
    acceptable = 0
    miss = 0

    print("\n" + "=" * 80)
    print("VALIDATION REPORT: Generated vs Ground Truth")
    print("=" * 80)
    print(f"{'Item':<35} {'Expected':>10} {'Actual':>10} {'Diff':>8} {'Accuracy':>10} {'Status':>10}")
    print("-" * 80)

    for r in results:
        status_symbol = {
            "exact": "✓",
            "close": "~",
            "acceptable": "○",
            "miss": "✗"
        }.get(r.status, "?")

        print(f"{r.item:<35} {r.expected:>10} {r.actual:>10} {r.difference:>+8} {r.accuracy_pct:>9.1f}% {status_symbol:>10}")

        if r.status == "exact":
            exact += 1
        elif r.status == "close":
            close += 1
        elif r.status == "acceptable":
            acceptable += 1
        else:
            miss += 1

    print("-" * 80)
    total = len(results)
    print(f"\nSUMMARY:")
    print(f"  Exact matches:      {exact:3d} / {total} ({exact/total*100:.1f}%)")
    print(f"  Close (±2):         {close:3d} / {total} ({close/total*100:.1f}%)")
    print(f"  Acceptable (≥80%):  {acceptable:3d} / {total} ({acceptable/total*100:.1f}%)")
    print(f"  Misses:             {miss:3d} / {total} ({miss/total*100:.1f}%)")
    print(f"\n  Overall accuracy:   {(exact + close)/total*100:.1f}% (exact + close)")
    print("=" * 80)

    return exact, close, miss


def calculate_overall_accuracy(results: List[ValidationResult]) -> float:
    """Calculate overall accuracy as percentage of items within ±2 of expected."""
    if not results:
        return 0.0

    accurate = sum(1 for r in results if r.status in ("exact", "close"))
    return (accurate / len(results)) * 100
