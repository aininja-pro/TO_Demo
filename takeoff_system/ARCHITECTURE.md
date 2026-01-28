# MEP TakeOff System - Architecture Documentation

## Overview

The MEP TakeOff System is a production-ready AI system that generates complete electrical material lists from construction PDF drawings. It matches what an estimator produces manually (119 line items, 28,000+ units).

## System Architecture

```
PDF Input
    │
    ├─→ [PDF Processor] → Sheet classification (Legend/Demo/New/Schedule/Reference)
    │
    ├─→ [Schedule Reader] → Fixture quantities, panel breakers (E600, E700)
    │       │
    │       └─→ Linear LEDs, F10/F11 pendants, safety switches, breakers
    │
    ├─→ [Symbol Counter] → Floor plan devices (E100, E200, E201, T200)
    │       │
    │       └─→ Fixtures, controls, receptacles, switches, data jacks, demo
    │
    ├─→ [Routing Analyzer] → Conduit/wire lengths (E200, E201)
    │       │
    │       └─→ EMT footage, wire runs, vertical drops
    │
    └─→ [Business Rules Engine]
            │
            ├─→ Fittings (connectors, couplings, bushings, straps)
            ├─→ Boxes & Rings (4" square, 4-11/16", plaster rings)
            ├─→ Plates & Covers (duplex, decora, switch, blank)
            ├─→ Consumables (wirenuts, screws, ground hardware)
            └─→ Accessories (whips, pendants, j-hooks, pull line)
                    │
                    ▼
            [Material List Output]
```

## Module Descriptions

### 1. models.py
Data models for the entire system:
- `SheetType`: Enum for sheet classification (LEGEND, DEMO, NEW, SCHEDULE, REFERENCE)
- `Sheet`: Individual sheet metadata
- `DeviceCounts`: Device counts by category
- `FixtureScheduleData`: Extracted fixture schedule data
- `PanelScheduleData`: Extracted panel schedule data
- `ConduitCounts`: Conduit and wire lengths
- `RoutingData`: Complete routing analysis results
- `FullTakeoffResult`: Complete pipeline output
- `ValidationResult`: Comparison to ground truth

### 2. pdf_processor.py
PDF extraction and classification:
- `extract_pages_from_pdf()`: Convert PDF pages to images
- `classify_pages()`: Assign sheet types based on numbers
- `get_sheets_by_type()`: Filter sheets by type

### 3. schedule_reader.py
AI vision-based schedule parsing:
- `read_fixture_schedule()`: Parse E600 LED luminaire schedule
- `read_panel_schedule()`: Parse E700 panel breaker schedule
- `read_all_schedules()`: Combined schedule reading

### 4. symbol_counter.py
AI vision-based symbol counting:
- `count_symbols_with_claude()`: Count devices on floor plans
- `count_by_level()`: Level-by-level counting for accuracy
- `count_demo_items_deep()`: Deep demo counting
- Scope filtering: all, mezzanine_only, first_floor_only, etc.

### 5. routing_analyzer.py
Conduit and wire estimation:
- `estimate_conduit_with_ai()`: AI-based routing analysis
- `estimate_conduit_from_devices()`: Device-based fallback
- `calculate_wire_from_conduit()`: Wire quantity derivation
- `analyze_routing_complete()`: Combined analysis
- `manual_conduit_input()`: Manual override

### 6. business_rules.py
Material derivation rules:
- **Validated rules**: Power packs (0.74 ratio), Cat 6 cable (10 ft/jack), J-hooks (1 per 4 ft)
- **Fittings rules**: Connectors, couplings, bushings, straps per 100 ft conduit
- **Box rules**: 4" square, 4-11/16", deep boxes based on device types
- **Plaster rings**: 1G, 2G, 3/0 rings based on boxes
- **Cover plates**: Duplex, decora, switch, blank covers
- **Consumables**: Wirenuts, screws, tape, pull line
- **Wire**: From conduit lengths with multipliers

### 7. validator.py
Ground truth comparison:
- `validate_counts()`: Compare generated vs expected
- `print_validation_report()`: Formatted report
- `calculate_overall_accuracy()`: Accuracy metrics

### 8. output_generator.py
Multiple output formats:
- `generate_material_list_text()`: Human-readable text
- `generate_client_format()`: Matching client layout
- `export_to_csv()`: Spreadsheet format
- `export_to_json()`: Machine-readable
- `compare_to_client_format()`: Side-by-side comparison
- `generate_accuracy_report()`: Category-based accuracy

### 9. ground_truth.py
Validation data:
- 119 total items across 16 categories
- Counted items: 61 (from floor plans and schedules)
- Derived items: 58 (from business rules)
- Total quantity: 28,000+ units

### 10. main.py
Pipeline orchestration:
- `TakeOffSystem`: Main class with step-by-step control
- `run_full_pipeline()`: Complete automated pipeline
- `run_quick_test()`: Fast testing mode

## Pipeline Steps

1. **PDF Processing**: Extract pages, classify by sheet number
2. **Schedule Reading**: Parse E600 fixtures, E700 panels
3. **Symbol Counting**: AI vision on floor plans (E200, E201, T200, E100, T100)
4. **Routing Analysis**: Estimate conduit runs and wire lengths
5. **Business Rules**: Derive supporting materials
6. **Output Generation**: Multiple formats with validation

## Accuracy Targets

| Metric | Target |
|--------|--------|
| Item coverage | 95%+ (113/119 items) |
| Quantity accuracy | 85%+ on counted items |
| Derived accuracy | 90%+ using business rules |
| No hardcoding | All quantities from logic/prompts |

## Key Design Decisions

1. **Level-by-level counting**: Validated to achieve exact matches on multi-floor sheets
2. **Schedule preference**: Use schedule data over floor plan counts for fixtures
3. **Industry ratios**: Fittings derived using standard per-100-ft ratios
4. **Fallback methods**: Device-based estimation when AI routing fails
5. **Manual override**: Allow user input for conduit when needed

## File Dependencies

```
main.py
├── models.py (data structures)
├── pdf_processor.py (PDF handling)
├── schedule_reader.py (E600/E700 parsing)
├── symbol_counter.py (floor plan counting)
├── routing_analyzer.py (conduit/wire)
├── business_rules.py (material derivation)
├── validator.py (ground truth comparison)
├── output_generator.py (formatting)
└── ground_truth.py (validation data)
```

## Usage Examples

```python
# Full automated pipeline
from takeoff_system import run_full_pipeline
system = run_full_pipeline("drawings.pdf", "output/")

# Step-by-step control
from takeoff_system import TakeOffSystem
system = TakeOffSystem("output/")
system.process_pdf("drawings.pdf")
system.read_schedules()
system.count_all_sheets()
system.analyze_routing()
system.generate_output("text")
system.validate_results()

# Quick test with manual conduit
from takeoff_system import run_quick_test
system = run_quick_test("drawings.pdf", "output/")
```
