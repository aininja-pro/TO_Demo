"""Main orchestration for the MEP TakeOff System.

This module provides the complete pipeline for generating material lists
from electrical construction drawings:
1. PDF extraction and page classification
2. Schedule reading (E600 fixtures, E700 panels)
3. Symbol counting on floor plans
4. Routing analysis for conduit/wire
5. Business rules for derived materials
6. Output generation and validation
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import (
    Sheet, SheetType, DeviceCounts,
    FixtureScheduleData, PanelScheduleData,
    RoutingData, FullTakeoffResult
)
from .pdf_processor import extract_pages_from_pdf, classify_pages, get_sheets_by_type
from .symbol_counter import count_symbols_with_claude, count_demo_items_deep, count_by_floor_crop
from .schedule_reader import read_fixture_schedule, read_panel_schedule
from .pdf_extractor import (
    extract_fixture_counts, extract_floor_plan_data,
    extract_conduit_lengths, extract_schedule_tables,
    extract_all_from_pdf, extract_all_to_device_counts,
    extract_controls, extract_power_devices, extract_demo_items,
    extract_technology, extract_panel_breakers
)
from .routing_analyzer import analyze_routing_complete, manual_conduit_input
from .business_rules import derive_all_materials, derive_materials_with_schedules
from .validator import validate_counts, print_validation_report
from .output_generator import (
    generate_material_list_text, export_to_csv, export_to_json,
    compare_to_client_format, generate_accuracy_report
)


class TakeOffSystem:
    """Main class for running the MEP takeoff pipeline."""

    def __init__(self, output_dir: str = None):
        """Initialize the takeoff system."""
        self.output_dir = output_dir or "./takeoff_output"
        self.sheets: List[Sheet] = []
        self.device_counts = DeviceCounts()
        self.demo_counts = DeviceCounts()
        self.fixture_schedule = FixtureScheduleData()
        self.panel_schedule = PanelScheduleData()
        self.routing = RoutingData()
        self.pdf_path: Optional[str] = None  # Store original PDF path

        os.makedirs(self.output_dir, exist_ok=True)

    def process_pdf(self, pdf_path: str, dpi: int = 200) -> List[Sheet]:
        """
        Extract and classify pages from a PDF.

        Args:
            pdf_path: Path to the electrical drawings PDF
            dpi: Resolution for image extraction

        Returns:
            List of classified Sheet objects
        """
        print(f"\n[1/6] Processing PDF: {pdf_path}")

        # Store PDF path for later use in PDF extraction
        self.pdf_path = os.path.abspath(pdf_path)

        images_dir = os.path.join(self.output_dir, "pages")
        image_paths = extract_pages_from_pdf(pdf_path, images_dir, dpi=dpi)

        self.sheets = classify_pages(image_paths)

        print(f"\nSheet Classification:")
        for sheet in self.sheets:
            print(f"  Page {sheet.page_number}: {sheet.sheet_number} - {sheet.sheet_type.value} - {sheet.title}")

        return self.sheets

    def read_schedules(self, api_key: Optional[str] = None) -> Tuple[FixtureScheduleData, PanelScheduleData]:
        """
        Read fixture and panel schedules from E600 and E700 sheets.

        Args:
            api_key: Anthropic API key

        Returns:
            Tuple of (FixtureScheduleData, PanelScheduleData)
        """
        print(f"\n[2/6] Reading Schedules...")

        # Find schedule sheets
        e600_sheet = next((s for s in self.sheets if s.sheet_number == "E600"), None)
        e700_sheet = next((s for s in self.sheets if s.sheet_number == "E700"), None)

        if e600_sheet:
            print(f"  Reading E600 (Fixture Schedule)...")
            try:
                self.fixture_schedule = read_fixture_schedule(e600_sheet.image_path, api_key)
                linear_count = sum(self.fixture_schedule.linear_fixtures.values())
                pendant_count = sum(self.fixture_schedule.pendant_fixtures.values())
                print(f"    Found {linear_count} linear LEDs, {pendant_count} pendants")
            except Exception as e:
                print(f"    Warning: Failed to read E600: {e}")
        else:
            print("  E600 sheet not found, skipping fixture schedule")

        if e700_sheet:
            print(f"  Reading E700 (Panel Schedule)...")
            try:
                self.panel_schedule = read_panel_schedule(e700_sheet.image_path, api_key)
                breaker_count = sum(self.panel_schedule.breakers.values())
                switch_count = sum(self.panel_schedule.safety_switches.values())
                print(f"    Found {breaker_count} breakers, {switch_count} safety switches")
            except Exception as e:
                print(f"    Warning: Failed to read E700: {e}")
        else:
            print("  E700 sheet not found, skipping panel schedule")

        return self.fixture_schedule, self.panel_schedule

    def count_all_sheets(
        self,
        api_key: Optional[str] = None,
        scope: str = "all",
        use_pdf_extraction: bool = True
    ) -> Tuple[DeviceCounts, DeviceCounts]:
        """
        Count symbols on all relevant sheets.

        Args:
            api_key: Anthropic API key (or uses ANTHROPIC_API_KEY env var)
            scope: Scope filter - "all" counts everything, or specific floor if needed
            use_pdf_extraction: If True, use PDF text extraction (faster, more accurate).
                              If False, use AI vision (legacy method).

        Returns:
            Tuple of (new_counts, demo_counts) as DeviceCounts objects
        """
        if not self.sheets:
            raise ValueError("No sheets loaded. Call process_pdf first.")

        print(f"\n[3/6] Counting Symbols on Floor Plans...")

        new_counts = DeviceCounts()
        demo_counts = DeviceCounts()

        # Use complete PDF extraction if enabled and PDF path is available
        if use_pdf_extraction and self.pdf_path:
            print("  Using PDF text extraction for all sheets...")
            try:
                results = extract_all_from_pdf(self.pdf_path)

                # Populate new_counts from extraction results
                new_counts.fixtures = results.get('fixtures', {})
                new_counts.controls = results.get('controls', {})
                new_counts.power = results.get('power', {})
                new_counts.technology = results.get('technology', {})

                # Populate demo_counts
                demo_counts.demo = results.get('demo', {})

                # Add panel data to power
                panel = results.get('panel', {})
                for item, count in panel.items():
                    new_counts.power[item] = count

                self.device_counts = new_counts
                self.demo_counts = demo_counts

                return new_counts, demo_counts

            except Exception as e:
                print(f"    Warning: PDF extraction failed: {e}")
                print("    Falling back to vision-based extraction...")

        # Fallback to vision-based extraction
        new_sheets = get_sheets_by_type(self.sheets, SheetType.NEW)
        print(f"  Processing {len(new_sheets)} NEW sheets with vision...")

        for sheet in new_sheets:
            print(f"    {sheet.sheet_number}: {sheet.title}...")
            try:
                if sheet.sheet_number == "E200":
                    counts = count_by_floor_crop(
                        sheet.image_path,
                        sheet.sheet_type,
                        sheet.sheet_number,
                        api_key
                    )
                else:
                    counts = count_symbols_with_claude(
                        sheet.image_path,
                        sheet.sheet_type,
                        sheet.sheet_number,
                        api_key,
                        scope=scope,
                        level_by_level=False
                    )
                new_counts.merge(counts)
                print(f"      Completed")
            except Exception as e:
                print(f"      Error: {e}")

        # Process DEMO sheets
        demo_sheets = get_sheets_by_type(self.sheets, SheetType.DEMO)
        print(f"  Processing {len(demo_sheets)} DEMO sheets...")

        for sheet in demo_sheets:
            print(f"    {sheet.sheet_number}: {sheet.title}...")
            try:
                counts = count_symbols_with_claude(
                    sheet.image_path,
                    sheet.sheet_type,
                    sheet.sheet_number,
                    api_key,
                    scope=scope,
                    level_by_level=False
                )
                demo_counts.merge(counts)
                total = sum(counts.demo.values())
                print(f"      Found {total} demo items")
            except Exception as e:
                print(f"      Error: {e}")

        self.device_counts = new_counts
        self.demo_counts = demo_counts

        return new_counts, demo_counts

    def _count_with_pdf_extraction(self, sheet: Sheet) -> DeviceCounts:
        """
        Count fixtures using PDF text extraction.

        This method extracts fixture tags directly from the PDF text,
        which is more accurate than vision-based counting.

        Args:
            sheet: Sheet object with page information

        Returns:
            DeviceCounts with extracted fixture counts
        """
        # Find the original PDF path from the image path
        # Image paths are like: ./takeoff_output/pages/page_3.png
        # We need to find the original PDF
        pdf_path = self._find_pdf_path()

        if not pdf_path:
            raise ValueError("Could not find original PDF path")

        # Extract fixture counts from the PDF page
        # Note: page_number in Sheet is 1-indexed, PDF extraction is 0-indexed
        page_num = sheet.page_number - 1
        fixture_counts = extract_fixture_counts(pdf_path, page_num)

        print(f"      PDF extraction: {fixture_counts}")

        # Convert to DeviceCounts
        counts = DeviceCounts()
        counts.fixtures = fixture_counts

        return counts

    def _find_pdf_path(self) -> Optional[str]:
        """Find the original PDF path from stored path or by searching."""
        # Use stored path if available
        if self.pdf_path:
            return self.pdf_path

        # Fallback: Look for PDF files in the current directory
        import glob

        patterns = [
            "*.pdf",
            "../*.pdf",
            "../../*.pdf",
        ]

        for pattern in patterns:
            pdfs = glob.glob(pattern)
            if pdfs:
                # Return the first electrical plans PDF found
                for pdf in pdfs:
                    if "Electrical" in pdf or "IVCC" in pdf:
                        return pdf
                return pdfs[0]

        return None

    def analyze_routing(
        self,
        api_key: Optional[str] = None,
        use_ai: bool = True,
        building_sqft: int = 10000,
        use_pdf_vectors: bool = False
    ) -> RoutingData:
        """
        Analyze conduit routing and calculate wire lengths.

        Args:
            api_key: Anthropic API key
            use_ai: Whether to use AI vision for routing analysis
            building_sqft: Building size for device-based estimation
            use_pdf_vectors: Whether to use PDF vector extraction for conduit lengths

        Returns:
            RoutingData with conduit and wire estimates
        """
        print(f"\n[4/6] Analyzing Conduit Routing...")

        # Find floor plan sheets
        e200_sheet = next((s for s in self.sheets if s.sheet_number == "E200"), None)
        e201_sheet = next((s for s in self.sheets if s.sheet_number == "E201"), None)

        if e200_sheet and e201_sheet:
            try:
                self.routing = analyze_routing_complete(
                    e200_sheet.image_path,
                    e201_sheet.image_path,
                    self.aggregate_counts(),
                    building_sqft,
                    api_key,
                    use_ai,
                    pdf_path=self.pdf_path,
                    use_pdf_vectors=use_pdf_vectors
                )
                total_conduit = sum(self.routing.conduit.conduit_by_size.values())
                print(f"    Estimated {total_conduit:,} ft total conduit ({self.routing.estimated_method})")
            except Exception as e:
                print(f"    Warning: Routing analysis failed: {e}")
                print("    Using device-based estimation...")
                from .routing_analyzer import estimate_conduit_from_devices
                conduit = estimate_conduit_from_devices(self.aggregate_counts(), building_sqft)
                self.routing.conduit = conduit
                self.routing.estimated_method = "device_based"
        else:
            print("  Floor plan sheets not found, skipping routing analysis")

        return self.routing

    def aggregate_counts(self) -> Dict[str, int]:
        """
        Aggregate all device counts into a single dictionary.

        Returns:
            Dictionary with all item counts
        """
        all_counts = {}

        # Merge device counts
        for attr in ['fixtures', 'controls', 'power', 'fire_alarm', 'technology']:
            counts_dict = getattr(self.device_counts, attr)
            all_counts.update(counts_dict)

        # Merge schedule data
        all_counts.update(self.fixture_schedule.linear_fixtures)
        all_counts.update(self.fixture_schedule.pendant_fixtures)
        all_counts.update(self.fixture_schedule.standard_fixtures)
        all_counts.update(self.panel_schedule.breakers)
        all_counts.update(self.panel_schedule.safety_switches)

        return all_counts

    def derive_materials(self) -> Dict[str, int]:
        """
        Apply business rules to derive supporting materials.

        Returns:
            Dictionary of derived material quantities
        """
        print(f"\n[5/6] Deriving Supporting Materials...")

        all_counts = self.aggregate_counts()

        # Get conduit lengths if available
        conduit_lengths = None
        if self.routing.conduit.conduit_by_size:
            conduit_lengths = self.routing.conduit.conduit_by_size

        derived = derive_all_materials(
            all_counts,
            conduit_lengths,
            include_fittings=conduit_lengths is not None,
            include_consumables=True,
            include_wire=conduit_lengths is not None
        )

        print(f"    Derived {len(derived)} supporting materials")
        return derived

    def validate_results(self) -> None:
        """Validate generated counts against ground truth and print report."""
        all_counts = self.aggregate_counts()
        demo_counts = self.demo_counts.demo
        derived = self.derive_materials()

        # Merge all for validation
        all_counts.update(demo_counts)
        all_counts.update(derived)

        # Also add conduit lengths if available
        if self.routing.conduit.conduit_by_size:
            for size, length in self.routing.conduit.conduit_by_size.items():
                all_counts[f'{size} EMT'] = length

        results = validate_counts(all_counts)
        print_validation_report(results)

    def generate_output(self, format: str = "text") -> str:
        """
        Generate material list output.

        Args:
            format: Output format ("text", "csv", "json", "comparison", "accuracy")

        Returns:
            Path to output file or text content
        """
        print(f"\n[6/6] Generating Output ({format})...")

        new_materials = self.aggregate_counts()
        demo_materials = self.demo_counts.demo
        derived_materials = self.derive_materials()

        if format == "text":
            output = generate_material_list_text(new_materials, demo_materials, derived_materials)
            output_path = os.path.join(self.output_dir, "material_list.txt")
            with open(output_path, 'w') as f:
                f.write(output)
            print(output)
            return output_path

        elif format == "csv":
            output_path = os.path.join(self.output_dir, "material_list.csv")
            export_to_csv(new_materials, demo_materials, derived_materials, output_path)
            print(f"    Exported to {output_path}")
            return output_path

        elif format == "json":
            output_path = os.path.join(self.output_dir, "material_list.json")
            export_to_json(
                new_materials, demo_materials, derived_materials, output_path,
                metadata={
                    "routing_method": self.routing.estimated_method,
                    "sheets_processed": len(self.sheets),
                }
            )
            print(f"    Exported to {output_path}")
            return output_path

        elif format == "comparison":
            output_path = os.path.join(self.output_dir, "comparison_report.txt")
            all_materials = {**new_materials, **demo_materials, **derived_materials}
            output = compare_to_client_format(all_materials, output_path)
            print(output)
            return output_path

        elif format == "accuracy":
            all_materials = {**new_materials, **demo_materials, **derived_materials}
            output = generate_accuracy_report(all_materials)
            output_path = os.path.join(self.output_dir, "accuracy_report.txt")
            with open(output_path, 'w') as f:
                f.write(output)
            print(output)
            return output_path

        else:
            raise ValueError(f"Unknown format: {format}")

    def get_full_result(self) -> FullTakeoffResult:
        """Get the complete takeoff result as a structured object."""
        derived = self.derive_materials()
        all_counts = self.aggregate_counts()
        all_counts.update(self.demo_counts.demo)

        results = validate_counts(all_counts)

        return FullTakeoffResult(
            new_counts=self.device_counts,
            demo_counts=self.demo_counts,
            fixture_schedule=self.fixture_schedule,
            panel_schedule=self.panel_schedule,
            routing=self.routing,
            derived_materials=derived,
            validation_results=results,
        )


def run_full_pipeline(
    pdf_path: str,
    output_dir: str = None,
    api_key: str = None,
    dpi: int = 300,  # Higher DPI for better tag readability
    use_ai_routing: bool = True,
    building_sqft: int = 10000,
    use_pdf_extraction: bool = True
) -> TakeOffSystem:
    """
    Run the complete takeoff pipeline.

    Args:
        pdf_path: Path to electrical drawings PDF
        output_dir: Directory for output files
        api_key: Anthropic API key
        dpi: Resolution for PDF extraction
        use_ai_routing: Whether to use AI for conduit routing
        building_sqft: Building size for estimation
        use_pdf_extraction: Whether to use PDF text extraction (faster, more accurate)
                          instead of vision-based counting

    Returns:
        TakeOffSystem instance with all results
    """
    print("=" * 70)
    print("MEP TAKEOFF SYSTEM - FULL PIPELINE")
    print("=" * 70)

    if use_pdf_extraction:
        print("Using PDF text extraction (pdfplumber) for improved accuracy")
    else:
        print("Using AI vision-based extraction")

    system = TakeOffSystem(output_dir)

    # Step 1: Process PDF
    system.process_pdf(pdf_path, dpi=dpi)

    # Step 2: Read schedules
    system.read_schedules(api_key)

    # Step 3: Count symbols
    system.count_all_sheets(api_key, use_pdf_extraction=use_pdf_extraction)

    # Step 4: Analyze routing
    system.analyze_routing(api_key, use_ai_routing, building_sqft)

    # Step 5: Generate outputs
    system.generate_output("text")
    system.generate_output("json")
    system.generate_output("csv")

    # Step 6: Validate and report
    system.validate_results()
    system.generate_output("accuracy")

    print(f"\nPipeline complete! Output saved to: {system.output_dir}")

    return system


def run_quick_test(
    pdf_path: str,
    output_dir: str = None,
    api_key: str = None
) -> TakeOffSystem:
    """
    Run a quick test with minimal processing (no routing analysis).

    Args:
        pdf_path: Path to electrical drawings PDF
        output_dir: Directory for output files
        api_key: Anthropic API key

    Returns:
        TakeOffSystem instance
    """
    print("=" * 70)
    print("MEP TAKEOFF SYSTEM - QUICK TEST")
    print("=" * 70)

    system = TakeOffSystem(output_dir)

    system.process_pdf(pdf_path, dpi=150)  # Lower DPI for speed
    system.read_schedules(api_key)
    system.count_all_sheets(api_key)

    # Skip routing, use manual input
    system.routing.conduit = manual_conduit_input(
        conduit_34=3773,  # From client list
        conduit_1=790
    )
    system.routing.estimated_method = "manual"

    system.generate_output("text")
    system.validate_results()

    return system


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m takeoff_system.main <pdf_path> [output_dir]")
        print("       python -m takeoff_system.main --quick <pdf_path> [output_dir]")
        sys.exit(1)

    if sys.argv[1] == "--quick":
        pdf_path = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "./takeoff_output"
        run_quick_test(pdf_path, output_dir)
    else:
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./takeoff_output"
        run_full_pipeline(pdf_path, output_dir)
