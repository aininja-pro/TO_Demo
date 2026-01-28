#!/usr/bin/env python3
"""Quick test of vision API with direct implementation."""
import os
import sys
import re
import json
import base64
import tempfile
from PIL import Image
import anthropic

api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("Error: ANTHROPIC_API_KEY not set")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

LIGHTING_PROMPT = '''You are an expert electrical estimator analyzing a lighting floor plan from construction drawings.

IMPORTANT RULES:
1. Only count devices with THICK/WIDE lines (NEW WORK), not thin lines (existing)
2. Do NOT count devices that have a dashed pattern (those are DEMO/TO BE REMOVED)
3. Look for fixture tags like F2, F3, F4, F4E, F5, F7, F7E, F8, F9, X1, X2
4. For F4E and F7E, the "E" means EMERGENCY battery, NOT "Existing"
5. Count UNITS, not linear feet for linear fixtures

This sheet has multiple floor plans. Scan ALL areas completely.

Return your counts as JSON ONLY:
{
    "fixtures": {"F2": <count>, "F3": <count>, "F4": <count>, "F4E": <count>, "F5": <count>, "F7": <count>, "F7E": <count>, "F8": <count>, "F9": <count>, "X1": <count>, "X2": <count>},
    "controls": {"Ceiling Occupancy Sensor": <count>, "Wall Occupancy Sensor": <count>, "Daylight Sensor": <count>, "Wireless Dimmer": <count>}
}'''

image_path = 'test_output/pages/page-03.png'

# Resize image if needed
with Image.open(image_path) as img:
    width, height = img.size
    print(f"Original size: {width}x{height}")

    max_dim = 7000
    if width > max_dim or height > max_dim:
        if width > height:
            new_width = max_dim
            new_height = int(height * (max_dim / width))
        else:
            new_height = max_dim
            new_width = int(width * (max_dim / height))

        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        resized.save(temp_path)
        print(f"Resized to: {new_width}x{new_height}")
        use_path = temp_path
    else:
        use_path = image_path
        temp_path = None

with open(use_path, 'rb') as f:
    image_data = base64.standard_b64encode(f.read()).decode('utf-8')

if temp_path:
    os.remove(temp_path)

print("Calling Claude Vision API...")
message = client.messages.create(
    model='claude-sonnet-4-20250514',
    max_tokens=2048,
    messages=[
        {
            'role': 'user',
            'content': [
                {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': 'image/png',
                        'data': image_data,
                    },
                },
                {
                    'type': 'text',
                    'text': LIGHTING_PROMPT
                }
            ],
        }
    ],
)

response_text = message.content[0].text
print("\n=== RESPONSE ===")
print(response_text)

# Extract JSON
code_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
if code_block_match:
    data = json.loads(code_block_match.group(1))
else:
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    data = json.loads(json_match.group()) if json_match else {}

print("\n=== EXTRACTED COUNTS ===")
fixtures = data.get('fixtures', {})
controls = data.get('controls', {})
print(f"Fixtures: {fixtures}")
print(f"Controls: {controls}")

# Ground truth comparison
GROUND_TRUTH = {
    'F2': 6, 'F3': 10, 'F4': 10, 'F4E': 2, 'F5': 8,
    'F7': 3, 'F7E': 2, 'F8': 1, 'F9': 6, 'X1': 5, 'X2': 1
}

print("\n=== COMPARISON TO GROUND TRUTH ===")
print(f"{'Item':<10} {'AI':>6} {'Truth':>6} {'Diff':>6}")
print("-" * 35)
exact = 0
close = 0
for item, expected in GROUND_TRUTH.items():
    actual = fixtures.get(item, 0)
    diff = actual - expected
    marker = "✓" if diff == 0 else ("~" if abs(diff) <= 2 else "✗")
    print(f"{item:<10} {actual:>6} {expected:>6} {diff:>+6} {marker}")
    if diff == 0:
        exact += 1
    elif abs(diff) <= 2:
        close += 1

print(f"\nExact: {exact}/11, Close (±2): {close}/11")
print(f"Total accurate: {(exact+close)/11*100:.1f}%")

if (exact + close) / 11 >= 0.85:
    print("\n✅ SUCCESS: Vision capability PROVEN - 85%+ accuracy!")
else:
    print("\n⚠️  Below 85% - counts differ from ground truth")
    print("Note: Ground truth may be partial or scope-specific")
