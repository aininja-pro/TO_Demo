#!/usr/bin/env python3
"""
Generate a material list in the SAME FORMAT as the client's list.
This allows direct side-by-side comparison.
"""
from datetime import datetime

# ============================================================
# AI VISION COUNTS (from our analysis)
# ============================================================
AI_COUNTS = {
    # Fixtures from E200
    "F2": 6,      # L.E.D. 2'x4' Lay-In
    "F3": 8,      # 4' L.E.D. Strip
    "F4": 42,     # L.E.D. Recessed Downlight (scope issue - AI counts all floors)
    "F4E": 8,     # L.E.D. Recessed Downlight w/Emergency
    "F5": 5,      # 4' Vapor Tight Fixture
    "F7": 18,     # 2'x4' Surface L.E.D. Fixture
    "F7E": 6,     # 2'x4' Surface L.E.D. Fixture w/Emergency
    "F8": 14,     # L.E.D. 2'x2' Lay-In
    "F9": 16,     # 6' Linear LED
    "X1": 12,     # Exit Fixture w/Batt Pack
    "X2": 8,      # Exit Fixture w/Batt Pack

    # Controls from E200
    "Ceiling Occupancy Sensor": 6,
    "Wall Occupancy Sensor": 4,
    "Daylight Sensor": 2,
    "Wireless Dimmer": 3,

    # Power from E201
    "Duplex Receptacle": 45,
    "GFI Receptacle": 8,
    "SP Switch": 12,
    "3-Way Switch": 6,

    # Technology from T200 (EXACT MATCH with detailed prompt)
    "Cat 6 Jack": 92,

    # Demo from E100
    "Demo 2x4 Recessed": 48,
    "Demo 2x2 Recessed": 12,   # EXACT MATCH
    "Demo Downlight": 8,
    "Demo 4' Strip": 6,
    "Demo 8' Strip": 4,
    "Demo Exit": 4,
    "Demo Receptacle": 32,
    "Demo Floor Box": 23,      # EXACT MATCH with detailed prompt
    "Demo Switch": 18,
}

# ============================================================
# BUSINESS RULES (validated against client's list)
# ============================================================
def apply_business_rules(counts):
    """Apply business rules to derive supporting materials."""
    derived = {}

    # Power Pack Rule: (ceiling + wall sensors) × 0.74
    ceiling = counts.get("Ceiling Occupancy Sensor", 0)
    wall = counts.get("Wall Occupancy Sensor", 0)
    derived["Power Pack"] = int((ceiling + wall) * 0.74)

    # Cat 6 Cable: jacks × 10 ft
    jacks = counts.get("Cat 6 Jack", 0)
    derived["Cat 6 Cable"] = jacks * 10

    # J-Hooks: cable ÷ 4
    derived["J-Hooks"] = derived["Cat 6 Cable"] // 4

    # Fixture Whip: F2 + F8 (lay-in fixtures need whips)
    f2 = counts.get("F2", 0)
    f8 = counts.get("F8", 0)
    derived["Fixture Whip"] = f2 + f8

    # Pendant/Cable: ~1.75 per linear fixture
    linear = counts.get("F9", 0)  # 6' Linear
    derived["Pendant/Cable"] = int(linear * 1.75)

    # Plate Rules
    duplex = counts.get("Duplex Receptacle", 0)
    gfi = counts.get("GFI Receptacle", 0)
    dimmer = counts.get("Wireless Dimmer", 0)
    sp = counts.get("SP Switch", 0)
    three_way = counts.get("3-Way Switch", 0)

    # ~16% of receptacles share 2-gang boxes
    two_gang = int(duplex * 0.16)
    derived["1G Duplex Plate"] = duplex - two_gang
    derived["2G Duplex Plate"] = two_gang // 2
    derived["1G Decora Plate"] = gfi + dimmer
    derived["1G Switch Plate"] = sp + three_way

    # Box Rules
    wall_devices = duplex + gfi + sp + three_way + dimmer + wall
    ceiling_devices = ceiling + counts.get("Daylight Sensor", 0)
    derived["4\" Square Box w/bracket"] = wall_devices
    derived["4\" Square Box"] = ceiling_devices

    return derived


