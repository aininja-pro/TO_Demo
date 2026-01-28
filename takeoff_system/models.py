"""Data models for the MEP TakeOff System."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SheetType(Enum):
    """Classification of drawing sheets."""
    LEGEND = "LEGEND"
    DEMO = "DEMO"
    NEW = "NEW"
    SCHEDULE = "SCHEDULE"
    REFERENCE = "REFERENCE"


@dataclass
class Sheet:
    """Represents a single sheet from the drawing set."""
    page_number: int
    sheet_number: str
    sheet_type: SheetType
    title: str
    image_path: Optional[str] = None


@dataclass
class SymbolDefinition:
    """Definition of a symbol from the legend."""
    tag: str
    description: str
    category: str  # fixture, control, power, fire_alarm, technology
    wattage: Optional[float] = None


@dataclass
class DeviceCounts:
    """Counts of devices from a sheet or aggregated."""
    # Fixtures
    fixtures: dict = field(default_factory=dict)
    # Controls
    controls: dict = field(default_factory=dict)
    # Power devices
    power: dict = field(default_factory=dict)
    # Fire alarm
    fire_alarm: dict = field(default_factory=dict)
    # Technology
    technology: dict = field(default_factory=dict)
    # Demo items (separate tracking)
    demo: dict = field(default_factory=dict)

    def merge(self, other: 'DeviceCounts') -> 'DeviceCounts':
        """Merge another DeviceCounts into this one."""
        for attr in ['fixtures', 'controls', 'power', 'fire_alarm', 'technology', 'demo']:
            self_dict = getattr(self, attr)
            other_dict = getattr(other, attr)
            for key, value in other_dict.items():
                self_dict[key] = self_dict.get(key, 0) + value
        return self


@dataclass
class MaterialList:
    """Generated material list."""
    new_materials: dict = field(default_factory=dict)
    demo_materials: dict = field(default_factory=dict)
    derived_materials: dict = field(default_factory=dict)  # From business rules


@dataclass
class ValidationResult:
    """Result of comparing generated counts to ground truth."""
    item: str
    expected: int
    actual: int
    difference: int
    accuracy_pct: float
    status: str  # exact, close, miss


@dataclass
class FixtureScheduleData:
    """Data extracted from fixture schedule (E600)."""
    linear_fixtures: Dict[str, int] = field(default_factory=dict)  # 4', 6', 8', 10', 16' LEDs
    pendant_fixtures: Dict[str, int] = field(default_factory=dict)  # F10-xx, F11-xxxx
    standard_fixtures: Dict[str, int] = field(default_factory=dict)  # Other fixture types


@dataclass
class PanelScheduleData:
    """Data extracted from panel schedule (E700)."""
    breakers: Dict[str, int] = field(default_factory=dict)  # 20A 1P, 30A 2P, etc.
    safety_switches: Dict[str, int] = field(default_factory=dict)  # 30A/2P, 100A/3P, etc.
    feeder_wire: Dict[str, int] = field(default_factory=dict)  # Wire sizes for feeders


@dataclass
class ConduitCounts:
    """Counts and lengths for conduit and wire."""
    conduit_by_size: Dict[str, int] = field(default_factory=dict)  # 3/4" EMT: feet, etc.
    wire_by_size: Dict[str, int] = field(default_factory=dict)  # #12 THHN: feet, etc.


@dataclass
class RoutingData:
    """Combined routing analysis data."""
    conduit: ConduitCounts = field(default_factory=ConduitCounts)
    estimated_method: str = "ai_vision"  # ai_vision, device_based, manual


@dataclass
class FullTakeoffResult:
    """Complete result from full takeoff pipeline."""
    # Counted items
    new_counts: DeviceCounts = field(default_factory=DeviceCounts)
    demo_counts: DeviceCounts = field(default_factory=DeviceCounts)

    # Schedule data
    fixture_schedule: FixtureScheduleData = field(default_factory=FixtureScheduleData)
    panel_schedule: PanelScheduleData = field(default_factory=PanelScheduleData)

    # Routing data
    routing: RoutingData = field(default_factory=RoutingData)

    # Derived materials
    derived_materials: Dict[str, int] = field(default_factory=dict)

    # Validation
    validation_results: List[ValidationResult] = field(default_factory=list)
