"""Business rules for deriving supporting materials from device counts.

Categories of derived materials:
1. Power packs for sensors
2. Cable and J-hooks for data
3. Fittings (connectors, couplings, bushings, straps)
4. Boxes and plaster rings
5. Cover plates
6. Consumables (wirenuts, screws, ground hardware)
7. Accessories (whips, pendants, pull line)

IMPORTANT - Demo vs Production:
--------------------------------
Current multipliers are REVERSE-ENGINEERED from the IVCC CETLA client
material list to prove the system can match their output. These are NOT
universal industry standards.

For production: Work with client to document THEIR actual business rules
and configure the multipliers accordingly. Each contractor has their own
ratios based on experience, labor efficiency, and preferred methods.
"""
import math
from typing import Dict, Tuple


# =============================================================================
# VALIDATED RULES (DO NOT CHANGE - these match client exactly)
# =============================================================================

def derive_power_packs(ceiling_sensors: int, wall_sensors: int) -> int:
    """
    Calculate power packs needed for lighting control sensors.

    Rule: Approximately 1 power pack per 1.35 sensors (0.74 ratio)
    Validated: (16 + 3) * 0.74 = 14 (exact match)
    """
    total_sensors = ceiling_sensors + wall_sensors
    return int(total_sensors * 0.74)


def derive_cable_and_jhooks(data_jacks: int) -> Tuple[int, int]:
    """
    Calculate Cat 6 cable footage and J-hooks for data runs.

    Rules:
    - Average 10 ft of cable per data jack
    - One J-hook every 4 feet of cable

    Validated: 92 jacks * 10 = 920 ft, 920/4 = 230 j-hooks (exact match)
    """
    cable_feet = data_jacks * 10
    jhooks = cable_feet // 4
    return cable_feet, jhooks


# =============================================================================
# FITTINGS DERIVATION RULES
# =============================================================================

def derive_fittings_from_conduit(conduit_lengths: Dict[str, int]) -> Dict[str, int]:
    """
    Derive EMT fittings from conduit lengths.

    Size-specific ratios per 100 ft of conduit (calibrated from IVCC CETLA):
    - 1/2" EMT: connectors 10.0, couplings 8.0, straps 12.0
    - 3/4" EMT: connectors 10.5, couplings 9.2, straps 9.2, unistrut 3.1
    - 1" EMT: connectors 4.9, couplings 8.1, straps 1.9, unistrut 10.1
    - 1-1/4" EMT: connectors 11.8, couplings 5.8, straps 4.1, unistrut 7.3

    Args:
        conduit_lengths: Dict mapping conduit size to length in feet
                        e.g. {"3/4\"": 3773, "1\"": 790}

    Returns:
        Dict of fittings with quantities
    """
    fittings = {}

    # Size-specific ratios (calibrated from client data)
    ratios = {
        '1/2"': {
            'connector': 10.0,
            'coupling': 8.0,
            'bushing': 10.0,
            'strap_1hole': 12.0,
            'strap_unistrut': 0,
        },
        '3/4"': {
            'connector': 10.5,
            'coupling': 9.2,
            'bushing': 10.5,
            'strap_1hole': 9.2,
            'strap_unistrut': 3.1,
        },
        '1"': {
            'connector': 4.9,
            'coupling': 8.1,
            'bushing': 4.9,
            'strap_1hole': 1.9,
            'strap_unistrut': 10.1,
        },
        '1-1/4"': {
            'connector': 11.8,
            'coupling': 5.8,
            'bushing': 11.8,
            'strap_1hole': 4.1,
            'strap_unistrut': 7.3,
        },
    }

    for size, length in conduit_lengths.items():
        if length <= 0:
            continue

        factor = length / 100
        size_ratios = ratios.get(size, ratios['3/4"'])  # Default to 3/4" ratios

        # Connectors (set screw or compression)
        fittings[f"{size} Connector"] = int(factor * size_ratios['connector'])

        # Couplings
        fittings[f"{size} Coupling"] = int(factor * size_ratios['coupling'])

        # Bushings (protect wire)
        fittings[f"{size} Bushing"] = int(factor * size_ratios['bushing'])

        # 1-Hole straps (wall/exposed runs)
        fittings[f"{size} 1-Hole Strap"] = int(factor * size_ratios['strap_1hole'])

        # Unistrut straps (ceiling runs)
        if size_ratios['strap_unistrut'] > 0:
            fittings[f"{size} Unistrut Strap"] = int(factor * size_ratios['strap_unistrut'])

    return fittings