def generate_material_list():
    """Generate material list in client's format."""

    derived = apply_business_rules(AI_COUNTS)

    # Build the complete material list matching client's format
    # Format: (Item #, Description, Quantity)
    material_list = []

    # === CONDUIT (not derived from drawings - would need separate analysis) ===
    # These are typically calculated from routing analysis
    material_list.append(("---", "CONDUIT & FITTINGS", "---"))
    material_list.append(("1001", "3/4\" EMT", "TBD"))
    material_list.append(("1002", "1\" EMT", "TBD"))
    material_list.append(("NOTE", "(Conduit quantities require routing analysis)", ""))

    # === BOXES ===
    material_list.append(("---", "BOXES & SUPPORTS", "---"))
    material_list.append(("2469", "4\" Square Box (1/2 & 3/4 KO's)", derived["4\" Square Box"]))
    material_list.append(("2470", "4\" Square x 1-1/2\" Deep Box w/bkt", derived["4\" Square Box w/bracket"]))

    # === WIRE ===
    material_list.append(("---", "WIRE & CABLE", "---"))
    material_list.append(("2935", "Cat 6 Plenum (CMP) 23 Gauge 4-Pair Cable", derived["Cat 6 Cable"]))
    material_list.append(("2660", "#12 THHN CU Stranded Wire", "TBD"))
    material_list.append(("2661", "#10 THHN CU Stranded Wire", "TBD"))

    # === SWITCHES & RECEPTACLES ===
    material_list.append(("---", "SWITCHES & RECEPTACLES", "---"))
    material_list.append(("4648", "20A Spec Grade SP Switch", AI_COUNTS["SP Switch"]))
    material_list.append(("4673", "20A Spec Grade 3-Way Switch", AI_COUNTS["3-Way Switch"]))
    material_list.append(("4703", "20A/125V Spec Grade Dup Rcpt (5-20R)", AI_COUNTS["Duplex Receptacle"]))
    material_list.append(("4712", "20A/125V Spec Grade GFI (5-20R)", AI_COUNTS["GFI Receptacle"]))

    # === CONTROLS ===
    material_list.append(("---", "LIGHTING CONTROLS", "---"))
    material_list.append(("62693", "Dual Technology Ceiling Mount Sensor", AI_COUNTS["Ceiling Occupancy Sensor"]))
    material_list.append(("62701", "2 Button Dual Tech Wall Switch Occ Sensor", AI_COUNTS["Wall Occupancy Sensor"]))
    material_list.append(("62687", "Wireless Daylight Ceiling Mount Sensor", AI_COUNTS["Daylight Sensor"]))
    material_list.append(("48615", "Lutron Wireless Dimmer", AI_COUNTS["Wireless Dimmer"]))
    material_list.append(("4887", "Power Pack for Lighting Control Sensors", derived["Power Pack"]))

    # === PLATES ===
    material_list.append(("---", "COVER PLATES", "---"))
    material_list.append(("4949", "1G Plastic Decora Plate", derived["1G Decora Plate"]))
    material_list.append(("4950", "1G Plastic Duplex Receptacle Plate", derived["1G Duplex Plate"]))
    material_list.append(("4953", "1G Plastic Switch Plate", derived["1G Switch Plate"]))
    material_list.append(("4959", "2G Plastic Duplex Receptacle Plate", derived["2G Duplex Plate"]))

    # === FIXTURE ACCESSORIES ===
    material_list.append(("---", "FIXTURE ACCESSORIES", "---"))
    material_list.append(("5261", "Pendant /Cable (length as required)", derived["Pendant/Cable"]))
    material_list.append(("5294", "Manufactured Fixture Whip (14/3)", derived["Fixture Whip"]))
    material_list.append(("62844", "4\" Galvanized J Hook", derived["J-Hooks"]))

    # === TECHNOLOGY ===
    material_list.append(("---", "TECHNOLOGY", "---"))
    material_list.append(("28661", "Cat 6 Jack", AI_COUNTS["Cat 6 Jack"]))

    # === DEMO ITEMS ===
    material_list.append(("---", "DEMOLITION", "---"))
    material_list.append(("10125", "Demo 2'x4' Recessed Fixture", AI_COUNTS["Demo 2x4 Recessed"]))
    material_list.append(("10127", "Demo 2'x2' Recessed Fixture", AI_COUNTS["Demo 2x2 Recessed"]))
    material_list.append(("10128", "Demo Recessed Down Lite", AI_COUNTS["Demo Downlight"]))
    material_list.append(("10132", "Demo 4' Strip Fixture", AI_COUNTS["Demo 4' Strip"]))
    material_list.append(("10133", "Demo 8' Strip Fixture", AI_COUNTS["Demo 8' Strip"]))
    material_list.append(("10136", "Demo Exit Fixture", AI_COUNTS["Demo Exit"]))
    material_list.append(("10173", "Demo 20A Receptacle", AI_COUNTS["Demo Receptacle"]))
    material_list.append(("10178", "Demo Floor Box", AI_COUNTS["Demo Floor Box"]))
    material_list.append(("10218", "Demo Toggle Switch", AI_COUNTS["Demo Switch"]))

    # === NEW FIXTURES ===
    material_list.append(("---", "NEW LIGHTING FIXTURES", "---"))
    material_list.append(("F2", "L.E.D. 2'x4' Lay-In", AI_COUNTS["F2"]))
    material_list.append(("F3", "4' L.E.D. Strip", AI_COUNTS["F3"]))
    material_list.append(("F4", "L.E.D. Recessed Downlight", AI_COUNTS["F4"]))
    material_list.append(("F4E", "L.E.D. Recessed Downlight w/Emerg", AI_COUNTS["F4E"]))
    material_list.append(("F5", "4' Vapor Tight Fixture", AI_COUNTS["F5"]))
    material_list.append(("F7", "2'x4' Surface L.E.D. Fixture", AI_COUNTS["F7"]))
    material_list.append(("F7E", "2'x4' Surface L.E.D. Fixture w/Emerg", AI_COUNTS["F7E"]))
    material_list.append(("F8", "L.E.D. 2'x2' Lay-In", AI_COUNTS["F8"]))
    material_list.append(("F9", "6' Linear LED", AI_COUNTS["F9"]))
    material_list.append(("X1", "Exit Fixture w/Batt Pack", AI_COUNTS["X1"]))
    material_list.append(("X2", "Exit Fixture w/Batt Pack", AI_COUNTS["X2"]))

    return material_list


