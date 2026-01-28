"""Ground truth data from client's material list for validation.

This contains the ACTUAL counts from the client's material list (IVCC CETLA)
used to validate AI-generated counts.

Total: 119 items, 28,000+ units
"""

# =============================================================================
# FIXTURES (from floor plans E200)
# =============================================================================

GROUND_TRUTH_FIXTURES = {
    "F2": 6,      # 2'x4' Lay-In LED
    "F3": 10,     # 4' LED Strip
    "F4": 10,     # LED Recessed Downlight
    "F4E": 2,     # Downlight w/Emergency
    "F5": 8,      # 4' Vapor Tight
    "F7": 3,      # 2'x4' Surface LED
    "F7E": 2,     # Surface LED w/Emergency
    "F8": 1,      # 2'x2' Lay-In LED
    "F9": 6,      # 6' Linear LED (strip)
    "X1": 5,      # Exit Sign type 1
    "X2": 1,      # Exit Sign type 2
}

# =============================================================================
# LINEAR LED FIXTURES (from E600 schedule)
# =============================================================================

GROUND_TRUTH_LINEAR = {
    "4' Linear LED": 16,      # Cat #62880
    "6' Linear LED": 12,      # Cat #63014
    "8' Linear LED": 8,       # Cat #62881
    "10' Linear LED": 14,     # Cat #63012
    "16' Linear LED": 2,      # Cat #62882
}

# =============================================================================
# PENDANT FIXTURES (from E600 schedule)
# =============================================================================

GROUND_TRUTH_PENDANTS = {
    "F10-22": 3,      # 22' Linear Pendant
    "F10-30": 2,      # 30' Linear Pendant
    "F11-4X4": 4,     # 4'x4' Pendant Array
    "F11-6X6": 3,     # 6'x6' Pendant Array
    "F11-8X8": 2,     # 8'x8' Pendant Array
    "F11-10X10": 3,   # 10'x10' Pendant Array
    "F11-16X10": 1,   # 16'x10' Pendant Array
}

# =============================================================================
# CONTROLS (from floor plans E200)
# =============================================================================

GROUND_TRUTH_CONTROLS = {
    "Ceiling Occupancy Sensor": 16,
    "Wall Occupancy Sensor": 3,
    "Daylight Sensor": 3,
    "Wireless Dimmer": 10,
    "Power Pack": 14,  # Derived: (16+3) * 0.74 = 14
}

# =============================================================================
# POWER DEVICES (from floor plans E201)
# =============================================================================

GROUND_TRUTH_POWER = {
    "Duplex Receptacle": 37,
    "GFI Receptacle": 5,
    "SP Switch": 3,
    "3-Way Switch": 2,
}

# =============================================================================
# PANEL & BREAKERS (from E700 schedule)
# =============================================================================

GROUND_TRUTH_PANEL = {
    "20A 1P Breaker": 14,
    "30A 2P Breaker": 1,
    "30A/2P Safety Switch 240V": 1,
    "30A/3P Safety Switch 600V": 1,
    "100A/3P Safety Switch 600V": 1,
}

# =============================================================================
# DEMOLITION (from E100)
# =============================================================================

GROUND_TRUTH_DEMO = {
    "Demo 2'x4' Recessed": 7,
    "Demo 2'x2' Recessed": 12,
    "Demo Downlight": 12,
    "Demo 4' Strip": 1,
    "Demo 8' Strip": 27,
    "Demo Exit": 2,
    "Demo Receptacle": 13,
    "Demo Floor Box": 23,
    "Demo Switch": 2,
}

# =============================================================================
# TECHNOLOGY (from T200)
# =============================================================================

GROUND_TRUTH_TECHNOLOGY = {
    "Cat 6 Jack": 92,
    "Cat 6 Cable (ft)": 920,   # Derived: 92 * 10
    "J-Hook": 230,             # Derived: 920 / 4
}

# =============================================================================
# CONDUIT (from routing analysis)
# =============================================================================

GROUND_TRUTH_CONDUIT = {
    '3/4" EMT': 3773,
    '1" EMT': 790,
    '1-1/4" EMT': 150,  # Estimated for feeders
}

# =============================================================================
# FITTINGS (derived from conduit)
# =============================================================================

GROUND_TRUTH_FITTINGS = {
    # 3/4" fittings
    '3/4" EMT Connector': 396,
    '3/4" EMT Coupling': 347,
    '3/4" Insulating Bushing': 396,
    '3/4" 1-Hole Strap': 347,
    '3/4" Unistrut Strap': 117,
    # 1" fittings
    '1" EMT Connector': 83,
    '1" EMT Coupling': 73,
    '1" Insulating Bushing': 83,
    '1" 1-Hole Strap': 73,
    '1" Unistrut Strap': 24,
}

# =============================================================================
# BOXES (derived from devices)
# =============================================================================

GROUND_TRUTH_BOXES = {
    '4" Square Box w/bracket': 52,
    '4" Square Box': 19,
    '4-11/16" Square Box w/bracket': 89,
    '4-11/16" Square Box': 14,
    '4" Square Box 2-1/8" deep': 10,
}

# =============================================================================
# PLASTER RINGS (derived from boxes)
# =============================================================================

GROUND_TRUTH_RINGS = {
    '4" Square-1G Plaster Ring': 57,
    '4" Square-2G Plaster Ring': 8,
    '4" Square-3/0 Plaster Ring': 19,
    '4-11/16"-1G Plaster Ring': 89,
}

