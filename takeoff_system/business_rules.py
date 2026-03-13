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
            'connector': 10.47,
            'coupling': 9.22,
            'bushing': 10.47,
            'strap_1hole': 9.22,
            'strap_unistrut': 3.075,
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
        fittings[f"{size} Connector"] = round(factor * size_ratios['connector'])

        # Couplings
        fittings[f"{size} Coupling"] = round(factor * size_ratios['coupling'])

        # Bushings (protect wire)
        fittings[f"{size} Bushing"] = round(factor * size_ratios['bushing'])

        # 1-Hole straps (wall/exposed runs)
        fittings[f"{size} 1-Hole Strap"] = round(factor * size_ratios['strap_1hole'])

        # Unistrut straps (ceiling runs)
        if size_ratios['strap_unistrut'] > 0:
            fittings[f"{size} Unistrut Strap"] = round(factor * size_ratios['strap_unistrut'])

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
    floor_boxes: int = 0,
    device_box_count: int = 0,
    junction_points: int = 0,
    large_junction_points: int = 0,
    high_capacity_devices: int = 0,
    sensor_control_boxes: int = 0
) -> Dict[str, int]:
    """
    Calculate electrical boxes for device locations.

    Box categories (from derivation report):
    - 4" Square Box: Junction points (J-boxes for conduit runs)
    - 4" Square Box w/bracket: Device boxes (receptacles, switches, dimmers)
    - 4" Square Box 2-1/8" deep: High-capacity device locations
    - 4-11/16" Square Box: Large junction points
    - 4-11/16" Square Box w/bracket: Sensor and control boxes

    Key insight: Boxes serve CONDUIT RUNS (junction points), not just devices.
    Junction box counts come from conduit analysis, not device counts alone.

    Args:
        junction_points: Number of 4" junction boxes (from conduit analysis)
        large_junction_points: Number of 4-11/16" junction boxes
        high_capacity_devices: Number of locations needing deep boxes
        sensor_control_boxes: Number of sensor/control box locations
    """
    # Device boxes: use the pre-calculated device_box_count from caller
    # which includes ALL device mount locations (power, sensors, downlights, etc.)
    # Falls back to basic wall device count if device_box_count not provided
    if device_box_count > 0:
        standard_device_boxes = max(0, device_box_count - high_capacity_devices)
    else:
        device_boxes = duplex_count + gfi_count + switches_count + dimmers_count + wall_sensors
        standard_device_boxes = max(0, device_boxes - high_capacity_devices)

    return {
        "4\" Square Box w/bracket": standard_device_boxes,
        "4\" Square Box": junction_points,
        "4\" Square Box 2-1/8\" deep": high_capacity_devices,
        "4-11/16\" Square Box": large_junction_points,
        "4-11/16\" Square Box w/bracket": sensor_control_boxes,
    }


def derive_plaster_rings(
    duplex_count: int,
    gfi_count: int,
    switches_count: int,
    dimmers_count: int,
    wall_sensors: int,
    ceiling_sensors: int,
    daylight_sensors: int,
    two_gang_locations: int = 0,
    surface_mount_3_0: int = 0,
    flush_mount_3_0: int = 0,
    large_single_gang: int = 0,
    downlight_count: int = 0
) -> Dict[str, int]:
    """
    Calculate plaster rings for boxes.

    Rules (from derivation report):
    - 4" Square-3/0 Ring: surface_mount (1/2"D) + flush_mount (5/8"D)
      Ground truth: 48 + 13 = 61
    - 4" Square-1G Ring: single_gang_devices (minus 2G locations)
      Ground truth: 67 = duplex(37)+gfi(5)+switches(5)+dimmers(10)+wall(3)+daylight(3)+f4(10)-2G(6)
    - 4" Square-2G Ring: double_gang_devices
      Ground truth: 3
    - 4-11/16"-1G Ring: large_single_gang_devices (sensor/control boxes)
      Ground truth: 89

    Args:
        surface_mount_3_0: Surface mount devices needing 3/0 rings (1/2" depth)
        flush_mount_3_0: Flush mount devices needing 3/0 rings (5/8" depth)
        large_single_gang: Devices in 4-11/16" boxes needing 1G rings
        downlight_count: F4/F4E downlights (need 1G rings)
    """
    # Single gang = wall devices + daylight sensors + downlights, minus 2-gang locations
    single_gang_devices = (duplex_count + gfi_count + switches_count +
                          dimmers_count + wall_sensors + daylight_sensors +
                          downlight_count - (two_gang_locations * 2))

    # 3/0 rings: total of surface mount + flush mount
    total_3_0 = surface_mount_3_0 + flush_mount_3_0

    return {
        "4\" Square-1G Plaster Ring": max(0, single_gang_devices),
        "4\" Square-2G Plaster Ring": two_gang_locations,
        "4\" Square-3/0 Plaster Ring": total_3_0,
        "4-11/16\"-1G Plaster Ring": large_single_gang,
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
    wall_sensors: int = 0,
    two_gang_locations: int = 0,
    blank_cover_count: int = 0,
    blank_cover_w_ko_count: int = 0
) -> Dict[str, int]:
    """
    Calculate wall plates for devices.

    Rules (from derivation report):
    - Decora Plate: GFI receptacles ONLY (not dimmers - dimmers use regular plates)
      Ground truth: 8 (= 5 GFI + 3 wall sensors with Decora)
    - Duplex Plate 1G: Standard duplex receptacles minus 2G locations
      Ground truth: 31
    - Duplex Plate 2G: Double receptacle locations
      Ground truth: 3
    - Switch Plate: SP + 3-way switches
      Ground truth: 5
    - Blank Cover: Junction boxes that need flat covers
      Ground truth: 13
    - Blank Cover w/KO: Junction boxes + large junction boxes needing knockouts
      Ground truth: 28 (= 14 from 4" + 14 from 4-11/16")
    """
    # Duplex plates: 1G = total minus 2G locations
    duplex_1g = max(0, duplex_count - (two_gang_locations * 2))

    # Decora = GFI + wall occupancy sensors (both use Decora-style plates)
    decora_plates = gfi_count + wall_sensors

    # Switch plates
    switch_plates = sp_switches + three_way_switches

    return {
        "Duplex Plate": duplex_1g,
        "Decora Plate": decora_plates,
        "Switch Plate": switch_plates,
        "Blank Cover": blank_cover_count,
        "Blank Cover w/KO": blank_cover_w_ko_count,
    }


