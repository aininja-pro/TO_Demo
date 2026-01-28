"""Generate formatted material list output.

Supports multiple output formats:
- Text: Human-readable formatted list
- CSV: Spreadsheet-compatible
- JSON: Machine-readable
- Client format: Matching client's exact layout
"""
import csv
import json
from datetime import datetime
from typing import Dict, List, Optional


# Item number mappings for client format
ITEM_NUMBERS = {
    # Conduit
    '3/4" EMT': 1001,
    '1" EMT': 1002,
    '1-1/4" EMT': 1003,
    '1-1/2" EMT': 1004,
    # Fittings - 3/4"
    '3/4" EMT Connector': 1101,
    '3/4" EMT Coupling': 1102,
    '3/4" Insulating Bushing': 1103,
    '3/4" 1-Hole Strap': 1104,
    '3/4" Unistrut Strap': 1105,
    # Fittings - 1"
    '1" EMT Connector': 1111,
    '1" EMT Coupling': 1112,
    '1" Insulating Bushing': 1113,
    '1" 1-Hole Strap': 1114,
    '1" Unistrut Strap': 1115,
    # Wire
    "#12 THHN Black": 2001,
    "#12 THHN White": 2002,
    "#12 THHN Green": 2003,
    "#10 THHN Black": 2011,
    "#10 THHN White": 2012,
    "#10 THHN Green": 2013,
    "#8 THHN Black": 2021,
    "#8 THHN White": 2022,
    "#8 THHN Green": 2023,
    # Boxes
    '4" Square Box w/bracket': 3001,
    '4" Square Box': 3002,
    '4-11/16" Square Box w/bracket': 3011,
    '4-11/16" Square Box': 3012,
    '4" Square Box 2-1/8" deep': 3021,
    # Rings
    '4" Square-1G Plaster Ring': 3101,
    '4" Square-2G Plaster Ring': 3102,
    '4" Square-3/0 Plaster Ring': 3103,
    '4-11/16"-1G Plaster Ring': 3111,
    # Plates
    "Duplex Plate": 3201,
    "Decora Plate": 3202,
    "Switch Plate": 3203,
    "Blank Cover": 3204,
    "Blank Cover w/KO": 3205,
    # Consumables
    "Red Wirenut": 4001,
    "Yellow Wirenut": 4002,
    "Ground Screw": 4003,
    "Pan Head Tapping Screw #8": 4004,
    "Poly Pull Line (ft)": 4005,
    "Black Tape": 4006,
    "Red Phase Tape": 4007,
    "Blue Phase Tape": 4008,
    # Technology
    "Cat 6 Jack": 5001,
    "Cat 6 Cable (ft)": 5002,
    "J-Hook": 5003,
    "Floor Box": 5004,
    # Panel equipment
    "20A 1P Breaker": 6001,
    "30A 2P Breaker": 6002,
    "30A/2P Safety Switch 240V": 6011,
    "30A/3P Safety Switch 600V": 6012,
    "100A/3P Safety Switch 600V": 6013,
    # Controls
    "Ceiling Occupancy Sensor": 7001,
    "Wall Occupancy Sensor": 7002,
    "Daylight Sensor": 7003,
    "Wireless Dimmer": 7004,
    "Power Pack": 7005,
    # Power devices
    "Duplex Receptacle": 7101,
    "GFI Receptacle": 7102,
    "SP Switch": 7103,
    "3-Way Switch": 7104,
    # Fixtures
    "F2": "F2",
    "F3": "F3",
    "F4": "F4",
    "F4E": "F4E",
    "F5": "F5",
    "F7": "F7",
    "F7E": "F7E",
    "F8": "F8",
    "F9": "F9",
    "X1": "X1",
    "X2": "X2",
    # Linear LEDs
    "4' Linear LED": "L4",
    "6' Linear LED": "L6",
    "8' Linear LED": "L8",
    "10' Linear LED": "L10",
    "16' Linear LED": "L16",
    # Pendants
    "F10-22": "F10-22",
    "F10-30": "F10-30",
    "F11-4X4": "F11-4X4",
    "F11-6X6": "F11-6X6",
    "F11-8X8": "F11-8X8",
    "F11-10X10": "F11-10X10",
    "F11-16X10": "F11-16X10",
    # Accessories
    "Fixture Whip": 8001,
    "Pendant/Cable": 8002,
    "Aircraft Cable Kit": 8003,
    "Canopy Kit": 8004,
    # Demo items
    "Demo 2'x4' Recessed": "D01",
    "Demo 2'x2' Recessed": "D02",
    "Demo Downlight": "D03",
    "Demo 4' Strip": "D04",
    "Demo 8' Strip": "D05",
    "Demo Exit": "D06",
    "Demo Receptacle": "D07",
    "Demo Floor Box": "D08",
    "Demo Switch": "D09",
}


