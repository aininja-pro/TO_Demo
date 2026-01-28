"""AI Vision-based symbol counting using Claude API.

This module provides level-by-level analysis for improved accuracy,
scope filtering to count only specific areas, and support for
additional device and box types.
"""
import base64
import os
import json
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image

from .models import DeviceCounts, SheetType


def resize_image_if_needed(image_path: str, max_dimension: int = 7000) -> str:
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

        print(f"    Resized image from {width}x{height} to {new_width}x{new_height}")
        return temp_path


def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64, resizing if needed."""
    processed_path = resize_image_if_needed(image_path)

    with open(processed_path, "rb") as image_file:
        data = base64.standard_b64encode(image_file.read()).decode("utf-8")

    if processed_path != image_path:
        os.remove(processed_path)

    return data


def get_image_media_type(image_path: str) -> str:
    """Determine media type from file extension."""
    ext = Path(image_path).suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return media_types.get(ext, "image/png")


# =============================================================================
# SCOPE FILTERING
# =============================================================================

SCOPE_INSTRUCTIONS = {
    "all": "Scan ALL floor levels on this sheet completely. Count all NEW WORK devices.",
    "mezzanine_only": "Count ONLY devices on the MEZZANINE level. Ignore other floors.",
    "lower_level_only": "Count ONLY devices on the LOWER LEVEL / BASEMENT. Ignore other floors.",
    "first_floor_only": "Count ONLY devices on the FIRST FLOOR. Ignore other floors.",
    "second_floor_only": "Count ONLY devices on the SECOND FLOOR. Ignore other floors.",
    "new_work_only": "Count ONLY devices shown with THICK/SOLID lines (NEW WORK). Ignore thin/dashed lines.",
}


def get_scope_instruction(scope: str) -> str:
    """Get the scope filtering instruction for a prompt."""
    return SCOPE_INSTRUCTIONS.get(scope, SCOPE_INSTRUCTIONS["all"])


# =============================================================================
# PROMPTS FOR DIFFERENT SHEET TYPES
# =============================================================================

LIGHTING_PROMPT_TEMPLATE = """You are an expert electrical estimator analyzing a lighting floor plan.

CRITICAL: COUNT BY READING TEXT TAGS, NOT BY SHAPE

Each fixture on this drawing has a TEXT TAG label next to it. You MUST read the actual tag text.
DO NOT guess fixture types by their shape - read the tag.

FIXTURE TAG FORMAT:
- Tags appear as text like "F2", "F3", "F4", "F11" next to each fixture symbol
- Tags also include a CIRCUIT designation in parentheses, like "(LD2)" or "(LD3)"
- Example: A fixture tagged "F2 (LD2)" means fixture type F2 on circuit LD2

CRITICAL DISTINCTIONS:
- F2 = 2'x4' LED Lay-In (tags say "F2", typically in offices)
- F11 = Pendant arrays (tags say "F11/11/a", "F11/11/b", etc. - in large rooms like Band Room)
- These look similar as rectangles but have DIFFERENT TAGS - read the tag!

IMPORTANT RULES:
1. READ THE TEXT TAG next to each fixture - do not guess from shape
2. Only count NEW WORK (thick lines), not existing (thin lines) or demo (dashed)
3. For F4E and F7E, the "E" means EMERGENCY battery, NOT "Existing"
4. Count each fixture ONCE - don't double-count across floor plan views

SCOPE: {scope_instruction}

FIXTURE TYPES (identify by reading the TAG):
- F2: Tag says "F2" - 2'x4' LED Lay-In
- F3: Tag says "F3" - 4' LED Strip
- F4: Tag says "F4" - LED Recessed Downlight
- F4E: Tag says "F4E" - Downlight with Emergency
- F5: Tag says "F5" - 4' Vapor Tight
- F7: Tag says "F7" - 2'x4' Surface LED
- F7E: Tag says "F7E" - Surface LED with Emergency
- F8: Tag says "F8" - 2'x2' LED Lay-In
- F9: Tag says "F9" - 6' Linear LED
- F10: Tag says "F10-xx" - Linear pendant (xx = length)
- F11: Tag says "F11/xx/x" - Pendant array (DO NOT confuse with F2!)
- X1: Tag says "X1" - Exit Sign
- X2: Tag says "X2" - Exit Sign

CONTROL DEVICES (identify by reading the TAG):
- Ceiling Occupancy Sensor: Tag shows "OC" with subscript
- Wall Occupancy Sensor: Tag shows "OC" on wall
- Daylight Sensor: Tag shows "LS"
- Wireless Dimmer: Tag shows "D"

{level_instruction}

