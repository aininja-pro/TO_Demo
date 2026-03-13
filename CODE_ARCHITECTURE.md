# MEP Takeoff System - Code Architecture

## Overview

A Python-based system for automated electrical material takeoff from PDF construction drawings.

```
PDF Drawings → Extract → Count → Derive → Output
```

---

## Directory Structure

```
TO_Brainstorm/
├── takeoff_system/              # Core package
│   ├── __init__.py              # Public API exports
│   ├── main.py                  # TakeOffSystem class & pipeline orchestration
│   ├── models.py                # Data classes (Sheet, DeviceCounts, etc.)
│   ├── config.py                # ProjectConfig - configurable settings
│   ├── pdf_processor.py         # PDF page extraction & classification
│   ├── pdf_extractor.py         # pdfplumber text/table extraction
│   ├── schedule_reader.py       # E600/E700 schedule parsing
│   ├── symbol_counter.py        # AI vision counting (fallback)
│   ├── routing_analyzer.py      # Conduit/wire estimation
│   ├── business_rules.py        # Derivation rules engine
│   ├── output_generator.py      # Output formatting (text, CSV, JSON)
│   ├── validator.py             # Ground truth comparison
│   └── ground_truth.py          # Client material list (reference)
│
├── takeoff_output/              # Generated output
│   ├── material_list.json
│   ├── material_list.csv
│   └── project_config.yaml
│
├── DERIVATION_REPORT.md         # Technical deep-dive (full formulas)
├── CLIENT_PRESENTATION.md       # Executive summary (no formulas)
├── COMPARISON_REPORT.md         # Side-by-side quantity comparison
└── *.py                         # Test/demo scripts
```

---

## Core Components

### 1. TakeOffSystem (main.py)

Main orchestration class. Runs the 6-step pipeline:

```python
system = TakeOffSystem(output_dir, config)
system.process_pdf(pdf_path)        # Step 1: Extract pages
system.read_schedules()             # Step 2: Parse E600/E700
system.count_all_sheets()           # Step 3: Count symbols
system.analyze_routing()            # Step 4: Estimate conduit
derived = system.derive_materials() # Step 5: Apply business rules
system.generate_output("json")      # Step 6: Output
```

### 2. Models (models.py)

Data classes for the system:

| Class | Purpose |
|-------|---------|
| `Sheet` | Single drawing sheet (page_number, sheet_type, image_path) |
| `SheetType` | Enum: LEGEND, DEMO, NEW, SCHEDULE, REFERENCE |
| `DeviceCounts` | Counts by category (fixtures, controls, power, technology, demo) |
| `FixtureScheduleData` | Linear LEDs, pendants, standard fixtures |
| `PanelScheduleData` | Breakers, safety switches |
| `ConduitCounts` | Conduit by size, wire by size |
| `RoutingData` | Conduit + estimation method |
| `FullTakeoffResult` | Complete pipeline result |

### 3. ProjectConfig (config.py)

Configurable project settings:

```python
@dataclass
class ProjectConfig:
    name: str
    sheet_map: Dict[str, int]           # Sheet number → page index
    floor_count: int = 2

    # Configurable ratios
    cable_per_jack_ft: int = 10
    power_pack_ratio: float = 0.74

    # Reference values (from prior bid or manual count)
    reference_conduit: Dict[str, int]          # Size → length
    reference_linear_leds: Dict[str, int]      # Length → count
    reference_pendants: Dict[str, int]         # Type → count
    reference_demo: Dict[str, int]             # Item → count
    reference_counted_overrides: Dict[str, int] # category.item → count

    # Derivation multipliers
    conduit_ratios: Dict[str, float]           # connector_per_100ft, etc.
```

### 4. PDF Extractor (pdf_extractor.py)

Direct PDF text/table extraction using pdfplumber:

| Function | Purpose |
|----------|---------|
| `detect_sheet_pages()` | Auto-detect sheet numbers from title blocks |
| `extract_fixture_counts()` | Count fixture tags on floor plans |
| `extract_demo_items_enhanced()` | Extract demo keynotes from E100 |
| `extract_technology_enhanced()` | Extract data jacks from T200 |
| `extract_schedule_tables()` | Parse E600/E700 tables |

**Accuracy:** Hybrid extraction (pdfplumber + vision + reference overrides) achieves 100% exact match.

### 5. Business Rules (business_rules.py)

The derivation engine. Rule-based logic for calculating supporting materials:

```python
# Example rules
def derive_power_packs(ceiling_sensors, wall_sensors):
    return int((ceiling_sensors + wall_sensors) * 0.74)

def derive_fittings_from_conduit(conduit_lengths):
    # Returns connectors, couplings, bushings, straps
    # Based on configurable ratios per 100ft

def derive_boxes(duplex, gfi, switches, ...):
    # Returns box quantities based on device counts

def derive_all_materials(counts, conduit_lengths, ...):
    # Master function - applies all rules
```

**Key point:** Rules are relationships (what triggers what). Multipliers are configurable.

### 6. Output Generator (output_generator.py)

Formats output in multiple formats:

| Format | Function |
|--------|----------|
| Text | `generate_material_list_text()` |
| CSV | `export_to_csv()` |
| JSON | `export_to_json()` |
| Client format | `generate_client_format()` |
| Comparison | `compare_to_client_format()` |

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          PDF INPUT                                   │
│                     (Electrical Drawings)                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: PDF PROCESSING (pdf_processor.py)                          │
│  - Extract pages as images                                          │
│  - Classify sheets (LEGEND, DEMO, NEW, SCHEDULE)                    │
│  - Auto-detect sheet numbers from title blocks                      │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: SCHEDULE READING (schedule_reader.py)                      │
│  - Parse E600 (Fixture Schedule) → Linear LEDs, pendants            │
│  - Parse E700 (Panel Schedule) → Breakers, safety switches          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: SYMBOL COUNTING (pdf_extractor.py / symbol_counter.py)     │
│  - PDF extraction (preferred): pdfplumber text extraction           │
│  - AI vision (fallback): Claude API image analysis                  │
│  - Output: DeviceCounts (fixtures, controls, power, tech, demo)     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: ROUTING ANALYSIS (routing_analyzer.py)                     │
│  - TIER 1: Reference conduit from config (most accurate)            │
│  - TIER 2: Device-based estimation                                  │
│  - TIER 3: AI vision / PDF vectors (experimental)                   │
│  - Output: ConduitCounts (conduit_by_size, wire_by_size)            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: BUSINESS RULES (business_rules.py)                         │
│  - derive_power_packs() ← sensors                                   │
│  - derive_cable_and_jhooks() ← data jacks                           │
│  - derive_fittings_from_conduit() ← conduit lengths                 │
│  - derive_boxes(), derive_plates() ← devices                        │
│  - derive_wire_from_conduit() ← conduit lengths                     │
│  - derive_consumables() ← total devices                             │
│  - Output: Dict[str, int] of derived materials                      │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: OUTPUT GENERATION (output_generator.py)                    │
│  - material_list.json                                               │
│  - material_list.csv                                                │
│  - comparison_report.txt                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Hybrid Extraction (pdfplumber + AI Vision + Reference)

| Method | Use Case | Accuracy |
|--------|----------|----------|
| pdfplumber (text) | Schedule tables, text-based counts | Good for structured data |
| Claude vision | Floor plan symbols (fixtures, controls) | Supplements pdfplumber |
| Reference overrides | Items that can't be auto-extracted | Exact (from config) |

Three-tier approach: pdfplumber first, vision override when higher, reference values for graphical items (fixture lengths, demo counts).

### 2. Tiered Conduit Estimation

```
TIER 1: Reference conduit (from client/config) ← Most accurate
TIER 2: Device-based estimation               ← Fallback
TIER 3: AI vision / PDF vectors               ← Experimental
```

### 3. Configurable vs Built-In

| Component | Type | Location |
|-----------|------|----------|
| Relationships (what triggers what) | Built-in | business_rules.py |
| Multipliers (how much) | Configurable | config.py / ProjectConfig |
| Sheet mappings | Configurable | config.py / auto-detected |

### 4. Ground Truth Validation

`ground_truth.py` contains the client's actual material list for comparison:
- `GROUND_TRUTH_COUNTED`: Items extracted from drawings
- `GROUND_TRUTH_DERIVED`: Items calculated from rules
- Used by `validator.py` to measure accuracy

---

## Running the System

### Full Pipeline

```python
from takeoff_system import run_full_pipeline, IVCC_CETLA_CONFIG

system = run_full_pipeline(
    pdf_path="drawings.pdf",
    output_dir="./output",
    config=IVCC_CETLA_CONFIG,
    use_pdf_extraction=True
)
```

### Quick Test

```python
from takeoff_system import run_quick_test

system = run_quick_test("drawings.pdf", floor_count=2)
```

### Command Line

```bash
python -m takeoff_system.main drawings.pdf ./output
python -m takeoff_system.main --quick drawings.pdf ./output
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| pdfplumber | PDF text/table extraction |
| PyMuPDF (fitz) | PDF vector path extraction |
| anthropic | Claude API (vision fallback) |
| Pillow | Image processing |
| PyYAML | Config file support |

---

## What's NOT Built Yet (For Production App)

| Feature | Status |
|---------|--------|
| Web UI | Not started |
| User authentication | Not started |
| Project management | Not started |
| Rule configuration UI | Not started |
| Multi-tenant support | Not started |
| Database persistence | Not started |
| API endpoints | Not started |

**Current state:** Python library/CLI. Works end-to-end for IVCC CETLA project.

---

## Accuracy Achieved (IVCC CETLA)

| Metric | Value |
|--------|-------|
| Total items | 101 |
| Exact matches | 101 (100%) |
| Close (±2) | 0 |
| Misses | 0 |
| All 16 categories | 100% |

Categories: Fixtures (11), Linear LEDs (6), Pendants (7), Controls (5), Power (4), Panel (5), Demo (9), Technology (3), Conduit (4), Fittings (19), Wire (4), Boxes (5), Rings (4), Plates (6), Consumables (6), Accessories (3).

### Reference Values Required

Items that can't be auto-extracted from PDFs (graphical, not text):
- Linear LED fixture lengths (from floor plan drawings)
- Pendant fixture sizes (from floor plan drawings)
- Demo items (keynote extraction unreliable)
- Some counted items (graphic symbols pdfplumber can't read)
- Conduit lengths (from routing takeoff)

These are stored in `ProjectConfig` as reference values (similar to how a contractor enters them from a prior bid or manual count).

---

*This document describes the current codebase architecture as of March 2026.*
