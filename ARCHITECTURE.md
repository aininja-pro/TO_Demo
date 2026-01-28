# MEP TakeOff System - Architecture Documentation

## Overview

The MEP TakeOff System is an AI-powered tool that reads electrical construction drawing PDFs and generates material lists for estimating. It uses Claude Vision API to count symbols on floor plans and applies business rules to derive supporting materials.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INPUT                                        │
│  PDF of Electrical Drawings                                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: PDF PROCESSING (pdf_processor.py)                          │
│  - Convert PDF to PNG images (one per page)                         │
│  - Extract title block from each page                               │
│  - Classify sheet type (DEMO/NEW/LEGEND/REFERENCE)                  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: SYMBOL COUNTING (symbol_counter.py)                        │
│  - For each NEW sheet (E200, E201, T200-T400):                      │
│    - Send to Claude Vision with symbol library context              │
│    - Count each device type                                         │
│    - Return structured JSON counts                                  │
│  - For each DEMO sheet (E100, T100):                                │
│    - Count demo items separately                                    │
│  - Aggregate counts across all sheets                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: BUSINESS RULES (business_rules.py)                         │
│  - Apply rules to device counts                                     │
│  - Calculate: boxes, rings, plates, power packs, cable, j-hooks     │
│  - Estimate conduit and wire (approximate)                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: VALIDATION (validator.py)                                  │
│  - Compare generated counts to ground truth                         │
│  - Calculate accuracy metrics                                       │
│  - Flag discrepancies for review                                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: OUTPUT (output_generator.py)                               │
│  - Generate material list in client's format                        │
│  - Include NEW materials and DEMO items separately                  │
│  - Export to text, CSV, or JSON                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
takeoff_system/
├── __init__.py           # Package marker
├── models.py             # Data classes (Sheet, DeviceCounts, etc.)
├── pdf_processor.py      # PDF → images, sheet classification
├── symbol_counter.py     # AI vision counting with Claude API
├── business_rules.py     # Derive supporting materials
├── ground_truth.py       # Known correct counts for validation
├── validator.py          # Compare generated vs expected
├── output_generator.py   # Format material list
└── main.py               # Orchestration
```

## Key Concepts

### Sheet Classification
Sheets are classified by their number prefix:
- `xxx100` = Demolition (E100, T100) - items to remove
- `xxx200-599` = New Work (E200, E201, T200, etc.) - items to install
- `xxx000` = Legends (E000, T000) - symbol definitions
- `xxx600+` = Reference (E600, E700) - schedules and details

**Critical Rule:** DEMO and NEW counts are kept separate. DEMO items are for removal labor pricing only.

### Symbol Types

**Fixtures (from E200):**
| Tag | Description |
|-----|-------------|
| F2 | 2'x4' LED Lay-In |
| F3 | 4' LED Strip |
| F4 | LED Recessed Downlight |
| F4E | Downlight w/Emergency (E = emergency, NOT existing) |
| F5 | 4' Vapor Tight |
| F7/F7E | 2'x4' Surface LED |
| F8 | 2'x2' LED Lay-In |
| F9 | 6' Linear LED |
| X1/X2 | Exit Signs |

**Controls:**
| Symbol | Description |
|--------|-------------|
| OC (ceiling) | Occupancy Sensor |
| OC (wall) | Wall Occupancy Sensor |
| LS | Daylight Sensor |
| D | Wireless Dimmer |

**Power Devices (from E201):**
- Duplex Receptacle, GFI, SP Switch, 3-Way Switch

**Technology (from T200):**
- Data Jacks (Cat 6)

### Business Rules (Validated)

| Rule | Formula | Example |
|------|---------|---------|
| Power Packs | `(ceiling_sensors + wall_sensors) × 0.74` | (16 + 3) × 0.74 = 14 ✓ |
| Cat 6 Cable | `data_jacks × 10` | 92 × 10 = 920 ft ✓ |
| J-Hooks | `cable_feet ÷ 4` | 920 ÷ 4 = 230 ✓ |
| Fixture Whips | `F2_count + F8_count` | Lay-in fixtures get whips |

### Scope Detection Rules

1. **Line Weight:** THICK = New, THIN = Existing, DASHED = Demo
2. **Tag Suffix:** `-E` = Existing (exclude), but `F4E`/`F7E` = Emergency (include)
3. **Sheet Type:** E100/T100 = Demo, E200/T200 = New

## Data Flow

1. **Input:** Electrical construction PDF
2. **PDF Processing:** Extract pages as images, classify by sheet number
3. **AI Vision:** Send images to Claude with category-specific prompts
4. **Aggregation:** Combine counts from all sheets, keeping NEW/DEMO separate
5. **Business Rules:** Derive boxes, plates, rings, cable, etc.
6. **Validation:** Compare to ground truth (when available)
7. **Output:** Material list in text/CSV/JSON format

## Configuration

### Environment Variables
- `ANTHROPIC_API_KEY`: Required for AI vision counting

### Dependencies
- `anthropic`: Claude API client
- `pdf2image`: PDF to image conversion (requires poppler)
- `Pillow`: Image processing

## Usage

### Demo Mode (no API required)
```bash
python run_demo.py
```

### Full Pipeline
```bash
export ANTHROPIC_API_KEY='your-key'
python run_demo.py --full
```

### Python API
```python
from takeoff_system.main import run_full_pipeline
system = run_full_pipeline('/path/to/drawings.pdf')
```

## Ground Truth (IVCC CETLA Project)

The ground truth values in `ground_truth.py` come from the client's actual material list. Key targets:

| Category | Item | Count |
|----------|------|-------|
| Fixtures | F2 | 6 |
| Fixtures | F4 | 10 |
| Controls | Ceiling OC | 16 |
| Power | Duplex | 37 |
| Technology | Cat 6 Jack | 92 |

## Accuracy Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Fixture count | 90%+ exact | Easy to identify |
| Receptacle count | 95%+ | Well-defined symbols |
| Control count | 95%+ | Consistent markings |
| Overall match | 85%+ | Acceptable for estimating |

## Known Limitations

1. **Linear Fixtures:** Complex pendant configurations (F11-4X4, etc.) require careful counting
2. **Conduit/Wire:** Difficult to derive without routing knowledge
3. **Multi-page Overlap:** Some devices may appear on multiple sheets
4. **Symbol Variations:** Different drawing sets may use different symbols

## Future Improvements

1. **Legend Parsing:** Automatically extract symbol definitions from E000/T000
2. **Title Block OCR:** Extract sheet numbers from images instead of manual mapping
3. **Confidence Scores:** Report AI confidence for each count
4. **Human Review:** Semi-automated workflow with human verification
