"""Project configuration for the MEP TakeOff System.

This module provides a configuration-driven approach to electrical takeoffs,
making the system adaptable to different projects without code changes.

The ProjectConfig class stores:
- Sheet page mappings (auto-detected or manually specified)
- Project parameters (floor count, building size)
- Configurable ratios with industry-standard defaults
- Fixture definitions from schedules
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
import yaml
import json
from pathlib import Path


@dataclass
class ProjectConfig:
    """
    Configuration for a specific electrical takeoff project.

    This class centralizes all project-specific values that were previously
    hardcoded throughout the system. It supports:
    - Auto-detection of sheet pages from the PDF
    - Manual overrides for any value
    - Loading/saving to YAML or JSON files
    - Industry-standard defaults for all ratios

    Attributes:
        name: Project name for identification
        sheet_map: Mapping of sheet numbers to PDF page indices (0-indexed)
        floor_count: Number of floors (for multi-floor sheet deduplication)
        building_sqft: Building square footage (for conduit estimation)
        cable_per_jack_ft: Feet of Cat 6 cable per data jack
        power_pack_ratio: Power packs per occupancy sensor
        oc_ceiling_ratio: Ratio of ceiling vs wall occupancy sensors
        fixture_definitions: Fixture types from E600 schedule
        conduit_ratios: Ratios for deriving fittings from conduit
    """

    # Project identification
    name: str = "Unnamed Project"

    # Sheet page mapping (auto-detected or manual override)
    # Keys are sheet numbers (E100, E200, etc.)
    # Values are 0-indexed page numbers
    sheet_map: Dict[str, int] = field(default_factory=dict)

    # Project parameters
    floor_count: int = 2  # Number of floors shown on multi-floor sheets
    building_sqft: int = 10000  # Building size for estimation

    # Configurable ratios (with industry defaults)
    cable_per_jack_ft: int = 10  # Feet of Cat 6 cable per data jack
    power_pack_ratio: float = 0.74  # Power packs per OC sensor
    oc_ceiling_ratio: float = 0.84  # Ceiling OC ratio (vs wall)
    jhook_spacing_ft: int = 4  # J-hook spacing in feet

    # Reference conduit (from client material list or prior bid)
    # e.g. {'1/2"': 100, '3/4"': 3773, '1"': 790, '1-1/4"': 655}
    reference_conduit: Dict[str, int] = field(default_factory=dict)
    conduit_source: str = "estimated"  # "reference" | "estimated"

    # Fixture definitions (auto-read from E600 or manual)
    # Format: {"F2": {"description": "2x4 Recessed", "category": "lay-in"}, ...}
    fixture_definitions: Dict[str, dict] = field(default_factory=dict)

    # Conduit derivation ratios (per 100 ft of conduit)
    conduit_ratios: Dict[str, float] = field(default_factory=lambda: {
        "connector_per_100ft": 10.5,
        "coupling_per_100ft": 9.2,
        "bushing_per_100ft": 10.5,
        "strap_1hole_per_100ft": 9.2,
        "strap_unistrut_per_100ft": 3.1,
    })

    # Wire derivation multipliers
    wire_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "lighting_pct": 0.6,  # % of conduit for lighting (#12)
        "power_pct": 0.3,    # % of conduit for power (#10)
        "feeder_pct": 0.1,   # % of conduit for feeders (#8+)
    })

    # Demo item keynote mapping (typical E100 legends)
    demo_keynotes: Dict[str, str] = field(default_factory=lambda: {
        '1': "Demo 2'x4' Recessed",
        '2': "Demo 2'x2' Recessed",
        '3': "Demo Downlight",
        '4': "Demo Switch",
        '5': "Demo 4' Strip",
        '6': "Demo 8' Strip",
        '7': "Demo Exit",
        '9': "Demo Receptacle",
    })

    def get_sheet_page(self, sheet_number: str) -> int:
        """
        Get the page index for a sheet number.

        Args:
            sheet_number: Sheet number (e.g., "E200")

        Returns:
            Page index (0-indexed), or default based on typical conventions
        """
        sheet_upper = sheet_number.upper()

        if sheet_upper in self.sheet_map:
            return self.sheet_map[sheet_upper]

        # Return typical defaults if not in map
        defaults = {
            "E001": 0,
            "E100": 1,
            "E200": 2,
            "E201": 3,
            "E600": 4,
            "E700": 5,
            "E701": 6,
            "T100": 7,
            "T200": 8,
        }
        return defaults.get(sheet_upper, -1)

    def update_sheet_map(self, detected_map: Dict[str, int]) -> None:
        """
        Update sheet map with detected values, preserving manual overrides.

        Args:
            detected_map: Auto-detected sheet page mapping
        """
        for sheet, page in detected_map.items():
            if sheet not in self.sheet_map:
                self.sheet_map[sheet] = page

    def derive_power_packs(self, ceiling_sensors: int, wall_sensors: int) -> int:
        """Calculate power packs using configured ratio."""
        total_sensors = ceiling_sensors + wall_sensors
        return int(total_sensors * self.power_pack_ratio)

    def derive_cable_and_jhooks(self, data_jacks: int) -> tuple:
        """Calculate Cat 6 cable and J-hooks using configured ratios."""
        cable_feet = data_jacks * self.cable_per_jack_ft
        jhooks = cable_feet // self.jhook_spacing_ft
        return cable_feet, jhooks

    def derive_fittings_from_conduit(self, conduit_lengths: Dict[str, int]) -> Dict[str, int]:
        """Derive fittings from conduit using configured ratios."""
        fittings = {}

        for size, length in conduit_lengths.items():
            if length <= 0:
                continue

            factor = length / 100

            fittings[f"{size} Connector"] = int(factor * self.conduit_ratios["connector_per_100ft"])
            fittings[f"{size} Coupling"] = int(factor * self.conduit_ratios["coupling_per_100ft"])
            fittings[f"{size} Bushing"] = int(factor * self.conduit_ratios["bushing_per_100ft"])
            fittings[f"{size} 1-Hole Strap"] = int(factor * self.conduit_ratios["strap_1hole_per_100ft"])
            fittings[f"{size} Unistrut Strap"] = int(factor * self.conduit_ratios["strap_unistrut_per_100ft"])

        return fittings

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'ProjectConfig':
        """
        Load configuration from a YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            ProjectConfig instance
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_path: str) -> 'ProjectConfig':
        """
        Load configuration from a JSON file.

        Args:
            json_path: Path to JSON configuration file

        Returns:
            ProjectConfig instance
        """
        with open(json_path, 'r') as f:
            data = json.load(f)

        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_yaml(self, yaml_path: str) -> None:
        """
        Save configuration to a YAML file.

        Args:
            yaml_path: Path for output YAML file
        """
        data = {
            'name': self.name,
            'sheet_map': self.sheet_map,
            'floor_count': self.floor_count,
            'building_sqft': self.building_sqft,
            'cable_per_jack_ft': self.cable_per_jack_ft,
            'power_pack_ratio': self.power_pack_ratio,
            'oc_ceiling_ratio': self.oc_ceiling_ratio,
            'jhook_spacing_ft': self.jhook_spacing_ft,
            'fixture_definitions': self.fixture_definitions,
            'conduit_ratios': self.conduit_ratios,
            'wire_multipliers': self.wire_multipliers,
            'demo_keynotes': self.demo_keynotes,
            'reference_conduit': self.reference_conduit,
            'conduit_source': self.conduit_source,
        }

        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def to_json(self, json_path: str) -> None:
        """
        Save configuration to a JSON file.

        Args:
            json_path: Path for output JSON file
        """
        data = {
            'name': self.name,
            'sheet_map': self.sheet_map,
            'floor_count': self.floor_count,
            'building_sqft': self.building_sqft,
            'cable_per_jack_ft': self.cable_per_jack_ft,
            'power_pack_ratio': self.power_pack_ratio,
            'oc_ceiling_ratio': self.oc_ceiling_ratio,
            'jhook_spacing_ft': self.jhook_spacing_ft,
            'fixture_definitions': self.fixture_definitions,
            'conduit_ratios': self.conduit_ratios,
            'wire_multipliers': self.wire_multipliers,
            'demo_keynotes': self.demo_keynotes,
            'reference_conduit': self.reference_conduit,
            'conduit_source': self.conduit_source,
        }

        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)