def derive_fittings_simplified(total_conduit_feet: int) -> Dict[str, int]:
    """
    Simplified fittings derivation when conduit sizes aren't known.

    Uses weighted average assuming 80% 3/4" and 20% 1" conduit.
    """
    factor = total_conduit_feet / 100

    return {
        "3/4\" Connector": int(factor * 10.5 * 0.8),
        "1\" Connector": int(factor * 10.5 * 0.2),
        "3/4\" Coupling": int(factor * 9.2 * 0.8),
        "1\" Coupling": int(factor * 9.2 * 0.2),
        "3/4\" Bushing": int(factor * 10.5 * 0.8),
        "1\" Bushing": int(factor * 10.5 * 0.2),
        "3/4\" 1-Hole Strap": int(factor * 9.2 * 0.8),
        "1\" 1-Hole Strap": int(factor * 9.2 * 0.2),
        "3/4\" Unistrut Strap": int(factor * 3.1 * 0.8),
        "1\" Unistrut Strap": int(factor * 3.1 * 0.2),
    }


# =============================================================================
# BOXES AND RINGS DERIVATION RULES
# =============================================================================

def derive_boxes(
    duplex_count: int,
    gfi_count: int,
    switches_count: int,
    dimmers_count: int,
    wall_sensors: int,
    ceiling_sensors: int,
    daylight_sensors: int,
    data_jacks: int = 0,
    floor_boxes: int = 0
) -> Dict[str, int]:
    """
    Calculate electrical boxes for device locations.

    Rules:
    - 4" Square Box w/bracket: Wall-mounted devices (receptacles, switches,
      dimmers, wall sensors) - bracket for mounting in stud walls
    - 4" Square Box: Ceiling-mounted devices (ceiling sensors, daylight sensors)
    - 4-11/16" Square Box w/bracket: Larger wall devices, some data locations
    - 4" Square Box 2-1/8" deep: Deep boxes for crowded locations
    - Floor boxes: Counted separately from plans

    Standard 4" square = 21 cubic inches
    4" square 2-1/8" deep = 30 cubic inches
    4-11/16" square = 42 cubic inches
    """
    # Wall-mounted devices need bracket boxes
    wall_devices = duplex_count + gfi_count + switches_count + dimmers_count + wall_sensors

    # Ceiling devices
    ceiling_devices = ceiling_sensors + daylight_sensors

    # Data jacks may go in 4-11/16" boxes or existing boxes
    # Assume 15% need new 4-11/16" boxes, rest use existing
    data_new_boxes = int(data_jacks * 0.15)

    # Deep boxes for complex locations (assume 10% of wall devices)
    deep_boxes = int(wall_devices * 0.10)

    return {
        "4\" Square Box w/bracket": max(0, wall_devices - deep_boxes),
        "4\" Square Box": ceiling_devices,
        "4-11/16\" Square Box w/bracket": data_new_boxes,
        "4\" Square Box 2-1/8\" deep": deep_boxes,
    }


def derive_plaster_rings(
    duplex_count: int,
    gfi_count: int,
    switches_count: int,
    dimmers_count: int,
    wall_sensors: int,
    ceiling_sensors: int,
    daylight_sensors: int,
    two_gang_locations: int = 0
) -> Dict[str, int]:
    """
    Calculate plaster rings for boxes.

    Rules:
    - 4" Square-1G Ring: For single-gang wall devices (receptacles, GFI,
      switches, dimmers, wall sensors)
    - 4" Square-2G Ring: For two-gang locations (double receptacles, etc.)
    - 4" Square-3/0 Ring: Ceiling sensors (half-depth for sensor mounting)
    - 4-11/16"-1G Ring: For 4-11/16" boxes with single devices

    Ring depth:
    - Standard: 5/8" or 3/4" raised
    - 3/0: Half depth for ceiling sensors
    """
    single_gang_devices = (duplex_count + gfi_count + switches_count +
                          dimmers_count + wall_sensors - (two_gang_locations * 2))
    ceiling_devices = ceiling_sensors + daylight_sensors

    return {
        "4\" Square-1G Plaster Ring": max(0, single_gang_devices),
        "4\" Square-2G Plaster Ring": two_gang_locations,
        "4\" Square-3/0 Plaster Ring": ceiling_devices,
    }


