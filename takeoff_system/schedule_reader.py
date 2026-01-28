"""Schedule reading module for E600 (fixtures) and E700 (panels).

This module uses Claude Vision to extract structured data from schedule tables
in construction drawings.
"""
import base64
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image

from .models import FixtureScheduleData, PanelScheduleData


def resize_image_if_needed(image_path: str, max_dimension: int = 6000) -> str:
    """Resize image if it exceeds the max dimension limit."""
    with Image.open(image_path) as img:
        width, height = img.size
        if width <= max_dimension and height <= max_dimension:
            return image_path

        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))

        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        suffix = Path(image_path).suffix
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        resized.save(temp_path)

        return temp_path


def encode_image_to_base64(image_path: str) -> Tuple[str, str]:
    """Encode image to base64, resizing if needed. Returns (data, temp_path or None)."""
    processed_path = resize_image_if_needed(image_path)

    with open(processed_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")

    temp_created = processed_path if processed_path != image_path else None
    return data, temp_created


def get_media_type(image_path: str) -> str:
    """Get media type from file extension."""
    ext = Path(image_path).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "image/png")


# Prompt for E600 - Fixture/Luminaire Schedule
FIXTURE_SCHEDULE_PROMPT = """You are an expert electrical estimator analyzing an ELECTRICAL SCHEDULES sheet (E600).

This is a SPECIFICATION SCHEDULE - it defines fixture types but does NOT contain project quantities.
The QUANTITIES must be counted from floor plans, not from this schedule.

FOCUS ON THE LED LUMINAIRE SCHEDULE TABLE on the right side.

YOUR TASK: Identify which fixture types are SPECIFIED for this project.
Return 0 for all quantities - the actual counts come from floor plan analysis.

FIXTURE TYPES TO LOOK FOR (just confirm they exist in the schedule):
- Standard: F2, F3, F4, F4E, F5, F7, F7E, F8, F9, X1, X2
- Linear LEDs by length: 4', 6', 8', 10', 16'
- Pendants: F10-22 (22-foot linear), F10-30 (30-foot linear)
- Pendant arrays: F11-4X4, F11-6X6, F11-8X8, F11-10X10, F11-16X10

CRITICAL: DO NOT confuse fixture TYPE names with quantities!
- "F10-22" means a fixture TYPE that is 22 feet long, NOT "F10" with qty 22
- "F11-8X8" means an 8x8 array fixture TYPE, NOT "F11" with qty 8

Return ONLY JSON - set all quantities to 0 since this is a spec sheet:
```json
{
    "standard_fixtures": {
        "F2": 0,
        "F3": 0,
        "F4": 0,
        "F4E": 0,
        "F5": 0,
        "F7": 0,
        "F7E": 0,
        "F8": 0,
        "F9": 0,
        "X1": 0,
        "X2": 0
    },
    "linear_fixtures": {
        "4' Linear LED": 0,
        "6' Linear LED": 0,
        "8' Linear LED": 0,
        "10' Linear LED": 0,
        "16' Linear LED": 0
    },
    "pendant_fixtures": {
        "F10-22": 0,
        "F10-30": 0,
        "F11-4X4": 0,
        "F11-6X6": 0,
        "F11-8X8": 0,
        "F11-10X10": 0,
        "F11-16X10": 0
    },
    "notes": "<list fixture types you found specified in the schedule>"
}
```"""