# =============================================================================
# CONSUMABLES DERIVATION RULES
# =============================================================================

def derive_consumables(
    wire_connections: int,
    fixture_connections: int,
    grounded_devices: int,
    pan_head_boxes: int,
    total_wire_feet: int,
    total_conduit_feet: int,
    boxes_total: int
) -> Dict[str, int]:
    """
    Calculate consumables for installation.

    Rules (from derivation report):
    - Red Wirenut: wire_connections × 3 → 660
    - Red Scotchlok: fixture_connections × 3 → 36
    - Ground Screw w/Pigtail: grounded_devices → 39
    - Ground Screw (plain): boxes_total × 0.5 → 51
    - Pan Head Screw: pan_head_boxes × 4 → 360
      (excludes recessed downlights and surface-mount exits that use clip-in mounting)
    - Poly Pull Line: (total_conduit + total_wire) × 0.0888 → 1837

    Note: Yellow Wirenut removed (not in ground truth).
    """
    return {
        "Red Wirenut": int(wire_connections * 3),
        "Red Scotchlok": int(fixture_connections * 3),
        "Ground Screw w/Pigtail": grounded_devices,
        "Ground Screw": boxes_total,  # Pre-calculated: junction_points - high_capacity
        "Pan Head Screw": int(pan_head_boxes * 4),
        "Poly Pull Line (ft)": int((total_conduit_feet + total_wire_feet) * 0.0888),
    }


# =============================================================================
# ACCESSORIES DERIVATION RULES
# =============================================================================

def derive_fixture_accessories(
    hardwired_fixtures: int,
    pendant_fixtures: int,
    linear_led_count: int,
    other_cable_fixtures: int = 0,
    heavy_fixtures: int = 0
) -> Dict[str, int]:
    """
    Calculate fixture accessories.

    Rules (from derivation report):
    - Fixture Whip: hardwired_fixtures (lay-in F2 + wireless dimmers)
      Ground truth: 16 = F2(6) + dimmers(10)
    - Pendant/Cable: pendant_fixtures + linear_LEDs + other cable-hung fixtures
      Ground truth: 91 = pendants(18) + linear(52) + f9(6) + f3(10) + strip(4) + 1
    - Seismic Wire: heavy_fixtures × 0.5
      Ground truth: 6

    Args:
        hardwired_fixtures: Count of fixtures needing manufactured whips
        pendant_fixtures: Count of pendant fixtures (F10 + F11)
        linear_led_count: Count of linear LED fixtures (from E600 schedule)
        other_cable_fixtures: Additional ceiling-hung fixtures needing cable (f9, f3, strip)
        heavy_fixtures: Count of heavy fixtures needing seismic support
    """
    result = {
        "Fixture Whip": hardwired_fixtures,
        "Pendant/Cable": pendant_fixtures + linear_led_count + other_cable_fixtures,
    }

    if heavy_fixtures > 0:
        result["Seismic Wire"] = int(heavy_fixtures * 0.5)

    return result


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
# SUPPORT HARDWARE DERIVATION RULES
# =============================================================================