def get_item_number(item: str) -> str:
    """Get the item number for a material."""
    return str(ITEM_NUMBERS.get(item, "----"))


def generate_material_list_text(
    new_materials: Dict[str, int],
    demo_materials: Dict[str, int],
    derived_materials: Dict[str, int],
    project_name: str = "IVCC CETLA Program Renovation"
) -> str:
    """
    Generate a formatted text material list.

    Args:
        new_materials: Dictionary of new material counts
        demo_materials: Dictionary of demo item counts
        derived_materials: Dictionary of derived material counts
        project_name: Project name for header

    Returns:
        Formatted string of the material list
    """
    lines = []
    lines.append("=" * 70)
    lines.append(f"MATERIAL LIST: {project_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)

    def add_section(title: str, items: List[tuple], show_item_num: bool = True):
        """Add a section with items."""
        if not items:
            return
        lines.append(f"\n{title}")
        lines.append("-" * 50)
        if show_item_num:
            lines.append(f"{'Item #':<8} {'Description':<35} {'Qty':>8}")
            lines.append("-" * 50)
            for item, qty in items:
                if qty > 0:
                    item_num = get_item_number(item)
                    lines.append(f"{item_num:<8} {item:<35} {qty:>8,}")
        else:
            for item, qty in items:
                if qty > 0:
                    lines.append(f"  {item:<40} {qty:>8,}")

    # NEW FIXTURES
    fixture_tags = ["F2", "F3", "F4", "F4E", "F5", "F7", "F7E", "F8", "F9", "X1", "X2"]
    fixture_items = [(tag, new_materials.get(tag, 0)) for tag in fixture_tags]
    add_section("NEW FIXTURES", [i for i in fixture_items if i[1] > 0])

    # LINEAR LED FIXTURES
    linear_tags = ["4' Linear LED", "6' Linear LED", "8' Linear LED",
                   "10' Linear LED", "16' Linear LED"]
    linear_items = [(tag, new_materials.get(tag, 0)) for tag in linear_tags]
    add_section("LINEAR LED FIXTURES", [i for i in linear_items if i[1] > 0])

    # PENDANT FIXTURES
    pendant_tags = ["F10-22", "F10-30", "F11-4X4", "F11-6X6",
                    "F11-8X8", "F11-10X10", "F11-16X10"]
    pendant_items = [(tag, new_materials.get(tag, 0)) for tag in pendant_tags]
    add_section("PENDANT FIXTURES", [i for i in pendant_items if i[1] > 0])

    # CONTROLS
    control_items = ["Ceiling Occupancy Sensor", "Wall Occupancy Sensor",
                     "Daylight Sensor", "Wireless Dimmer"]
    controls = [(item, new_materials.get(item, 0)) for item in control_items]
    add_section("CONTROLS", [c for c in controls if c[1] > 0])

    # POWER DEVICES
    power_items = ["Duplex Receptacle", "GFI Receptacle", "SP Switch", "3-Way Switch"]
    power = [(item, new_materials.get(item, 0)) for item in power_items]
    add_section("POWER DEVICES", [p for p in power if p[1] > 0])

    # TECHNOLOGY
    tech_items = ["Cat 6 Jack"]
    tech = [(item, new_materials.get(item, 0)) for item in tech_items]
    add_section("TECHNOLOGY", [t for t in tech if t[1] > 0])

    # DERIVED MATERIALS
    if derived_materials:
        # Conduit
        conduit_items = [(k, v) for k, v in derived_materials.items()
                        if "EMT" in k and "Connector" not in k and "Coupling" not in k
                        and "Bushing" not in k and "Strap" not in k]
        add_section("CONDUIT", sorted(conduit_items))

        # Fittings
        fitting_items = [(k, v) for k, v in derived_materials.items()
                        if any(x in k for x in ["Connector", "Coupling", "Bushing", "Strap"])]
        add_section("FITTINGS", sorted(fitting_items))

        # Wire
        wire_items = [(k, v) for k, v in derived_materials.items() if "THHN" in k]
        add_section("WIRE", sorted(wire_items))

        # Boxes
        box_items = [(k, v) for k, v in derived_materials.items()
                    if "Box" in k and "Floor" not in k]
        add_section("BOXES", sorted(box_items))

        # Rings
        ring_items = [(k, v) for k, v in derived_materials.items() if "Ring" in k]
        add_section("PLASTER RINGS", sorted(ring_items))

        # Plates
        plate_items = [(k, v) for k, v in derived_materials.items()
                      if "Plate" in k or "Cover" in k]
        add_section("COVER PLATES", sorted(plate_items))

        # Consumables
        consumable_keys = ["Wirenut", "Screw", "Pull Line", "Tape"]
        consumable_items = [(k, v) for k, v in derived_materials.items()
                          if any(x in k for x in consumable_keys)]
        add_section("CONSUMABLES", sorted(consumable_items))

        # Technology derived
        tech_derived = [(k, v) for k, v in derived_materials.items()
                       if k in ["Cat 6 Cable (ft)", "J-Hook", "Power Pack"]]
        if tech_derived:
            add_section("TECHNOLOGY (Derived)", sorted(tech_derived))

        # Accessories
        accessory_items = [(k, v) for k, v in derived_materials.items()
                          if any(x in k for x in ["Whip", "Pendant", "Cable Kit", "Canopy"])]
        add_section("ACCESSORIES", sorted(accessory_items))

    # DEMO ITEMS
    if demo_materials:
        demo_items = [(k, v) for k, v in sorted(demo_materials.items())]
        add_section("DEMO ITEMS (for removal)", demo_items)

    lines.append("\n" + "=" * 70)

    return "\n".join(lines)


def generate_client_format(
    all_materials: Dict[str, int],
    project_name: str = "IVCC CETLA Program Renovation"
) -> str:
    """
    Generate output matching client's exact format.

    Args:
        all_materials: All materials combined
        project_name: Project name

    Returns:
        Formatted string matching client layout
    """
    lines = []
    lines.append(f"Material List - {project_name}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"{'Item #':<10} {'Description':<45} {'Quantity':>12}")
    lines.append("-" * 70)

    # Sort by item number
    sorted_items = sorted(
        [(get_item_number(k), k, v) for k, v in all_materials.items() if v > 0],
        key=lambda x: (isinstance(x[0], int), x[0])
    )

    for item_num, description, qty in sorted_items:
        lines.append(f"{item_num:<10} {description:<45} {qty:>12,}")

    lines.append("-" * 70)
    lines.append(f"{'TOTAL ITEMS:':<55} {len(sorted_items):>12}")
    lines.append(f"{'TOTAL QUANTITY:':<55} {sum(v for _, _, v in sorted_items):>12,}")

    return "\n".join(lines)


def export_to_csv(
    new_materials: Dict[str, int],
    demo_materials: Dict[str, int],
    derived_materials: Dict[str, int],
    output_path: str
) -> None:
    """Export material list to CSV file."""
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Category', 'Item #', 'Item', 'Quantity'])

        # New materials
        for item, qty in sorted(new_materials.items()):
            if qty > 0:
                writer.writerow(['NEW', get_item_number(item), item, qty])

        # Derived materials
        for item, qty in sorted(derived_materials.items()):
            if qty > 0:
                writer.writerow(['DERIVED', get_item_number(item), item, qty])

        # Demo materials
        for item, qty in sorted(demo_materials.items()):
            if qty > 0:
                writer.writerow(['DEMO', get_item_number(item), item, qty])


def export_to_json(
    new_materials: Dict[str, int],
    demo_materials: Dict[str, int],
    derived_materials: Dict[str, int],
    output_path: str,
    metadata: Optional[Dict] = None
) -> None:
    """Export material list to JSON file."""
    data = {
        "project": "IVCC CETLA Program Renovation",
        "generated": datetime.now().isoformat(),
        "summary": {
            "new_items": len([v for v in new_materials.values() if v > 0]),
            "demo_items": len([v for v in demo_materials.values() if v > 0]),
            "derived_items": len([v for v in derived_materials.values() if v > 0]),
            "total_quantity": sum(new_materials.values()) + sum(demo_materials.values()) + sum(derived_materials.values()),
        },
        "new_materials": {k: v for k, v in new_materials.items() if v > 0},
        "derived_materials": {k: v for k, v in derived_materials.items() if v > 0},
        "demo_materials": {k: v for k, v in demo_materials.items() if v > 0},
    }

    if metadata:
        data["metadata"] = metadata

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def compare_to_client_format(
    generated: Dict[str, int],
    output_path: str = None
) -> str:
    """
    Generate a side-by-side comparison with the client's material list.
    """
    from .ground_truth import (
        GROUND_TRUTH_FIXTURES, GROUND_TRUTH_LINEAR, GROUND_TRUTH_PENDANTS,
        GROUND_TRUTH_CONTROLS, GROUND_TRUTH_POWER, GROUND_TRUTH_PANEL,
        GROUND_TRUTH_DEMO, GROUND_TRUTH_TECHNOLOGY
    )

    lines = []
    lines.append("COMPARISON: Generated vs Client's Material List")
    lines.append("=" * 75)
    lines.append(f"{'Item':<35} {'Client':>12} {'Generated':>12} {'Diff':>8} {'Match':>8}")
    lines.append("-" * 75)

    exact = 0
    close = 0
    miss = 0

    def compare_section(title: str, ground_truth: Dict):
        nonlocal exact, close, miss
        lines.append(f"\n{title}")
        for item, expected in ground_truth.items():
            actual = generated.get(item, 0)
            diff = actual - expected

            if actual == expected:
                match = "EXACT"
                exact += 1
            elif abs(diff) <= 2 or (expected > 0 and abs(diff) / expected <= 0.1):
                match = "CLOSE"
                close += 1
            else:
                match = "MISS"
                miss += 1

            lines.append(f"  {item:<33} {expected:>12,} {actual:>12,} {diff:>+8} {match:>8}")

    compare_section("FIXTURES:", GROUND_TRUTH_FIXTURES)
    compare_section("LINEAR FIXTURES:", GROUND_TRUTH_LINEAR)
    compare_section("PENDANT FIXTURES:", GROUND_TRUTH_PENDANTS)
    compare_section("CONTROLS:", GROUND_TRUTH_CONTROLS)
    compare_section("POWER:", GROUND_TRUTH_POWER)
    compare_section("PANEL:", GROUND_TRUTH_PANEL)
    compare_section("DEMO:", GROUND_TRUTH_DEMO)
    compare_section("TECHNOLOGY:", GROUND_TRUTH_TECHNOLOGY)

    total = exact + close + miss
    lines.append("\n" + "=" * 75)
    lines.append("SUMMARY:")
    lines.append(f"  Exact matches:  {exact:3d} / {total} ({exact/total*100:.1f}%)")
    lines.append(f"  Close (within 10%): {close:3d} / {total} ({close/total*100:.1f}%)")
    lines.append(f"  Misses:         {miss:3d} / {total} ({miss/total*100:.1f}%)")
    lines.append(f"  Overall accuracy: {(exact + close)/total*100:.1f}%")
    lines.append("=" * 75)

    output = "\n".join(lines)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(output)

    return output


def generate_accuracy_report(
    generated: Dict[str, int],
    ground_truth: Dict[str, int] = None
) -> str:
    """
    Generate a detailed accuracy report by category.

    Returns formatted report showing accuracy metrics by material category.
    """
    from .ground_truth import ALL_GROUND_TRUTH, get_category

    if ground_truth is None:
        ground_truth = ALL_GROUND_TRUTH

    categories = {}

    for item, expected in ground_truth.items():
        actual = generated.get(item, 0)
        cat = get_category(item)

        if cat not in categories:
            categories[cat] = {
                "items": 0,
                "exact": 0,
                "close": 0,
                "miss": 0,
                "expected_qty": 0,
                "actual_qty": 0,
            }

        categories[cat]["items"] += 1
        categories[cat]["expected_qty"] += expected
        categories[cat]["actual_qty"] += actual

        if actual == expected:
            categories[cat]["exact"] += 1
        elif abs(actual - expected) <= 2:
            categories[cat]["close"] += 1
        else:
            categories[cat]["miss"] += 1

    lines = []
    lines.append("ACCURACY REPORT")
    lines.append("=" * 80)
    lines.append(f"{'Category':<18} {'Items':>8} {'Exact':>8} {'Close':>8} {'Miss':>8} {'Accuracy':>10}")
    lines.append("-" * 80)

    total_items = 0
    total_exact = 0
    total_close = 0
    total_miss = 0

    for cat in sorted(categories.keys()):
        data = categories[cat]
        accuracy = (data["exact"] + data["close"]) / data["items"] * 100 if data["items"] > 0 else 0

        lines.append(
            f"{cat:<18} {data['items']:>8} {data['exact']:>8} "
            f"{data['close']:>8} {data['miss']:>8} {accuracy:>9.1f}%"
        )

        total_items += data["items"]
        total_exact += data["exact"]
        total_close += data["close"]
        total_miss += data["miss"]

    lines.append("-" * 80)
    overall_accuracy = (total_exact + total_close) / total_items * 100 if total_items > 0 else 0
    lines.append(
        f"{'TOTAL':<18} {total_items:>8} {total_exact:>8} "
        f"{total_close:>8} {total_miss:>8} {overall_accuracy:>9.1f}%"
    )
    lines.append("=" * 80)

    return "\n".join(lines)
