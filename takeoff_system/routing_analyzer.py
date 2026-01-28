"""Conduit and wire routing analysis module.

This module estimates conduit runs and wire lengths from floor plans
using AI vision analysis, PDF vector extraction, and device-based estimation methods.
"""
import base64
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image

from .models import ConduitCounts, RoutingData
from .pdf_extractor import extract_conduit_lengths, analyze_drawing_elements


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


# Prompt for AI-based conduit routing estimation
CONDUIT_ROUTING_PROMPT = """You are an expert electrical estimator analyzing a floor plan to estimate conduit runs.

This floor plan shows electrical devices and their connections. I need you to estimate the total conduit lengths.

WHAT TO LOOK FOR:
1. CONDUIT RUNS are shown as lines connecting devices to panels/junction boxes
2. Lines may be solid (new work) or dashed (existing/demo)
3. Look for conduit size notations: 3/4", 1", 1-1/4", etc.
4. Panel locations are typically marked with rectangles and "PANEL" labels

ESTIMATION APPROACH:
1. Identify the electrical panel location(s)
2. Trace conduit paths from panels to device clusters
3. Estimate lengths based on the floor plan scale (typically 1/8" = 1'-0")
4. Consider:
   - Horizontal runs along ceilings/walls
   - Drops to devices (~8-10 ft typical)
   - Turns and offsets add ~20%

TYPICAL CONDUIT SIZES:
- 3/4" EMT: Lighting circuits (most common, ~75% of runs)
- 1" EMT: Power circuits, larger loads (~20% of runs)
- 1-1/4" EMT or larger: Feeders (~5% of runs)

For this floor plan, estimate:
1. Total length of each conduit size in FEET
2. Number of major routing paths identified

The client's material list shows approximately:
- 3/4" EMT: 3,773 ft
- 1" EMT: 790 ft

Please analyze the floor plan and provide your estimates.

Return ONLY JSON in this exact format:
```json
{
    "conduit_by_size": {
        "3/4\\"": <feet>,
        "1\\"": <feet>,
        "1-1/4\\"": <feet>
    },
    "analysis": {
        "panels_found": <count>,
        "major_routes": <count>,
        "estimated_drops": <count>,
        "scale_used": "<scale description>",
        "confidence": "<low/medium/high>"
    },
    "notes": "<observations about routing>"
}
```"""


WIRE_CALCULATION_PROMPT = """You are an electrical estimator calculating wire quantities from conduit data.

Given conduit lengths, calculate wire requirements using these rules:

WIRE SIZING:
- 3/4" EMT typically carries #12 THHN (20A circuits)
- 1" EMT typically carries #10 THHN (30A circuits) or multiple #12
- 1-1/4"+ EMT carries #8, #6, or larger feeders

WIRE MULTIPLIERS (per foot of conduit):
- Lighting circuits (#12): 2.2x (hot + neutral + ground + 10% waste)
- Power circuits (#10): 2.5x (same plus extra for larger gauge)
- Feeder circuits: Per panel schedule (typically 4x for 3-phase)

COLOR CODING:
- Black: Hot conductors
- White: Neutral
- Green: Ground
- Red/Blue: Additional phases or switch legs

Return calculated wire quantities in feet.
"""