def create_config_from_pdf(pdf_path: str, name: Optional[str] = None) -> ProjectConfig:
    """
    Create a ProjectConfig by auto-detecting values from a PDF.

    This function:
    1. Detects sheet pages from title blocks
    2. Parses E600 for fixture definitions
    3. Sets reasonable defaults for other values

    Args:
        pdf_path: Path to the electrical PDF
        name: Optional project name

    Returns:
        ProjectConfig with auto-detected values
    """
    from .pdf_extractor import detect_sheet_pages, parse_fixture_schedule_from_pdf

    config = ProjectConfig()

    if name:
        config.name = name
    else:
        config.name = Path(pdf_path).stem

    # Auto-detect sheet pages
    try:
        config.sheet_map = detect_sheet_pages(pdf_path)
        print(f"  Detected sheets: {config.sheet_map}")
    except Exception as e:
        print(f"  Warning: Could not auto-detect sheets: {e}")

    # Parse fixture definitions from E600
    try:
        fixture_data = parse_fixture_schedule_from_pdf(pdf_path, sheet_map=config.sheet_map)
        config.fixture_definitions = fixture_data.get("definitions", {})
        print(f"  Found {len(config.fixture_definitions)} fixture definitions")
    except Exception as e:
        print(f"  Warning: Could not parse fixture schedule: {e}")

    return config


# Default configuration for IVCC CETLA project (for reference/testing)
IVCC_CETLA_CONFIG = ProjectConfig(
    name="IVCC CETLA",
    sheet_map={
        "E001": 0,
        "E100": 1,
        "E200": 2,
        "E201": 3,
        "E600": 4,
        "E700": 5,
        "E701": 6,
        "T100": 7,
        "T200": 8,
    },
    floor_count=2,
    building_sqft=15000,
    cable_per_jack_ft=10,
    power_pack_ratio=0.74,
    oc_ceiling_ratio=0.84,
    # Reference conduit from client material list (known accurate values)
    reference_conduit={
        '1/2"': 100,
        '3/4"': 3773,
        '1"': 790,
        '1-1/4"': 655,
    },
    conduit_source="reference",
)