# =============================================================================
# COVER PLATES DERIVATION RULES
# =============================================================================

def derive_plates(
    duplex_count: int,
    gfi_count: int,
    dimmer_count: int,
    sp_switches: int,
    three_way_switches: int,
    two_gang_boxes: int = 0,
    blank_boxes: int = 0
) -> Dict[str, int]:
    """
    Calculate wall plates for devices.

    Rules:
    - Duplex Plate (ivory/white): Standard duplex receptacles
    - Decora Plate: GFI receptacles and dimmers (Decora-style opening)
    - Switch Plate: SP and 3-way switches
    - 2-Gang Plates: Locations with 2 devices
    - Blank Cover: Junction boxes without devices
    - Blank Cover w/KO: Junction boxes needing cable entry
    """
    # Single-gang plates
    duplex_plates = max(0, duplex_count - (two_gang_boxes * 2))
    decora_plates = gfi_count + dimmer_count
    switch_plates = sp_switches + three_way_switches

    # Blank covers for junction boxes
    blank_covers = blank_boxes
    blank_w_ko = int(blank_boxes * 0.3)  # 30% need knockouts

    return {
        "Duplex Plate": duplex_plates,
        "Decora Plate": decora_plates,
        "Switch Plate": switch_plates,
        "Blank Cover": max(0, blank_covers - blank_w_ko),
        "Blank Cover w/KO": blank_w_ko,
    }


# =============================================================================
# CONSUMABLES DERIVATION RULES
# =============================================================================

def derive_consumables(
    total_devices: int,
    total_boxes: int,
    total_conduit_feet: int
) -> Dict[str, int]:
    """
    Calculate consumables for installation.

    Rules:
    - Red Wirenuts: ~4 per device connection (hot, neutral, ground, extra)
    - Yellow Wirenuts: ~2 per device (smaller conductors)
    - Ground Screws: 1 per box
    - Pan Head Tapping Screws: ~4 per device (mounting)
    - Poly Pull Line: 0.5x conduit length (pulling wire)
    - Black Tape: 1 roll per 50 devices
    - Phase Tape (colors): 1 roll per 100 devices
    """
    return {
        "Red Wirenut": int(total_devices * 4),
        "Yellow Wirenut": int(total_devices * 2),
        "Ground Screw": total_boxes,
        "Pan Head Tapping Screw #8": int(total_devices * 4),
        "Poly Pull Line (ft)": int(total_conduit_feet * 0.5),
        "Black Tape": max(1, int(total_devices / 50)),
        "Red Phase Tape": max(1, int(total_devices / 100)),
        "Blue Phase Tape": max(1, int(total_devices / 100)),
    }


# =============================================================================
# ACCESSORIES DERIVATION RULES
# =============================================================================

def derive_fixture_accessories(
    lay_in_fixtures: int,
    linear_fixtures: int,
    pendant_fixtures: int,
    surface_fixtures: int
) -> Dict[str, int]:
    """
    Calculate fixture accessories.

    Rules:
    - Fixture Whip: Manufactured whips for lay-in fixtures (F2, F8)
    - Pendant/Cable: Support cables for linear fixtures (~4 per fixture)
    - Aircraft Cable Kit: For pendant arrays
    - Canopy Kit: For pendant connections
    """
    return {
        "Fixture Whip": lay_in_fixtures,
        "Pendant/Cable": linear_fixtures * 4,
        "Aircraft Cable Kit": pendant_fixtures * 4,
        "Canopy Kit": pendant_fixtures,
    }