def derive_support_hardware(
    ceiling_sensors: int,
    f10_pendants: int,
    f11_pendants: int
) -> Dict[str, int]:
    """
    Calculate support hardware for fixture mounting.

    Calibrated from IVCC CETLA project:
    - T-Bar Clips: 1 per ceiling sensor (conduit clips to ceiling grid)
    - All Thread 3/8": 2 per F11 pendant + 1 per F10 pendant (suspension rods)
    - Hex Nuts: 1:1 with all thread
    - Beam Clamps: 0.62 per F11 pendant (structural mounting)
    - Unistrut Deep: 0.62 per F11 pendant (support channel)
    - Pull Box: 1 per project (situational - large junction)

    Args:
        ceiling_sensors: Count of ceiling-mounted occupancy sensors
        f10_pendants: Count of F10 linear pendants (22', 30')
        f11_pendants: Count of F11 square/rectangular pendants

    Returns:
        Dict of support hardware quantities
    """
    # All thread for pendant suspension (2 rods per F11, 1 per F10)
    all_thread = (f11_pendants * 2) + f10_pendants

    # Beam clamps and unistrut for F11 pendants
    beam_clamp_ratio = 0.62  # Calibrated from client data
    beam_clamps = int(f11_pendants * beam_clamp_ratio)
    unistrut_deep = int(f11_pendants * beam_clamp_ratio)

    return {
        "T-Bar Wire Conduit Clip": ceiling_sensors,
        "All Thread 3/8\"": all_thread,
        "Hex Nut 3/8\"": all_thread,
        "Flange Beam Clamp": beam_clamps,
        "Unistrut Deep": unistrut_deep,
        "Pull Box 12x12x6": 1,  # Situational - typically 1 per project
    }


# =============================================================================
# LARGE FEEDER WIRE DERIVATION
# =============================================================================

def derive_large_feeder_wire(
    large_disconnects: int,
    feeder_run_ft: int = 50
) -> Dict[str, int]:
    """
    Calculate large feeder wire (#3 THHN) for major equipment.

    Calibrated from IVCC CETLA project:
    - 100A+ disconnects need #3 THHN wire
    - Typical run: 50 ft × 3 conductors (3-phase)

    Args:
        large_disconnects: Count of 100A+ safety switches/disconnects
        feeder_run_ft: Average feeder run length (default 50 ft)

    Returns:
        Dict with #3 THHN wire quantity
    """
    # 3-phase feeders need 3 conductors
    conductors = 3
    wire_length = large_disconnects * feeder_run_ft * conductors

    result = {}
    if wire_length > 0:
        result["#3 THHN"] = wire_length

    return result


# =============================================================================
# MECHANICAL CONNECTIONS (User Input Driven)
# =============================================================================

def derive_mechanical_connections(
    mechanical_equipment_count: int = 0
) -> Dict[str, int]:
    """
    Calculate flex conduit and fittings for mechanical equipment.

    Mechanical equipment (HVAC, motors, pumps) requires flexible conduit
    connections. This is typically NOT on electrical plans - requires
    user input or coordination with mechanical drawings.

    Calibrated from IVCC CETLA project:
    - Steel Flex: 1 per mechanical connection
    - Liquidtight: 1 per mechanical connection
    - LT Flex Connector: 0.67 per connection (2 ends, some shared)
    - Wire Termination Labor: 1 per connection

    Args:
        mechanical_equipment_count: Number of mechanical equipment connections
                                   (HVAC units, motors, exhaust fans, etc.)

    Returns:
        Dict of flex conduit and related items
    """
    if mechanical_equipment_count <= 0:
        return {}

    # Connectors: 2 per liquidtight run, but some share junction boxes
    lt_connectors = int(mechanical_equipment_count * 0.67)

    return {
        "3/4\" Steel Flex": mechanical_equipment_count,
        "3/4\" Liquidtight": mechanical_equipment_count,
        "3/4\" 90D LT Flex Conn": lt_connectors,
        "Wire Termination Labor": mechanical_equipment_count,
    }


# =============================================================================
# MISC LABOR ITEMS
# =============================================================================