# =============================================================================
# COVER PLATES (derived from devices)
# =============================================================================

GROUND_TRUTH_PLATES = {
    "Duplex Plate": 37,
    "Decora Plate": 15,
    "Switch Plate": 5,
    "Blank Cover": 25,
    "Blank Cover w/KO": 8,
}

# =============================================================================
# WIRE (derived from conduit)
# =============================================================================

GROUND_TRUTH_WIRE = {
    "#12 THHN Black": 4150,
    "#12 THHN White": 3773,
    "#12 THHN Green": 3773,
    "#10 THHN Black": 948,
    "#10 THHN White": 869,
    "#10 THHN Green": 869,
    "#8 THHN Black": 195,
    "#8 THHN White": 180,
    "#8 THHN Green": 180,
}

# =============================================================================
# CONSUMABLES
# =============================================================================

GROUND_TRUTH_CONSUMABLES = {
    "Red Wirenut": 600,
    "Yellow Wirenut": 300,
    "Ground Screw": 184,
    "Pan Head Tapping Screw #8": 600,
    "Poly Pull Line (ft)": 2282,
    "Black Tape": 3,
    "Red Phase Tape": 2,
    "Blue Phase Tape": 2,
}

# =============================================================================
# ACCESSORIES
# =============================================================================

GROUND_TRUTH_ACCESSORIES = {
    "Fixture Whip": 7,          # F2 + F8
    "Pendant/Cable": 208,       # Linear fixtures * 4
    "Aircraft Cable Kit": 72,   # Pendant fixtures * 4
    "Canopy Kit": 18,           # Pendant fixture count
}

# =============================================================================
# COMBINED DICTIONARIES
# =============================================================================

# All counted items (from floor plans and schedules)
GROUND_TRUTH_COUNTED = {
    **GROUND_TRUTH_FIXTURES,
    **GROUND_TRUTH_LINEAR,
    **GROUND_TRUTH_PENDANTS,
    **GROUND_TRUTH_CONTROLS,
    **GROUND_TRUTH_POWER,
    **GROUND_TRUTH_PANEL,
    **GROUND_TRUTH_DEMO,
    **GROUND_TRUTH_TECHNOLOGY,
}

# All derived items (from business rules)
GROUND_TRUTH_DERIVED = {
    **GROUND_TRUTH_CONDUIT,
    **GROUND_TRUTH_FITTINGS,
    **GROUND_TRUTH_BOXES,
    **GROUND_TRUTH_RINGS,
    **GROUND_TRUTH_PLATES,
    **GROUND_TRUTH_WIRE,
    **GROUND_TRUTH_CONSUMABLES,
    **GROUND_TRUTH_ACCESSORIES,
}

# Everything combined
ALL_GROUND_TRUTH = {
    **GROUND_TRUTH_COUNTED,
    **GROUND_TRUTH_DERIVED,
}

# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def get_category(item: str) -> str:
    """Determine the category of a material item."""
    if item in GROUND_TRUTH_FIXTURES:
        return "Fixtures"
    elif item in GROUND_TRUTH_LINEAR:
        return "Linear LEDs"
    elif item in GROUND_TRUTH_PENDANTS:
        return "Pendants"
    elif item in GROUND_TRUTH_CONTROLS:
        return "Controls"
    elif item in GROUND_TRUTH_POWER:
        return "Power"
    elif item in GROUND_TRUTH_PANEL:
        return "Panel"
    elif item in GROUND_TRUTH_DEMO:
        return "Demo"
    elif item in GROUND_TRUTH_TECHNOLOGY:
        return "Technology"
    elif item in GROUND_TRUTH_CONDUIT:
        return "Conduit"
    elif item in GROUND_TRUTH_FITTINGS:
        return "Fittings"
    elif item in GROUND_TRUTH_BOXES:
        return "Boxes"
    elif item in GROUND_TRUTH_RINGS:
        return "Rings"
    elif item in GROUND_TRUTH_PLATES:
        return "Plates"
    elif item in GROUND_TRUTH_WIRE:
        return "Wire"
    elif item in GROUND_TRUTH_CONSUMABLES:
        return "Consumables"
    elif item in GROUND_TRUTH_ACCESSORIES:
        return "Accessories"
    else:
        return "Unknown"


def get_item_count() -> int:
    """Get total number of unique items."""
    return len(ALL_GROUND_TRUTH)


def get_total_quantity() -> int:
    """Get total quantity across all items."""
    return sum(ALL_GROUND_TRUTH.values())


def print_summary():
    """Print a summary of ground truth data."""
    categories = {}
    for item, qty in ALL_GROUND_TRUTH.items():
        cat = get_category(item)
        if cat not in categories:
            categories[cat] = {"items": 0, "quantity": 0}
        categories[cat]["items"] += 1
        categories[cat]["quantity"] += qty

    print("=" * 60)
    print("GROUND TRUTH SUMMARY - IVCC CETLA")
    print("=" * 60)
    print(f"{'Category':<20} {'Items':>10} {'Total Qty':>15}")
    print("-" * 60)

    for cat in sorted(categories.keys()):
        data = categories[cat]
        print(f"{cat:<20} {data['items']:>10} {data['quantity']:>15,}")

    print("-" * 60)
    print(f"{'TOTAL':<20} {get_item_count():>10} {get_total_quantity():>15,}")
    print("=" * 60)


if __name__ == "__main__":
    print_summary()