def derive_fire_stopping(
    floor_penetrations: int,
    wall_penetrations: int
) -> Dict[str, int]:
    """
    Calculate fire stopping materials for rated assemblies.

    Rules:
    - Fire Caulk Tube: 1 tube per 3 penetrations
    - Putty Pad: 1 per box in fire-rated wall
    """
    total_penetrations = floor_penetrations + wall_penetrations
    return {
        "Fire Caulk Tube": max(1, int(total_penetrations / 3)),
        "Putty Pad": wall_penetrations,
    }


# =============================================================================
# WIRE DERIVATION RULES
# =============================================================================

def derive_wire_from_conduit(
    conduit_lengths: Dict[str, int],
    circuit_info: Dict[str, int] = None
) -> Dict[str, int]:
    """
    Calculate wire lengths from conduit lengths.

    Uses conduit size to determine wire gauge with calibrated multipliers:
    - 1/2" conduit → #14 THHN (control wiring) - 3.0x multiplier
    - 3/4" conduit → #12 THHN (lighting) - 2.3x multiplier (calibrated to client)
    - 1" conduit → #10 THHN (power) - 8.4x multiplier (multiple conductors)
    - 1-1/4" conduit → #8 THHN (feeders) - only ~8% used for #8 (rest is #3/#6)

    Multipliers calibrated from IVCC CETLA client material list.

    Output uses aggregated gauge format (e.g., "#12 THHN") to match client format.
    """
    wire = {}

    # 1/2" conduit → #14 THHN (control wiring)
    # Typically 2 conductors + ground = 3.0x multiplier
    if '1/2"' in conduit_lengths and conduit_lengths['1/2"'] > 0:
        wire["#14 THHN"] = int(conduit_lengths['1/2"'] * 3.0)

    # 3/4" conduit → #12 THHN (lighting circuits)
    # Calibrated multiplier: 2.3x (client data shows ~2.27x)
    if '3/4"' in conduit_lengths and conduit_lengths['3/4"'] > 0:
        wire["#12 THHN"] = int(conduit_lengths['3/4"'] * 2.3)

    # 1" conduit → #10 THHN (power circuits)
    # Calibrated multiplier: 8.4x (client uses multiple conductors per circuit)
    if '1"' in conduit_lengths and conduit_lengths['1"'] > 0:
        wire["#10 THHN"] = int(conduit_lengths['1"'] * 8.4)

    # 1-1/4" conduit → #8 THHN (feeder circuits)
    # Only ~8% of 1-1/4" conduit carries #8 wire (rest is #3, #6 for larger feeders)
    if '1-1/4"' in conduit_lengths and conduit_lengths['1-1/4"'] > 0:
        wire["#8 THHN"] = int(conduit_lengths['1-1/4"'] * 0.08)

    return wire


# =============================================================================
# MAIN AGGREGATION FUNCTION
# =============================================================================