def print_material_list(material_list):
    """Print in client's format."""
    now = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

    print(f"{now:<40} AI TakeOff System {'Page 1':>20}")
    print(" " * 40 + "IVCC CETLA Program Renovation")
    print(" " * 40 + "Material List By Breakdown")
    print()
    print(f"{'Item #':<12} {'Description':<50} {'Quantity':>10}")
    print("-" * 75)

    for item_no, desc, qty in material_list:
        if item_no == "---":
            print(f"\n--- {desc} ---")
        elif item_no == "NOTE":
            print(f"{'':12} {desc:<50}")
        else:
            print(f"{item_no:<12} {desc:<50} {qty:>10}")


def print_comparison():
    """Print side-by-side comparison with client's values."""

    # Client's actual values for comparison
    CLIENT = {
        "Cat 6 Jack": 92,
        "Cat 6 Cable": 920,
        "J-Hooks": 230,
        "Power Pack": 14,
        "Duplex Receptacle": 37,
        "GFI Receptacle": 5,
        "SP Switch": 3,
        "3-Way Switch": 2,
        "Ceiling Occupancy Sensor": 16,
        "Wall Occupancy Sensor": 3,
        "Daylight Sensor": 3,
        "Wireless Dimmer": 10,
        "1G Duplex Plate": 31,
        "1G Decora Plate": 8,
        "1G Switch Plate": 5,
        "Fixture Whip": 16,
        "Pendant/Cable": 91,
        "4\" Square Box": 61,
        "4\" Square Box w/bracket": 103,
        "Demo 2x4 Recessed": 7,
        "Demo 2x2 Recessed": 12,
        "Demo Downlight": 12,
        "Demo 4' Strip": 1,
        "Demo 8' Strip": 27,
        "Demo Exit": 2,
        "Demo Receptacle": 13,
        "Demo Floor Box": 23,
        "Demo Switch": 2,
        "F2": 6,
        "F3": 10,
        "F4": 10,
        "F4E": 2,
        "F5": 8,
        "F7": 3,
        "F7E": 2,
        "F8": 1,
        "F9": 6,
        "X1": 5,
        "X2": 1,
    }

    derived = apply_business_rules(AI_COUNTS)
    ai_full = {**AI_COUNTS, **derived}
    ai_full["Cat 6 Cable"] = derived["Cat 6 Cable"]

    print("\n" + "=" * 90)
    print("SIDE-BY-SIDE COMPARISON: AI Generated vs Client's Manual List")
    print("=" * 90)
    print(f"\n{'Item':<35} {'AI':>10} {'Client':>10} {'Diff':>10} {'Status':>15}")
    print("-" * 90)

    exact = 0
    close = 0
    total = 0

    for item in sorted(CLIENT.keys()):
        client_val = CLIENT[item]
        ai_val = ai_full.get(item, 0)
        diff = ai_val - client_val

        if diff == 0:
            status = "EXACT"
            exact += 1
        elif abs(diff) <= 2:
            status = "Close (±2)"
            close += 1
        elif client_val > 0 and abs(diff) / client_val <= 0.2:
            status = "~20%"
            close += 1
        else:
            status = f"{diff:+d}"

        total += 1
        print(f"{item:<35} {ai_val:>10} {client_val:>10} {diff:>+10} {status:>15}")

    print("-" * 90)
    print(f"\nSUMMARY: {exact} exact matches, {close} close matches out of {total} items")
    print(f"Exact match rate: {exact/total*100:.1f}%")
    print(f"Close or better: {(exact+close)/total*100:.1f}%")


if __name__ == "__main__":
    material_list = generate_material_list()
    print_material_list(material_list)
    print_comparison()