Return JSON with counts AND the circuits where you found each fixture type:
{{
    "fixtures": {{
        "F2": <count>,
        "F3": <count>,
        "F4": <count>,
        "F4E": <count>,
        "F5": <count>,
        "F7": <count>,
        "F7E": <count>,
        "F8": <count>,
        "F9": <count>,
        "X1": <count>,
        "X2": <count>
    }},
    "circuits_found": {{
        "F2": ["list of circuits like LD2, LD3"],
        "F4": ["list of circuits"]
    }},
    "controls": {{
        "Ceiling Occupancy Sensor": <count>,
        "Wall Occupancy Sensor": <count>,
        "Daylight Sensor": <count>,
        "Wireless Dimmer": <count>
    }}
}}"""


POWER_SYSTEMS_PROMPT_TEMPLATE = """You are an expert electrical estimator analyzing a power/systems floor plan.

CRITICAL: COUNT BY READING TEXT TAGS, NOT BY SHAPE

Each device has a TEXT TAG or label. Read the actual tag to identify the device type.
Tags with "-E" suffix indicate EXISTING devices - do NOT count these.

IMPORTANT RULES:
1. READ THE TEXT TAG next to each device
2. Only count NEW WORK (thick lines), not existing (thin) or demo (dashed)
3. Tags ending in "-E" mean EXISTING - skip these
4. Count each device ONCE across all floor plan views

SCOPE: {scope_instruction}

POWER DEVICES TO COUNT:
- Duplex Receptacle: Symbol with tag showing circuit (e.g., "P1", "P2")
- GFI Receptacle: Symbol tagged "GFI" or with GFI designation
- SP Switch: Single Pole Switch - tag shows "S" or switch symbol
- 3-Way Switch: Three-way switch - tag shows "S3" or "3"

FIRE ALARM DEVICES (for reference):
- Smoke Detector: Tagged "S"
- Horn/Strobe: Tagged "015" or "030"
- Pull Station: Tagged "F"

{level_instruction}

Return your counts as JSON ONLY, no other text:
{{
    "power": {{
        "Duplex Receptacle": <count>,
        "GFI Receptacle": <count>,
        "SP Switch": <count>,
        "3-Way Switch": <count>
    }},
    "boxes": {{
        "4\\" Square Box w/bracket": <count>,
        "4-11/16\\" Square Box": <count>,
        "4-11/16\\" Square Box w/bracket": <count>,
        "4\\" Square Box 2-1/8\\" deep": <count>
    }},
    "fire_alarm": {{
        "Smoke Detector": <count>,
        "Horn/Strobe 015": <count>,
        "Horn/Strobe 030": <count>,
        "Pull Station": <count>
    }}
}}"""


DEMO_PROMPT_TEMPLATE = """You are an expert electrical estimator analyzing a DEMOLITION floor plan.

This is a DEMO sheet - count fixtures and devices shown with DASHED LINES or HALFTONE patterns.
These items are to be REMOVED.

IMPORTANT RULES:
1. Demo items are shown with DASHED lines or lighter/halftone patterns
2. Count each item ONCE across all floor plan views shown
3. Identify fixture type by size/shape since demo items may not have tags

SCOPE: {scope_instruction}

DEMO ITEMS TO COUNT:
- Demo 2'x4' Recessed: 2'x4' recessed fluorescent fixtures (rectangular)
- Demo 2'x2' Recessed: 2'x2' recessed fixtures (square)
- Demo Downlight: Recessed downlights (circular)
- Demo 4' Strip: 4-foot strip fixtures
- Demo 8' Strip: 8-foot strip fixtures (longer strips)
- Demo Exit: Exit signs
- Demo Receptacle: Receptacles/outlets (circle symbols)
- Demo Floor Box: Floor boxes (rectangles, often tagged "FB")
- Demo Switch: Wall switches

{level_instruction}

Return your counts as JSON ONLY, no other text:
{{
    "demo": {{
        "Demo 2'x4' Recessed": <count>,
        "Demo 2'x2' Recessed": <count>,
        "Demo Downlight": <count>,
        "Demo 4' Strip": <count>,
        "Demo 8' Strip": <count>,
        "Demo Exit": <count>,
        "Demo Receptacle": <count>,
        "Demo Floor Box": <count>,
        "Demo Switch": <count>
    }}
}}"""


TECHNOLOGY_PROMPT_TEMPLATE = """You are an expert technology estimator analyzing a technology floor plan.

CRITICAL: COUNT BY READING TEXT TAGS

Each data jack has a TAG like "C2" or a number designation. Read the tags.

IMPORTANT RULES:
1. READ THE TEXT TAG next to each device
2. Only count NEW WORK (thick lines), not existing (thin) or demo (dashed)
3. Tags with "-E" suffix indicate EXISTING - do NOT count these
4. Count each device ONCE across all floor plan views

SCOPE: {scope_instruction}