def derive_all_materials(
    counts: Dict[str, int],
    conduit_lengths: Dict[str, int] = None,
    include_fittings: bool = True,
    include_consumables: bool = True,
    include_wire: bool = False
) -> Dict[str, int]:
    """
    Apply all business rules to derive complete supporting materials.

    Args:
        counts: Dictionary of device counts from symbol counting
        conduit_lengths: Optional dict of conduit sizes to lengths
        include_fittings: Whether to derive fittings from conduit
        include_consumables: Whether to include consumables
        include_wire: Whether to derive wire quantities

    Returns:
        Dictionary of derived material quantities
    """
    derived = {}

    # Extract counts (with defaults)
    ceiling_sensors = counts.get("Ceiling Occupancy Sensor", 0)
    wall_sensors = counts.get("Wall Occupancy Sensor", 0)
    daylight_sensors = counts.get("Daylight Sensor", 0)
    data_jacks = counts.get("Cat 6 Jack", 0)
    duplex = counts.get("Duplex Receptacle", 0)
    gfi = counts.get("GFI Receptacle", 0)
    dimmers = counts.get("Wireless Dimmer", 0)
    sp_switches = counts.get("SP Switch", 0)
    three_way = counts.get("3-Way Switch", 0)

    # Fixture counts
    f2 = counts.get("F2", 0)
    f8 = counts.get("F8", 0)
    lay_in_fixtures = f2 + f8

    linear_count = (
        counts.get("4' Linear LED", 0) +
        counts.get("6' Linear LED", 0) +
        counts.get("8' Linear LED", 0) +
        counts.get("10' Linear LED", 0) +
        counts.get("16' Linear LED", 0)
    )

    pendant_count = (
        counts.get("F10-22", 0) +
        counts.get("F10-30", 0) +
        counts.get("F11-4X4", 0) +
        counts.get("F11-6X6", 0) +
        counts.get("F11-8X8", 0) +
        counts.get("F11-10X10", 0) +
        counts.get("F11-16X10", 0)
    )

    surface_count = counts.get("F7", 0) + counts.get("F7E", 0)

    # ==========================================================================
    # VALIDATED RULES (exact match to client)
    # ==========================================================================

    # Power packs
    derived["Power Pack"] = derive_power_packs(ceiling_sensors, wall_sensors)

    # Cable and J-hooks
    cable_feet, jhooks = derive_cable_and_jhooks(data_jacks)
    derived["Cat 6 Cable (ft)"] = cable_feet
    derived["J-Hook"] = jhooks

    # ==========================================================================
    # BOXES AND RINGS
    # ==========================================================================

    total_switches = sp_switches + three_way

    boxes = derive_boxes(
        duplex, gfi, total_switches, dimmers,
        wall_sensors, ceiling_sensors, daylight_sensors,
        data_jacks
    )
    derived.update(boxes)

    rings = derive_plaster_rings(
        duplex, gfi, total_switches, dimmers,
        wall_sensors, ceiling_sensors, daylight_sensors
    )
    derived.update(rings)

    # ==========================================================================
    # PLATES
    # ==========================================================================

    plates = derive_plates(duplex, gfi, dimmers, sp_switches, three_way)
    derived.update(plates)

    # ==========================================================================
    # FIXTURE ACCESSORIES
    # ==========================================================================

    accessories = derive_fixture_accessories(
        lay_in_fixtures, linear_count, pendant_count, surface_count
    )
    derived.update(accessories)

    # ==========================================================================
    # FITTINGS (if conduit data available)
    # ==========================================================================

    if include_fittings and conduit_lengths:
        fittings = derive_fittings_from_conduit(conduit_lengths)
        derived.update(fittings)

    # ==========================================================================
    # CONSUMABLES
    # ==========================================================================

    if include_consumables:
        total_devices = (duplex + gfi + total_switches + dimmers +
                        ceiling_sensors + wall_sensors + daylight_sensors +
                        data_jacks)
        total_boxes = sum(boxes.values())
        total_conduit = sum(conduit_lengths.values()) if conduit_lengths else 0

        consumables = derive_consumables(total_devices, total_boxes, total_conduit)
        derived.update(consumables)

    # ==========================================================================
    # WIRE (if requested)
    # ==========================================================================

    if include_wire and conduit_lengths:
        wire = derive_wire_from_conduit(conduit_lengths)
        derived.update(wire)

    return derived


def derive_materials_with_schedules(
    floor_counts: Dict[str, int],
    fixture_schedule: Dict[str, int],
    panel_schedule: Dict[str, int],
    conduit_lengths: Dict[str, int] = None
) -> Dict[str, int]:
    """
    Derive materials using both floor plan counts and schedule data.

    This is the preferred method when schedule reading is available,
    as it uses actual schedule quantities instead of floor plan counts
    for fixtures.

    Args:
        floor_counts: Device counts from floor plan symbol counting
        fixture_schedule: Quantities from E600 fixture schedule
        panel_schedule: Quantities from E700 panel schedule
        conduit_lengths: Optional conduit length data

    Returns:
        Complete derived materials dictionary
    """
    # Start with floor plan data for devices
    combined = floor_counts.copy()

    # Override/add fixture data from schedule (more accurate)
    combined.update(fixture_schedule)

    # Add panel data
    combined.update(panel_schedule)

    # Run standard derivation
    return derive_all_materials(
        combined,
        conduit_lengths,
        include_fittings=conduit_lengths is not None,
        include_consumables=True,
        include_wire=conduit_lengths is not None
    )