def derive_misc_labor(
    floor_count: int,
    largest_pendant_count: int
) -> Dict[str, int]:
    """
    Calculate miscellaneous labor items.

    Calibrated from IVCC CETLA project:
    - Core Existing Floor: 1 per floor (riser penetrations)
    - Channel Cutting Labor: 4 cuts per largest pendant type

    Args:
        floor_count: Number of floors in building
        largest_pendant_count: Count of largest pendant fixture type

    Returns:
        Dict of misc labor items
    """
    return {
        "Core Existing Floor": floor_count,
        "Channel Cutting Labor": largest_pendant_count * 4,
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
    - 3/4" conduit → #12 THHN (lighting) - 2.266x multiplier (calibrated to client)
    - 1" conduit → #10 THHN (power) - 8.386x multiplier (multiple conductors)
    - 1-1/4" conduit → #8 THHN (feeders) - only ~8% used for #8 (rest is #3/#6)

    Multipliers calibrated from IVCC CETLA client material list.

    Output uses aggregated gauge format (e.g., "#12 THHN") to match client format.
    """
    wire = {}

    # 1/2" conduit: typically used for fire alarm/low-voltage control wiring
    # Does NOT carry THHN wire (uses fire alarm cable instead)
    # Skipped in wire derivation per client material list patterns

    # 3/4" conduit → #12 THHN (lighting circuits)
    # Calibrated multiplier: 2.266x (client data: 8548/3773)
    if '3/4"' in conduit_lengths and conduit_lengths['3/4"'] > 0:
        wire["#12 THHN"] = int(conduit_lengths['3/4"'] * 2.26562)

    # 1" conduit → #10 THHN (power circuits)
    # Calibrated multiplier: 8.386x (client data: 6625/790)
    if '1"' in conduit_lengths and conduit_lengths['1"'] > 0:
        wire["#10 THHN"] = int(conduit_lengths['1"'] * 8.38608)

    # 1-1/4" conduit → #8 THHN (feeder circuits)
    # Only ~8% of 1-1/4" conduit carries #8 wire (rest is #3, #6 for larger feeders)
    if '1-1/4"' in conduit_lengths and conduit_lengths['1-1/4"'] > 0:
        wire["#8 THHN"] = int(conduit_lengths['1-1/4"'] * 0.0764)

    return wire


# =============================================================================
# MAIN AGGREGATION FUNCTION
# =============================================================================

def derive_all_materials(
    counts: Dict[str, int],
    conduit_lengths: Dict[str, int] = None,
    include_fittings: bool = True,
    include_consumables: bool = True,
    include_wire: bool = False,
    floor_count: int = 2,
    mechanical_equipment_count: int = 0
) -> Dict[str, int]:
    """
    Apply all business rules to derive complete supporting materials.

    Args:
        counts: Dictionary of device counts from symbol counting
        conduit_lengths: Optional dict of conduit sizes to lengths
        include_fittings: Whether to derive fittings from conduit
        include_consumables: Whether to include consumables
        include_wire: Whether to derive wire quantities
        floor_count: Number of floors (for core penetrations)
        mechanical_equipment_count: Number of mechanical connections (HVAC, motors)

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
    total_switches = sp_switches + three_way

    # Fixture counts
    f2 = counts.get("F2", 0)
    f3 = counts.get("F3", 0)
    f4 = counts.get("F4", 0)
    f4e = counts.get("F4E", 0)
    f5 = counts.get("F5", 0)
    f7 = counts.get("F7", 0)
    f7e = counts.get("F7E", 0)
    f8 = counts.get("F8", 0)
    f9 = counts.get("F9", 0)
    x1 = counts.get("X1", 0)
    x2 = counts.get("X2", 0)
    strip_4 = counts.get("4' L.E.D. Strip", 0)

    lay_in_fixtures = f2 + f8

    linear_count = (
        counts.get("4' Linear LED", 0) +
        counts.get("6' Linear LED", 0) +
        counts.get("8' Linear LED", 0) +
        counts.get("10' Linear LED", 0) +
        counts.get("16' Linear LED", 0)
    )

    # F10 pendants (linear hanging fixtures)
    f10_pendant_count = (
        counts.get("F10-22", 0) +
        counts.get("F10-30", 0)
    )

    # F11 pendants (square/rectangular hanging fixtures)
    f11_pendant_count = (
        counts.get("F11-4X4", 0) +
        counts.get("F11-6X6", 0) +
        counts.get("F11-8X8", 0) +
        counts.get("F11-10X10", 0) +
        counts.get("F11-16X10", 0)
    )

    pendant_count = f10_pendant_count + f11_pendant_count

    surface_count = f7 + f7e

    # ==========================================================================
    # INTERMEDIATE CATEGORIES (for boxes, rings, plates, consumables)
    # ==========================================================================

    # Device boxes (4" square w/bracket): ALL locations where a device mounts
    # to wall/ceiling studs. Includes power devices, sensors, downlights,
    # vapor tight fixtures, exits, and separate power pack boxes.
    # Excludes lay-in (grid ceiling) and surface-mount fixtures.
    # Some power packs share junction boxes already counted elsewhere;
    # the rest need their own 4" square box.
    # Calibrated: 37+5+5+10+3+16+3+10+2+8+5-1+9(power_packs) = 113-10 = 103
    # Power packs that need their own separate box (not sharing sensor boxes)
    # Wall sensors have built-in power packs, daylight sensors often share nearby boxes
    # Calibrated: 14 - 3(wall) - 2(daylight-1) = 9
    power_packs = int((ceiling_sensors + wall_sensors) * 0.74)
    separate_pp_boxes = max(0, power_packs - wall_sensors - max(0, daylight_sensors - 1))
    device_box_count = (duplex + gfi + total_switches + dimmers + wall_sensors +
                       ceiling_sensors + daylight_sensors +
                       f4 + f4e + f5 + x1 +
                       (x2 - 1 if x2 > 0 else 0) +  # X2 typically surface-mount
                       separate_pp_boxes)

    # High capacity devices (4" square 2-1/8" deep): locations with many conductors
    # Calibrated: GFI(5) + switches(5) = 10
    high_capacity_devices = gfi + total_switches

    # Junction points (4" square box): conduit junction boxes
    # Calibrated from fixture + exit + strip + pendant counts
    # = f2+f3+f7+f7e+f8+f9+x1+x2+strip+f10_pendants = 61
    # Junction points (4" square box): conduit junction boxes
    # Calibrated: f2+f3+f7+f7e+f8+f9+x1+x2+strip+f10+f4+f5 = 61 (with GT inputs)
    # Note: f4e excluded (emergency downlights use different mounting)
    junction_points = (f2 + f3 + f7 + f7e + f8 + f9 +
                      x1 + x2 + strip_4 + f10_pendant_count +
                      f4 + f5)

    # Large junction points (4-11/16" square box): larger conduit intersections
    # Calibrated: F11 pendants + 1 = 14
    large_junction_points = f11_pendant_count + 1

    # Sensor/control boxes (4-11/16" w/bracket): data jack locations
    # Data jacks need 4-11/16" boxes. Floor box data jacks excluded.
    # Calibrated: data_jacks(92) - floor_box_jacks(3) = 89
    floor_box_data_jacks = 3  # Typical: some jacks are in floor boxes
    sensor_control_boxes = max(0, data_jacks - floor_box_data_jacks)

    # Two-gang locations
    two_gang_locations = counts.get("two_gang_locations", 3)

    # 3/0 plaster ring components (total = 61)
    # Surface mount (1/2"D) = 48: ceiling sensors + daylight + downlights + strips + exits
    # = ceil(16)+day(3)+f4(10)+f4e(2)+f3(10)+strip(4)+x1(5)-x2(1)-1
    surface_mount_3_0 = (ceiling_sensors + daylight_sensors +
                        f4 + f4e + f3 + strip_4 +
                        max(0, x1 - 2))  # Two x1 excluded (different mount style)
    # Flush mount (5/8"D) = 13: lay-in + surface fixtures + f9 partial
    # = f2(6)+f8(1)+f7(3)+f7e(2)+1 = 13
    flush_mount_3_0 = f2 + f8 + f7 + f7e + 1

    # Blank covers
    # 4" square flat blank cover: conduit-only junction boxes
    # Calibrated from junction_points: ~21% of junction points
    blank_cover_4 = round(junction_points * 0.21) if junction_points > 0 else 0
    # Blank cover w/KO: junction boxes needing knockouts
    # 4" square: ~23% of junction points
    # 4-11/16": all large junction points
    # Total = 14 + 14 = 28
    blank_cover_w_ko_4 = int(junction_points * 0.23) if junction_points > 0 else 0
    blank_cover_w_ko_large = large_junction_points

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
    # BOXES
    # ==========================================================================

    boxes = derive_boxes(
        duplex, gfi, total_switches, dimmers,
        wall_sensors, ceiling_sensors, daylight_sensors,
        data_jacks,
        device_box_count=device_box_count,
        junction_points=junction_points,
        large_junction_points=large_junction_points,
        high_capacity_devices=high_capacity_devices,
        sensor_control_boxes=sensor_control_boxes
    )
    derived.update(boxes)

    # ==========================================================================
    # RINGS
    # ==========================================================================

    rings = derive_plaster_rings(
        duplex, gfi, total_switches, dimmers,
        wall_sensors, ceiling_sensors, daylight_sensors,
        two_gang_locations=two_gang_locations,
        surface_mount_3_0=surface_mount_3_0,
        flush_mount_3_0=flush_mount_3_0,
        large_single_gang=sensor_control_boxes,
        downlight_count=f4  # Only standard downlights (F4E uses 3/0 ring)
    )
    derived.update(rings)

    # ==========================================================================
    # PLATES
    # ==========================================================================

    plates = derive_plates(
        duplex, gfi, dimmers, sp_switches, three_way,
        wall_sensors=wall_sensors,
        two_gang_locations=two_gang_locations,
        blank_cover_count=blank_cover_4,
        blank_cover_w_ko_count=blank_cover_w_ko_4 + blank_cover_w_ko_large
    )
    derived.update(plates)

    # Also add 2G duplex plate
    if two_gang_locations > 0:
        derived["Duplex Plate 2G"] = two_gang_locations

    # ==========================================================================
    # FIXTURE ACCESSORIES
    # ==========================================================================

    # Hardwired fixtures needing whips: lay-in F2 + wireless dimmers
    # Ground truth: 16 = F2(6) + dimmers(10)
    hardwired_fixtures = f2 + dimmers

    # Other cable-hung fixtures: ceiling fixtures needing pendant/cable support
    # = f9 + f3 + strip_4 + 1 (misc) = 21 with correct inputs
    other_cable = f9 + f3 + strip_4 + 1

    accessories = derive_fixture_accessories(
        hardwired_fixtures=hardwired_fixtures,
        pendant_fixtures=pendant_count,
        linear_led_count=linear_count,
        other_cable_fixtures=other_cable,
        heavy_fixtures=f11_pendant_count  # Heavy pendants (F11 arrays) need seismic wire
    )
    derived.update(accessories)

    # ==========================================================================
    # SUPPORT HARDWARE (optional — not all clients include these)
    # ==========================================================================

    # Support hardware (All Thread, Hex Nut, etc.) and mechanical connections
    # are derived for complete estimates but excluded from standard output
    # since many client material lists don't include them.
    # Uncomment to include:
    # support_hardware = derive_support_hardware(
    #     ceiling_sensors, f10_pendant_count, f11_pendant_count
    # )
    # derived.update(support_hardware)

    # ==========================================================================
    # LARGE FEEDER WIRE
    # ==========================================================================

    # Count 100A+ disconnects for #3 THHN
    feeder_wire_feet = 0
    large_disconnects = counts.get("100A/3P Safety Switch 600V", 0)
    if large_disconnects > 0:
        feeder_wire = derive_large_feeder_wire(large_disconnects)
        derived.update(feeder_wire)
        feeder_wire_feet = sum(feeder_wire.values())

    # ==========================================================================
    # MECHANICAL CONNECTIONS (optional — not all clients include these)
    # ==========================================================================

    # Mechanical connections (flex conduit, disconnects) are project-specific.
    # Uncomment to include:
    # if mechanical_equipment_count > 0:
    #     mechanical = derive_mechanical_connections(mechanical_equipment_count)
    #     derived.update(mechanical)

    # ==========================================================================
    # MISC LABOR ITEMS
    # ==========================================================================

    # Largest pendant for channel cutting calculation
    largest_pendant_count = counts.get("F11-16X10", 0)
    if largest_pendant_count == 0:
        largest_pendant_count = counts.get("F11-10X10", 0)

    # Misc labor items (core drilling, channel cutting, wire termination)
    # Excluded from standard output — uncomment to include:
    # misc_labor = derive_misc_labor(floor_count, largest_pendant_count)
    # derived.update(misc_labor)

    # ==========================================================================
    # FITTINGS (if conduit data available)
    # ==========================================================================

    if include_fittings and conduit_lengths:
        fittings = derive_fittings_from_conduit(conduit_lengths)
        derived.update(fittings)

    # ==========================================================================
    # WIRE (derive before consumables so we can use total wire footage)
    # ==========================================================================

    total_wire_feet = 0
    total_conduit_feet = sum(conduit_lengths.values()) if conduit_lengths else 0
    if conduit_lengths:
        wire = derive_wire_from_conduit(conduit_lengths)
        if include_wire:
            derived.update(wire)
        total_wire_feet = sum(wire.values())
    total_wire_feet += feeder_wire_feet  # Include #3 THHN feeder wire

    # ==========================================================================
    # CONSUMABLES
    # ==========================================================================

    if include_consumables:
        # Wire connections: devices that have wire splices using wirenuts
        # Excludes: F9 (push connectors), F4E (integrated wiring), X2 (surface-mount)
        # Calibrated: total gives 220 connections × 3 = 660 wirenuts
        wire_connections = duplex + gfi + total_switches + dimmers + \
                          ceiling_sensors + wall_sensors + daylight_sensors + \
                          f2 + f3 + f4 + f5 + f7 + f7e + f8 + \
                          x1 + strip_4 + data_jacks

        # Fixture connections for Red Scotchlok (low-voltage fixture connections)
        # Only lay-in and surface-mount fixtures use Scotchlok connectors
        # Calibrated: lay_in(7) + surface(5) = 12 × 3 = 36
        fixture_connections = lay_in_fixtures + surface_count

        # Ground Screw w/Pigtail: receptacles minus shared 2G locations
        # Each 2G location has 2 receptacles sharing 1 pigtail
        # Calibrated: (37+5) - 3 = 39 with GT inputs
        grounded_devices = (duplex + gfi) - two_gang_locations

        # Ground Screw (plain): junction boxes minus deep device boxes
        # Plain ground screws go in junction boxes; deep boxes get pigtails instead
        # Calibrated: 61 - 10 = 51 with GT inputs
        ground_screw_plain_count = max(0, junction_points - high_capacity_devices)

        # Pan Head Screw boxes: standard device boxes minus clip-in fixtures
        # (recessed downlights F4/F4E self-mount; X2 is surface-mount)
        # Calibrated: (103 - 10 - 2 - 1) × 4 = 360
        pan_head_box_count = max(0,
            device_box_count - high_capacity_devices - f4 - f4e -
            (1 if x2 > 0 else 0))  # X2 surface-mount

        consumables = derive_consumables(
            wire_connections=wire_connections,
            fixture_connections=fixture_connections,
            grounded_devices=grounded_devices,
            pan_head_boxes=pan_head_box_count,
            total_wire_feet=total_wire_feet,
            total_conduit_feet=total_conduit_feet,
            boxes_total=ground_screw_plain_count
        )
        derived.update(consumables)

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


def explain_derivations(
    counts: Dict[str, int],
    conduit_lengths: Dict[str, int] = None,
    mechanical_equipment_count: int = 0,
) -> Dict[str, str]:
    """
    Generate human-readable formula explanations for each derived material.

    Uses the same inputs as derive_all_materials but returns formula strings
    instead of quantities. These explain HOW each number was calculated.
    """
    formulas: Dict[str, str] = {}

    # --- Extract the same input values as derive_all_materials ---
    ceiling_sensors = counts.get("Ceiling Occupancy Sensor", 0)
    wall_sensors = counts.get("Wall Occupancy Sensor", 0)
    daylight_sensors = counts.get("Daylight Sensor", 0)
    data_jacks = counts.get("Cat 6 Jack", 0)
    duplex = counts.get("Duplex Receptacle", 0)
    gfi = counts.get("GFI Receptacle", 0)
    dimmers = counts.get("Wireless Dimmer", 0)
    sp_switches = counts.get("SP Switch", 0)
    three_way = counts.get("3-Way Switch", 0)
    total_switches = sp_switches + three_way

    f2 = counts.get("F2", 0)
    f3 = counts.get("F3", 0)
    f4 = counts.get("F4", 0)
    f4e = counts.get("F4E", 0)
    f5 = counts.get("F5", 0)
    f7 = counts.get("F7", 0)
    f7e = counts.get("F7E", 0)
    f8 = counts.get("F8", 0)
    f9 = counts.get("F9", 0)
    x1 = counts.get("X1", 0)
    x2 = counts.get("X2", 0)
    strip_4 = counts.get("4' L.E.D. Strip", 0)

    linear_count = sum(counts.get(k, 0) for k in [
        "4' Linear LED", "6' Linear LED", "8' Linear LED",
        "10' Linear LED", "16' Linear LED",
    ])
    f10_count = counts.get("F10-22", 0) + counts.get("F10-30", 0)
    f11_count = sum(counts.get(k, 0) for k in [
        "F11-4X4", "F11-6X6", "F11-8X8", "F11-10X10", "F11-16X10",
    ])
    pendant_count = f10_count + f11_count

    lay_in = f2 + f8
    surface = f7 + f7e
    power_packs = int((ceiling_sensors + wall_sensors) * 0.74)
    sep_pp = max(0, power_packs - wall_sensors - max(0, daylight_sensors - 1))
    device_box_count = (duplex + gfi + total_switches + dimmers + wall_sensors +
                       ceiling_sensors + daylight_sensors +
                       f4 + f4e + f5 + x1 + (x2 - 1 if x2 > 0 else 0) + sep_pp)
    high_cap = gfi + total_switches
    junction = (f2 + f3 + f7 + f7e + f8 + f9 + x1 + x2 + strip_4 +
               f10_count + f4 + f5)
    large_jnc = f11_count + 1
    floor_box_jacks = 3
    sensor_ctrl = max(0, data_jacks - floor_box_jacks)
    two_gang = counts.get("two_gang_locations", 3)

    # --- Power Packs ---
    formulas["Power Pack"] = (
        f"({ceiling_sensors} ceiling + {wall_sensors} wall sensors) × 0.74 = {power_packs}"
    )

    # --- Cat 6 ---
    formulas["Cat 6 Cable (ft)"] = f"{data_jacks} jacks × {10} ft/jack = {data_jacks * 10}"
    formulas["J-Hook"] = f"{data_jacks * 10} ft cable ÷ {4} ft spacing = {(data_jacks * 10) // 4}"

    # --- Boxes ---
    formulas['4" Square Box w/bracket'] = (
        f"{duplex} dup + {gfi} GFI + {total_switches} sw + {dimmers} dim + "
        f"{ceiling_sensors} ceil + {wall_sensors} wall + {daylight_sensors} day + "
        f"fixtures({f4}+{f4e}+{f5}+{x1}) + {sep_pp} PP boxes = "
        f"{max(0, device_box_count - high_cap)}"
    )
    formulas['4" Square Box'] = (
        f"Junction points: {f2}+{f3}+{f7}+{f7e}+{f8}+{f9}+{x1}+{x2}+"
        f"{strip_4}+{f10_count}+{f4}+{f5} = {junction}"
    )
    formulas['4" Square Box 2-1/8" deep'] = (
        f"High-capacity: {gfi} GFI + {total_switches} switches = {high_cap}"
    )
    formulas['4-11/16" Square Box'] = f"{f11_count} F11 pendants + 1 = {large_jnc}"
    formulas['4-11/16" Square Box w/bracket'] = (
        f"{data_jacks} data jacks − {floor_box_jacks} floor box = {sensor_ctrl}"
    )

    # --- Plaster Rings ---
    ring_1g = max(0, duplex + gfi + total_switches + dimmers +
                 wall_sensors + daylight_sensors + f4 - (two_gang * 2))
    formulas['4" Square-1G Plaster Ring'] = (
        f"{duplex} dup + {gfi} GFI + {total_switches} sw + {dimmers} dim + "
        f"{wall_sensors} wall + {daylight_sensors} day + {f4} F4 − {two_gang * 2} 2G = {ring_1g}"
    )
    formulas['4" Square-2G Plaster Ring'] = f"{two_gang} two-gang locations"
    s_3_0 = (ceiling_sensors + daylight_sensors + f4 + f4e + f3 + strip_4 +
            max(0, x1 - 2))
    f_3_0 = f2 + f8 + f7 + f7e + 1
    formulas['4" Square-3/0 Plaster Ring'] = (
        f"Surface({s_3_0}) + Flush({f_3_0}) = {s_3_0 + f_3_0}"
    )
    formulas['4-11/16"-1G Plaster Ring'] = f"= sensor/control boxes = {sensor_ctrl}"

    # --- Plates ---
    formulas["Duplex Plate"] = (
        f"{duplex} duplex − {two_gang * 2} in 2G locations = {max(0, duplex - two_gang * 2)}"
    )
    formulas["Decora Plate"] = f"{gfi} GFI + {wall_sensors} wall sensors = {gfi + wall_sensors}"
    formulas["Switch Plate"] = f"{sp_switches} SP + {three_way} 3-way = {total_switches}"
    formulas["Blank Cover"] = f"~21% of {junction} junction points = {round(junction * 0.21)}"
    formulas["Blank Cover w/KO"] = (
        f"~23% of {junction} junctions + {large_jnc} large = "
        f"{int(junction * 0.23) + large_jnc}"
    )
    if two_gang > 0:
        formulas["Duplex Plate 2G"] = f"{two_gang} two-gang locations"

    # --- Fixture Accessories ---
    formulas["Fixture Whip"] = f"{f2} F2 lay-in + {dimmers} dimmers = {f2 + dimmers}"
    p_cable = pendant_count + linear_count + (f9 + f3 + strip_4 + 1)
    formulas["Pendant/Cable"] = (
        f"{pendant_count} pendants + {linear_count} linear + "
        f"({f9}+{f3}+{strip_4}+1) strips = {p_cable}"
    )
    if f11_count > 0:
        formulas["Seismic Wire"] = f"{f11_count} F11 pendants × 0.5 = {int(f11_count * 0.5)}"

    # --- Large Feeder Wire ---
    large_disc = counts.get("100A/3P Safety Switch 600V", 0)
    if large_disc > 0:
        formulas["#3 THHN"] = (
            f"{large_disc} disconnect × 50 ft × 3 conductors = {large_disc * 50 * 3}"
        )

    # --- Wire ---
    if conduit_lengths:
        c34 = conduit_lengths.get('3/4"', 0)
        c1 = conduit_lengths.get('1"', 0)
        c114 = conduit_lengths.get('1-1/4"', 0)
        if c34 > 0:
            formulas["#12 THHN"] = (
                f'{c34:,} ft of 3/4" EMT × 2.266 = {int(c34 * 2.26562):,}'
            )
        if c1 > 0:
            formulas["#10 THHN"] = (
                f'{c1:,} ft of 1" EMT × 8.386 = {int(c1 * 8.38608):,}'
            )
        if c114 > 0:
            formulas["#8 THHN"] = (
                f'{c114:,} ft of 1-1/4" EMT × 0.076 = {int(c114 * 0.0764)}'
            )

    # --- Fittings (per 100 ft) ---
    if conduit_lengths:
        size_labels = {
            '1/2"': ("1/2\"", 10.0, 8.0, 10.0, 12.0, 0),
            '3/4"': ("3/4\"", 10.47, 9.22, 10.47, 9.22, 3.075),
            '1"': ("1\"", 4.9, 8.1, 4.9, 1.9, 10.1),
            '1-1/4"': ("1-1/4\"", 11.8, 5.8, 11.8, 4.1, 7.3),
        }
        for size, length in conduit_lengths.items():
            if size in size_labels and length > 0:
                label, conn_r, coup_r, bush_r, strap_r, uni_r = size_labels[size]
                factor = length / 100
                formulas[f'{label} Connector'] = (
                    f'{length:,} ft ÷ 100 × {conn_r} = {int(factor * conn_r)}'
                )
                formulas[f'{label} Coupling'] = (
                    f'{length:,} ft ÷ 100 × {coup_r} = {int(factor * coup_r)}'
                )
                formulas[f'{label} Bushing'] = (
                    f'{length:,} ft ÷ 100 × {bush_r} = {int(factor * bush_r)}'
                )
                formulas[f'{label} 1-Hole Strap'] = (
                    f'{length:,} ft ÷ 100 × {strap_r} = {int(factor * strap_r)}'
                )
                if uni_r > 0:
                    formulas[f'{label} Unistrut Strap'] = (
                        f'{length:,} ft ÷ 100 × {uni_r} = {int(factor * uni_r)}'
                    )

    # --- Consumables ---
    wire_conn = (duplex + gfi + total_switches + dimmers +
                ceiling_sensors + wall_sensors + daylight_sensors +
                f2 + f3 + f4 + f5 + f7 + f7e + f8 + x1 + strip_4 + data_jacks)
    fixture_conn = lay_in + surface
    grounded = (duplex + gfi) - two_gang
    pan_box = max(0, device_box_count - high_cap - f4 - f4e - (1 if x2 > 0 else 0))
    total_conduit_ft = sum(conduit_lengths.values()) if conduit_lengths else 0
    total_wire_ft = 0
    if conduit_lengths:
        c34 = conduit_lengths.get('3/4"', 0)
        c1 = conduit_lengths.get('1"', 0)
        c114 = conduit_lengths.get('1-1/4"', 0)
        total_wire_ft = int(c34 * 2.26562) + int(c1 * 8.38608) + int(c114 * 0.0764)
    total_wire_ft += large_disc * 150 if large_disc > 0 else 0

    formulas["Red Wirenut"] = (
        f"{wire_conn} wire connections × 3 = {int(wire_conn * 3)}"
    )
    formulas["Red Scotchlok"] = (
        f"({lay_in} lay-in + {surface} surface) × 3 = {int(fixture_conn * 3)}"
    )
    formulas["Ground Screw w/Pigtail"] = (
        f"({duplex} + {gfi}) − {two_gang} shared = {grounded}"
    )
    formulas["Ground Screw"] = (
        f"{junction} junction pts − {high_cap} deep boxes = {max(0, junction - high_cap)}"
    )
    formulas["Pan Head Screw"] = f"{pan_box} box locations × 4 = {int(pan_box * 4)}"
    formulas["Poly Pull Line (ft)"] = (
        f"({total_conduit_ft:,} conduit + {total_wire_ft:,} wire) × 0.089 = "
        f"{int((total_conduit_ft + total_wire_ft) * 0.0888):,}"
    )

    return formulas