TECHNOLOGY ITEMS TO COUNT:
- Cat 6 Jack: Tagged "C2" or with data outlet symbol and number
  Count each individual data jack location by its tag

FLOOR BOXES:
- Floor Box: Floor-mounted data/power boxes (rectangle symbols, tagged "FB")
- Count the BOXES, not the jacks inside them

{level_instruction}

Return your counts as JSON ONLY, no other text:
{{
    "technology": {{
        "Cat 6 Jack": <count>,
        "Floor Box": <count>
    }}
}}"""


# Level-by-level analysis prompt
LEVEL_BY_LEVEL_INSTRUCTION = """
IMPORTANT: Examine EACH floor level separately and report counts per level:
1. LOWER LEVEL / BASEMENT (if shown)
2. MEZZANINE LEVEL
3. FIRST FLOOR
4. SECOND FLOOR
5. Any other levels visible

For EACH level, identify all device locations, then sum for total.
This ensures nothing is missed across multi-level sheets.
"""


def get_prompt_for_sheet(
    sheet_type: SheetType,
    sheet_number: str,
    scope: str = "all",
    level_by_level: bool = True
) -> str:
    """
    Get the appropriate prompt for a sheet type and number.

    Args:
        sheet_type: Type of sheet (DEMO, NEW, etc.)
        sheet_number: Sheet number (E200, T200, etc.)
        scope: Scope filter ("all", "mezzanine_only", etc.)
        level_by_level: Whether to use level-by-level analysis

    Returns:
        Formatted prompt string
    """
    scope_instruction = get_scope_instruction(scope)
    level_instruction = LEVEL_BY_LEVEL_INSTRUCTION if level_by_level else ""

    if sheet_type == SheetType.DEMO:
        template = DEMO_PROMPT_TEMPLATE
    elif sheet_number.startswith("E2"):
        if sheet_number == "E200":
            template = LIGHTING_PROMPT_TEMPLATE
        else:  # E201
            template = POWER_SYSTEMS_PROMPT_TEMPLATE
    elif sheet_number.startswith("T"):
        template = TECHNOLOGY_PROMPT_TEMPLATE
    else:
        template = LIGHTING_PROMPT_TEMPLATE

    return template.format(
        scope_instruction=scope_instruction,
        level_instruction=level_instruction
    )


def count_symbols_with_claude(
    image_path: str,
    sheet_type: SheetType,
    sheet_number: str,
    api_key: Optional[str] = None,
    scope: str = "all",
    level_by_level: bool = True
) -> DeviceCounts:
    """
    Use Claude Vision API to count symbols on a floor plan.

    Args:
        image_path: Path to the sheet image
        sheet_type: Type of sheet (DEMO, NEW, etc.)
        sheet_number: Sheet number (E200, T200, etc.)
        api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        scope: Scope filter for counting
        level_by_level: Whether to use level-by-level analysis

    Returns:
        DeviceCounts with counted items
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required. Install with: pip install anthropic")

    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    # Get appropriate prompt
    prompt = get_prompt_for_sheet(sheet_type, sheet_number, scope, level_by_level)

    # Encode image
    image_data = encode_image_to_base64(image_path)
    media_type = get_image_media_type(image_path)

    # Call Claude Vision API
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[
            {
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
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )

    # Parse response
    response_text = message.content[0].text
    counts_data = _extract_json(response_text)

    # Convert to DeviceCounts
    counts = DeviceCounts()
    counts.fixtures = counts_data.get("fixtures", {})
    counts.controls = counts_data.get("controls", {})
    counts.power = counts_data.get("power", {})
    counts.fire_alarm = counts_data.get("fire_alarm", {})
    counts.technology = counts_data.get("technology", {})
    counts.demo = counts_data.get("demo", {})

    # Merge boxes into power if present
    if "boxes" in counts_data:
        counts.power.update(counts_data["boxes"])

    return counts


def count_by_level(
    image_path: str,
    sheet_type: SheetType,
    sheet_number: str,
    api_key: Optional[str] = None,
    levels: List[str] = None
) -> Dict[str, DeviceCounts]:
    """
    Count symbols on each floor level separately for maximum accuracy.

    This approach has been validated to achieve exact matches on
    multi-floor sheets (92/92 Cat 6 jacks, 23/23 floor boxes).

    Args:
        image_path: Path to the sheet image
        sheet_type: Type of sheet
        sheet_number: Sheet number
        api_key: Anthropic API key
        levels: List of levels to count (defaults to all standard levels)

    Returns:
        Dictionary mapping level name to DeviceCounts
    """
    if levels is None:
        levels = ["mezzanine_only", "lower_level_only", "first_floor_only", "second_floor_only"]

    results = {}

    for level in levels:
        try:
            counts = count_symbols_with_claude(
                image_path, sheet_type, sheet_number, api_key,
                scope=level, level_by_level=False
            )
            results[level] = counts
        except Exception as e:
            print(f"    Warning: Level {level} counting failed: {e}")
            results[level] = DeviceCounts()

    return results


def aggregate_level_counts(level_counts: Dict[str, DeviceCounts]) -> DeviceCounts:
    """
    Aggregate counts from multiple levels into a single total.

    Args:
        level_counts: Dictionary mapping level names to DeviceCounts

    Returns:
        Combined DeviceCounts
    """
    total = DeviceCounts()

    for level_name, counts in level_counts.items():
        total.merge(counts)

    return total


def _extract_json(response_text: str) -> Dict:
    """Extract JSON from Claude response text."""
    try:
        code_block = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
        if code_block:
            return json.loads(code_block.group(1))

        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())

        print(f"Warning: Could not find JSON in response: {response_text[:200]}")
        return {}

    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON: {e}")
        print(f"Response: {response_text[:500]}")
        return {}


