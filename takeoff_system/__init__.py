# MEP TakeOff System
# AI-powered material list generation from electrical construction drawings

"""
MEP TakeOff System - Production-Ready AI Material List Generator

This system extracts electrical material lists from construction PDF drawings
using direct PDF extraction (pdfplumber + PyMuPDF), AI vision analysis,
schedule reading, and business rules.

Architecture:
- pdf_extractor: Direct PDF text/table/vector extraction (pdfplumber + PyMuPDF)
- pdf_processor: PDF page extraction and classification
- schedule_reader: E600/E700 schedule table parsing
- symbol_counter: AI vision-based device counting (fallback)
- routing_analyzer: Conduit and wire estimation
- business_rules: Material derivation from counts
- validator: Ground truth comparison
- output_generator: Multiple output formats

Extraction Methods:
- PDF text extraction (pdfplumber): 8/9 exact matches on fixture counts
- AI vision (Claude): ~20% accuracy on fixture counts (fallback)

Usage:
    from takeoff_system import TakeOffSystem, run_full_pipeline

    # Full pipeline with PDF extraction (recommended)
    system = run_full_pipeline("drawings.pdf", "output/", use_pdf_extraction=True)

    # Manual control
    system = TakeOffSystem("output/")
    system.process_pdf("drawings.pdf")
    system.read_schedules()
    system.count_all_sheets(use_pdf_extraction=True)
    system.analyze_routing()
    system.generate_output("text")
"""

from .models import (
    SheetType,
    Sheet,
    DeviceCounts,
    FixtureScheduleData,
    PanelScheduleData,
    ConduitCounts,
    RoutingData,
    FullTakeoffResult,
    ValidationResult,
)

from .main import (
    TakeOffSystem,
    run_full_pipeline,
    run_quick_test,
)

from .pdf_processor import (
    extract_pages_from_pdf,
    classify_pages,
    get_sheets_by_type,
)

from .schedule_reader import (
    read_fixture_schedule,
    read_panel_schedule,
    read_all_schedules,
)

from .symbol_counter import (
    count_symbols_with_claude,
    count_by_level,
    count_demo_items_deep,
)

from .routing_analyzer import (
    estimate_conduit_with_ai,
    estimate_conduit_from_devices,
    calculate_wire_from_conduit,
    analyze_routing_complete,
    manual_conduit_input,
    estimate_conduit_from_pdf_vectors,
)

from .pdf_extractor import (
    extract_fixture_counts,
    extract_fixture_counts_all_floors,
    extract_schedule_tables,
    extract_luminaire_schedule,
    extract_panel_schedule,
    extract_conduit_lengths,
    extract_floor_plan_data,
    get_pdf_page_count,
)

from .business_rules import (
    derive_all_materials,
    derive_materials_with_schedules,
    derive_power_packs,
    derive_cable_and_jhooks,
    derive_fittings_from_conduit,
    derive_boxes,
    derive_plaster_rings,
    derive_plates,
    derive_consumables,
    derive_wire_from_conduit,
)

from .validator import (
    validate_counts,
    print_validation_report,
    calculate_overall_accuracy,
)

from .output_generator import (
    generate_material_list_text,
    generate_client_format,
    export_to_csv,
    export_to_json,
    compare_to_client_format,
    generate_accuracy_report,
)

from .ground_truth import (
    ALL_GROUND_TRUTH,
    GROUND_TRUTH_COUNTED,
    GROUND_TRUTH_DERIVED,
    get_category,
    get_item_count,
    get_total_quantity,
)

__version__ = "1.0.0"
__all__ = [
    # Main classes
    "TakeOffSystem",
    "run_full_pipeline",
    "run_quick_test",
    # Models
    "SheetType",
    "Sheet",
    "DeviceCounts",
    "FixtureScheduleData",
    "PanelScheduleData",
    "ConduitCounts",
    "RoutingData",
    "FullTakeoffResult",
    "ValidationResult",
    # PDF processing
    "extract_pages_from_pdf",
    "classify_pages",
    "get_sheets_by_type",
    # Schedule reading
    "read_fixture_schedule",
    "read_panel_schedule",
    "read_all_schedules",
    # Symbol counting
    "count_symbols_with_claude",
    "count_by_level",
    "count_demo_items_deep",
    # Routing
    "estimate_conduit_with_ai",
    "estimate_conduit_from_devices",
    "calculate_wire_from_conduit",
    "analyze_routing_complete",
    "manual_conduit_input",
    "estimate_conduit_from_pdf_vectors",
    # PDF extraction
    "extract_fixture_counts",
    "extract_fixture_counts_all_floors",
    "extract_schedule_tables",
    "extract_luminaire_schedule",
    "extract_panel_schedule",
    "extract_conduit_lengths",
    "extract_floor_plan_data",
    "get_pdf_page_count",
    # Business rules
    "derive_all_materials",
    "derive_materials_with_schedules",
    "derive_power_packs",
    "derive_cable_and_jhooks",
    "derive_fittings_from_conduit",
    "derive_boxes",
    "derive_plaster_rings",
    "derive_plates",
    "derive_consumables",
    "derive_wire_from_conduit",
    # Validation
    "validate_counts",
    "print_validation_report",
    "calculate_overall_accuracy",
    # Output
    "generate_material_list_text",
    "generate_client_format",
    "export_to_csv",
    "export_to_json",
    "compare_to_client_format",
    "generate_accuracy_report",
    # Ground truth
    "ALL_GROUND_TRUTH",
    "GROUND_TRUTH_COUNTED",
    "GROUND_TRUTH_DERIVED",
    "get_category",
    "get_item_count",
    "get_total_quantity",
]