# Prompt for E700 - Panel Schedule
PANEL_SCHEDULE_PROMPT = """You are an expert electrical estimator analyzing a PANEL SCHEDULES sheet (E700).

This sheet contains ELECTRICAL PANEL SCHEDULES showing circuit breakers and equipment.

EXTRACT THE FOLLOWING:

1. CIRCUIT BREAKERS - Count by type across ALL panels:
   - 20A 1-Pole (20A 1P) - single pole 20 amp breakers
   - 30A 2-Pole (30A 2P) - double pole 30 amp breakers
   - 50A 2-Pole (50A 2P) - double pole 50 amp breakers
   - Other sizes if present

   Look at each panel schedule table. Count the breakers in the circuit columns.
   A 2-pole breaker takes 2 spaces and is usually shown spanning two rows.

2. SAFETY SWITCHES / DISCONNECTS:
   - 30A/2P Safety Switch (240V) - for equipment disconnects
   - 30A/3P Safety Switch (600V) - 3-phase disconnect
   - 100A/3P Safety Switch (600V) - main disconnect
   - Other sizes if shown

3. FEEDER INFORMATION (if visible):
   - Main breaker sizes
   - Feeder wire sizes

Panel schedules typically show:
- Panel designation (Panel A, Panel B, etc.)
- Circuit number columns (1,3,5,7... and 2,4,6,8...)
- Breaker sizes in amps
- Load descriptions

Count EVERY breaker across ALL panels shown.

Return ONLY JSON in this exact format:
```json
{
    "breakers": {
        "20A 1P Breaker": <count>,
        "30A 2P Breaker": <count>,
        "50A 2P Breaker": <count>
    },
    "safety_switches": {
        "30A/2P Safety Switch 240V": <count>,
        "30A/3P Safety Switch 600V": <count>,
        "100A/3P Safety Switch 600V": <count>
    },
    "panels_found": ["<list of panel names>"],
    "notes": "<any relevant observations>"
}
```"""


def read_fixture_schedule(
    image_path: str,
    api_key: Optional[str] = None
) -> FixtureScheduleData:
    """
    Read fixture schedule from E600 sheet using Claude Vision.

    Args:
        image_path: Path to E600 sheet image
        api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)

    Returns:
        FixtureScheduleData with extracted quantities
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required. Install with: pip install anthropic")

    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    # Encode image
    image_data, temp_path = encode_image_to_base64(image_path)
    media_type = get_media_type(image_path)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": FIXTURE_SCHEDULE_PROMPT}
                ],
            }],
        )
    finally:
        if temp_path:
            os.remove(temp_path)

    # Parse response
    response_text = message.content[0].text
    data = _extract_json(response_text)

    result = FixtureScheduleData()
    result.linear_fixtures = data.get("linear_fixtures", {})
    result.pendant_fixtures = data.get("pendant_fixtures", {})
    result.standard_fixtures = data.get("standard_fixtures", {})

    return result


def read_panel_schedule(
    image_path: str,
    api_key: Optional[str] = None
) -> PanelScheduleData:
    """
    Read panel schedule from E700 sheet using Claude Vision.

    Args:
        image_path: Path to E700 sheet image
        api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)

    Returns:
        PanelScheduleData with extracted quantities
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required. Install with: pip install anthropic")

    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    # Encode image
    image_data, temp_path = encode_image_to_base64(image_path)
    media_type = get_media_type(image_path)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": PANEL_SCHEDULE_PROMPT}
                ],
            }],
        )
    finally:
        if temp_path:
            os.remove(temp_path)

    # Parse response
    response_text = message.content[0].text
    data = _extract_json(response_text)

    result = PanelScheduleData()
    result.breakers = data.get("breakers", {})
    result.safety_switches = data.get("safety_switches", {})

    return result


def _extract_json(response_text: str) -> Dict:
    """Extract JSON from Claude response text."""
    try:
        # Try code block first
        code_block = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
        if code_block:
            return json.loads(code_block.group(1))

        # Try raw JSON
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())

        print(f"Warning: Could not find JSON in response: {response_text[:200]}")
        return {}

    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON: {e}")
        print(f"Response: {response_text[:500]}")
        return {}


def read_all_schedules(
    e600_path: str,
    e700_path: str,
    api_key: Optional[str] = None
) -> Tuple[FixtureScheduleData, PanelScheduleData]:
    """
    Read both fixture and panel schedules.

    Args:
        e600_path: Path to E600 sheet image
        e700_path: Path to E700 sheet image
        api_key: Anthropic API key

    Returns:
        Tuple of (FixtureScheduleData, PanelScheduleData)
    """
    print("  Reading fixture schedule (E600)...")
    fixture_data = read_fixture_schedule(e600_path, api_key)

    print("  Reading panel schedule (E700)...")
    panel_data = read_panel_schedule(e700_path, api_key)

    return fixture_data, panel_data