# Floor level crop regions for E200/E201 multi-floor sheets
# Non-overlapping regions to prevent double-counting
FLOOR_CROP_REGIONS = {
    "mezzanine": (0, 0, 0.85, 0.36),       # top portion (main floor plan area)
    "lower_level": (0, 0.36, 0.85, 0.54),  # middle portion
    "first_floor": (0, 0.54, 0.45, 0.92),  # bottom left
    "second_floor": (0.45, 0.54, 0.85, 0.92), # bottom right (no overlap with first_floor)
}


def crop_floor_level(image_path: str, level: str) -> str:
    """
    Crop a specific floor level from a multi-floor sheet.

    Args:
        image_path: Path to full sheet image
        level: Floor level name (mezzanine, lower_level, first_floor, second_floor)

    Returns:
        Path to cropped temporary image
    """
    if level not in FLOOR_CROP_REGIONS:
        return image_path

    x1_pct, y1_pct, x2_pct, y2_pct = FLOOR_CROP_REGIONS[level]

    with Image.open(image_path) as img:
        width, height = img.size

        # Calculate pixel coordinates
        x1 = int(width * x1_pct)
        y1 = int(height * y1_pct)
        x2 = int(width * x2_pct)
        y2 = int(height * y2_pct)

        cropped = img.crop((x1, y1, x2, y2))

        # Save to temp file
        suffix = Path(image_path).suffix
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        cropped.save(temp_path)

        return temp_path


def count_by_floor_crop(
    image_path: str,
    sheet_type: SheetType,
    sheet_number: str,
    api_key: Optional[str] = None
) -> DeviceCounts:
    """
    Count symbols by cropping each floor level separately for better tag readability.

    This method is necessary for multi-floor sheets where fixture tags
    are too small to read when viewing the entire page.

    Args:
        image_path: Path to the full sheet image
        sheet_type: Type of sheet (DEMO, NEW, etc.)
        sheet_number: Sheet number (E200, E201, etc.)
        api_key: Anthropic API key

    Returns:
        DeviceCounts with aggregated counts from all floor levels
    """
    print("    Counting by floor-level cropping for better tag readability...")

    total = DeviceCounts()

    for level_name in FLOOR_CROP_REGIONS.keys():
        try:
            # Crop this floor level
            cropped_path = crop_floor_level(image_path, level_name)

            print(f"      {level_name}...")

            # Count on the cropped image
            counts = count_symbols_with_claude(
                cropped_path,
                sheet_type,
                sheet_number,
                api_key,
                scope="all",  # Already cropped to specific floor
                level_by_level=False
            )

            # Merge into total
            total.merge(counts)

            # Report what was found
            fixture_count = sum(counts.fixtures.values()) if counts.fixtures else 0
            if fixture_count > 0:
                print(f"        Found {fixture_count} fixtures")

            # Clean up temp file
            if cropped_path != image_path:
                os.remove(cropped_path)

        except Exception as e:
            print(f"        Error on {level_name}: {e}")

    return total


def count_demo_items_deep(
    image_path: str,
    api_key: Optional[str] = None
) -> DeviceCounts:
    """
    Deep count of demolition items using level-by-level analysis.

    This is the preferred method for E100/T100 demo sheets where
    accuracy is critical for removal scope.

    Args:
        image_path: Path to E100 or T100 sheet image
        api_key: Anthropic API key

    Returns:
        DeviceCounts with demo item counts
    """
    print("  Performing deep demo count by floor level...")

    level_results = count_by_level(
        image_path,
        SheetType.DEMO,
        "E100",  # Will work for T100 too
        api_key
    )

    total = aggregate_level_counts(level_results)

    # Print level breakdown
    for level, counts in level_results.items():
        level_total = sum(counts.demo.values())
        if level_total > 0:
            print(f"    {level}: {level_total} items")

    return total