def estimate_conduit_with_ai(
    image_path: str,
    api_key: Optional[str] = None
) -> ConduitCounts:
    """
    Use Claude Vision to estimate conduit runs from a floor plan.

    Args:
        image_path: Path to floor plan image (E200 or E201)
        api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)

    Returns:
        ConduitCounts with estimated lengths
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
                    {"type": "text", "text": CONDUIT_ROUTING_PROMPT}
                ],
            }],
        )
    finally:
        if temp_path:
            os.remove(temp_path)

    # Parse response
    response_text = message.content[0].text
    data = _extract_json(response_text)

    result = ConduitCounts()
    result.conduit_by_size = data.get("conduit_by_size", {})

    return result


def estimate_conduit_from_devices(
    device_counts: Dict[str, int],
    building_sqft: int = 10000,
    floors: int = 2
) -> ConduitCounts:
    """
    Estimate conduit lengths based on device counts and building size.

    This is a fallback method when AI routing analysis isn't available
    or reliable.

    Industry rules of thumb:
    - ~1 ft conduit per sq ft for lighting
    - ~0.5 ft conduit per sq ft for power
    - Adjust by device density

    Args:
        device_counts: Dictionary of device counts
        building_sqft: Total building square footage
        floors: Number of floors

    Returns:
        ConduitCounts with estimated lengths
    """
    # Count devices by category
    lighting_devices = (
        device_counts.get("F2", 0) +
        device_counts.get("F3", 0) +
        device_counts.get("F4", 0) +
        device_counts.get("F4E", 0) +
        device_counts.get("F5", 0) +
        device_counts.get("F7", 0) +
        device_counts.get("F7E", 0) +
        device_counts.get("F8", 0) +
        device_counts.get("F9", 0) +
        device_counts.get("X1", 0) +
        device_counts.get("X2", 0) +
        device_counts.get("Ceiling Occupancy Sensor", 0) +
        device_counts.get("Wall Occupancy Sensor", 0) +
        device_counts.get("Daylight Sensor", 0)
    )

    power_devices = (
        device_counts.get("Duplex Receptacle", 0) +
        device_counts.get("GFI Receptacle", 0) +
        device_counts.get("SP Switch", 0) +
        device_counts.get("3-Way Switch", 0)
    )

    data_devices = device_counts.get("Cat 6 Jack", 0)

    # Base estimation from building size
    base_lighting_conduit = building_sqft * 0.4  # 0.4 ft per sqft
    base_power_conduit = building_sqft * 0.2     # 0.2 ft per sqft

    # Adjust by device density
    lighting_density = lighting_devices / (building_sqft / 1000)
    power_density = power_devices / (building_sqft / 1000)

    # Density multipliers (more devices = more conduit)
    lighting_multiplier = 1.0 + (lighting_density - 5) * 0.1  # 5 devices per 1000 sqft baseline
    power_multiplier = 1.0 + (power_density - 4) * 0.1       # 4 devices per 1000 sqft baseline

    # Calculate totals
    lighting_conduit = int(base_lighting_conduit * max(0.5, lighting_multiplier))
    power_conduit = int(base_power_conduit * max(0.5, power_multiplier))

    # Add vertical runs for multiple floors
    vertical_runs = (floors - 1) * 50  # 50 ft per floor for risers

    result = ConduitCounts()
    result.conduit_by_size = {
        '3/4"': lighting_conduit + vertical_runs,
        '1"': power_conduit,
    }

    return result


def calculate_wire_from_conduit(
    conduit_counts: ConduitCounts,
    circuit_breakdown: Dict[str, float] = None
) -> Dict[str, int]:
    """
    Calculate wire quantities from conduit lengths.

    Args:
        conduit_counts: ConduitCounts with conduit lengths by size
        circuit_breakdown: Optional breakdown of circuit types
                          e.g. {"lighting": 0.6, "power": 0.3, "feeder": 0.1}

    Returns:
        Dictionary of wire sizes to lengths in feet
    """
    if circuit_breakdown is None:
        circuit_breakdown = {
            "lighting": 0.6,  # 60% lighting (#12)
            "power": 0.3,     # 30% power (#10)
            "feeder": 0.1,    # 10% feeder (#8 or larger)
        }

    wire = {}
    conduit = conduit_counts.conduit_by_size

    total_34 = conduit.get('3/4"', 0)
    total_1 = conduit.get('1"', 0)
    total_114 = conduit.get('1-1/4"', 0)

    # #12 THHN from 3/4" conduit (lighting)
    # Multiplier: 2.2 (1 hot + 1 neutral + 1 ground + waste)
    wire["#12 THHN Black"] = int(total_34 * 1.1)
    wire["#12 THHN White"] = int(total_34 * 1.0)
    wire["#12 THHN Green"] = int(total_34 * 1.0)

    # #10 THHN from 1" conduit (power)
    # Multiplier: 2.5 for larger gauge
    wire["#10 THHN Black"] = int(total_1 * 1.2)
    wire["#10 THHN White"] = int(total_1 * 1.1)
    wire["#10 THHN Green"] = int(total_1 * 1.1)

    # #8 THHN from 1-1/4" conduit (feeders)
    if total_114 > 0:
        wire["#8 THHN Black"] = int(total_114 * 1.3)
        wire["#8 THHN White"] = int(total_114 * 1.2)
        wire["#8 THHN Green"] = int(total_114 * 1.2)

    return wire


def estimate_conduit_from_pdf_vectors(
    pdf_path: str,
    page_num: int,
    width_mapping: Optional[Dict[float, str]] = None
) -> ConduitCounts:
    """
    Estimate conduit lengths from PDF vector paths using PyMuPDF.

    This extracts line drawings from the PDF and maps line widths to conduit sizes.
    More accurate than vision-based estimation when the PDF has proper vector data.

    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-indexed)
        width_mapping: Optional mapping of line widths to conduit sizes

    Returns:
        ConduitCounts with estimated conduit lengths
    """
    try:
        conduit_by_size = extract_conduit_lengths(pdf_path, page_num, width_mapping)

        result = ConduitCounts()
        result.conduit_by_size = conduit_by_size

        return result
    except ImportError:
        print("    Warning: PyMuPDF not installed, cannot extract vector paths")
        return ConduitCounts()
    except Exception as e:
        print(f"    Warning: PDF vector extraction failed: {e}")
        return ConduitCounts()


def analyze_pdf_drawing_elements(
    pdf_path: str,
    page_num: int
) -> dict:
    """
    Analyze drawing elements on a PDF page for calibration.

    Returns statistics about line widths, colors, and counts to help
    determine the correct width-to-conduit-size mapping.

    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-indexed)

    Returns:
        Dictionary with element statistics
    """
    try:
        return analyze_drawing_elements(pdf_path, page_num)
    except ImportError:
        return {"error": "PyMuPDF not installed"}
    except Exception as e:
        return {"error": str(e)}


def analyze_routing_complete(
    e200_path: str,
    e201_path: str,
    device_counts: Dict[str, int],
    building_sqft: int = 10000,
    api_key: Optional[str] = None,
    use_ai: bool = True,
    pdf_path: Optional[str] = None,
    use_pdf_vectors: bool = False
) -> RoutingData:
    """
    Complete routing analysis combining PDF vectors, AI vision, and device-based estimation.

    Args:
        e200_path: Path to E200 (lighting) floor plan image
        e201_path: Path to E201 (power) floor plan image
        device_counts: Device counts from symbol counting
        building_sqft: Building size for device-based estimation
        api_key: Anthropic API key
        use_ai: Whether to attempt AI-based estimation
        pdf_path: Path to original PDF for vector extraction
        use_pdf_vectors: Whether to attempt PDF vector extraction

    Returns:
        RoutingData with conduit and wire estimates
    """
    result = RoutingData()
    combined_conduit = ConduitCounts()

    # Try PDF vector extraction first (most accurate when available)
    if use_pdf_vectors and pdf_path:
        print("  Attempting PDF vector extraction for conduit lengths...")
        try:
            # E200 is typically page 3 (0-indexed: 2)
            # E201 is typically page 4 (0-indexed: 3)
            e200_conduit = estimate_conduit_from_pdf_vectors(pdf_path, 2)
            e201_conduit = estimate_conduit_from_pdf_vectors(pdf_path, 3)

            for conduit in [e200_conduit, e201_conduit]:
                for size, length in conduit.conduit_by_size.items():
                    combined_conduit.conduit_by_size[size] = (
                        combined_conduit.conduit_by_size.get(size, 0) + length
                    )

            if combined_conduit.conduit_by_size:
                result.estimated_method = "pdf_vectors"
                print(f"    PDF vector extraction: {combined_conduit.conduit_by_size}")
        except Exception as e:
            print(f"    Warning: PDF vector extraction failed: {e}")

    # Fall back to AI vision if PDF vectors didn't work
    if not combined_conduit.conduit_by_size and use_ai:
        print("  Analyzing E200 (Lighting) routing with AI...")
        try:
            lighting_conduit = estimate_conduit_with_ai(e200_path, api_key)
            for size, length in lighting_conduit.conduit_by_size.items():
                combined_conduit.conduit_by_size[size] = (
                    combined_conduit.conduit_by_size.get(size, 0) + length
                )
            result.estimated_method = "ai_vision"
        except Exception as e:
            print(f"    Warning: AI routing failed for E200: {e}")
            use_ai = False

        if use_ai:
            print("  Analyzing E201 (Power) routing with AI...")
            try:
                power_conduit = estimate_conduit_with_ai(e201_path, api_key)
                for size, length in power_conduit.conduit_by_size.items():
                    combined_conduit.conduit_by_size[size] = (
                        combined_conduit.conduit_by_size.get(size, 0) + length
                    )
            except Exception as e:
                print(f"    Warning: AI routing failed for E201: {e}")

    # If all else failed, use device-based estimation
    if not combined_conduit.conduit_by_size:
        print("  Using device-based conduit estimation...")
        combined_conduit = estimate_conduit_from_devices(device_counts, building_sqft)
        result.estimated_method = "device_based"

    # Calculate wire from conduit
    print("  Calculating wire quantities...")
    combined_conduit.wire_by_size = calculate_wire_from_conduit(combined_conduit)

    result.conduit = combined_conduit
    return result


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


def manual_conduit_input(
    conduit_34: int = 0,
    conduit_1: int = 0,
    conduit_114: int = 0,
    conduit_112: int = 0
) -> ConduitCounts:
    """
    Create ConduitCounts from manual user input.

    This is a last-resort method when neither AI nor device-based
    estimation is satisfactory.

    Args:
        conduit_34: 3/4" EMT in feet
        conduit_1: 1" EMT in feet
        conduit_114: 1-1/4" EMT in feet
        conduit_112: 1-1/2" EMT in feet

    Returns:
        ConduitCounts with manually specified lengths
    """
    result = ConduitCounts()

    if conduit_34 > 0:
        result.conduit_by_size['3/4"'] = conduit_34
    if conduit_1 > 0:
        result.conduit_by_size['1"'] = conduit_1
    if conduit_114 > 0:
        result.conduit_by_size['1-1/4"'] = conduit_114
    if conduit_112 > 0:
        result.conduit_by_size['1-1/2"'] = conduit_112

    # Calculate wire
    result.wire_by_size = calculate_wire_from_conduit(result)

    return result
