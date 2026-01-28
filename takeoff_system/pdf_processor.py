"""PDF processing and sheet classification."""
import os
from pathlib import Path
from typing import List, Tuple
from PIL import Image

from .models import Sheet, SheetType


def classify_sheet_number(sheet_number: str) -> SheetType:
    """
    Classify a sheet based on its number.

    Rules:
    - xxx100 = Demolition (E100, T100)
    - xxx200-599 = New Work (E200, E201, T200, etc.)
    - xxx000 or xxx001 = Legends (E000, E001, T000)
    - xxx600-799 = Schedules (E600, E700)
    - xxx800+ = Reference/Details
    """
    if not sheet_number or len(sheet_number) < 2:
        return SheetType.REFERENCE

    # Extract the numeric part (strip letter prefix)
    try:
        num = int(sheet_number[1:])
    except ValueError:
        return SheetType.REFERENCE

    if num == 100:
        return SheetType.DEMO
    elif 200 <= num < 600:
        return SheetType.NEW
    elif num < 100:
        return SheetType.LEGEND
    elif 600 <= num < 800:
        return SheetType.SCHEDULE
    else:
        return SheetType.REFERENCE


def extract_pages_from_pdf(pdf_path: str, output_dir: str, dpi: int = 200) -> List[str]:
    """
    Convert PDF pages to PNG images.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted images
        dpi: Resolution for conversion (200-300 recommended)

    Returns:
        List of paths to extracted images
    """
    try:
        from pdf2image import convert_from_path
    except ImportError:
        raise ImportError(
            "pdf2image is required. Install with: pip install pdf2image\n"
            "Also requires poppler: brew install poppler (macOS) or apt install poppler-utils (Linux)"
        )

    os.makedirs(output_dir, exist_ok=True)

    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)

    image_paths = []
    for i, image in enumerate(images, 1):
        image_path = os.path.join(output_dir, f"page-{i:02d}.png")
        image.save(image_path, "PNG")
        image_paths.append(image_path)
        print(f"Extracted page {i} -> {image_path}")

    return image_paths


# Known sheet structure for IVCC CETLA project
IVCC_SHEET_MAP = {
    1: ("E000", "ELECTRICAL OVERSHEET", SheetType.LEGEND),
    2: ("E100", "FLOOR PLANS - ELECTRICAL DEMOLITION", SheetType.DEMO),
    3: ("E200", "FLOOR PLANS - LIGHTING", SheetType.NEW),
    4: ("E201", "FLOOR PLANS - POWER/SYSTEMS", SheetType.NEW),
    5: ("E600", "ELECTRICAL SCHEDULES", SheetType.SCHEDULE),
    6: ("E700", "PANEL SCHEDULES", SheetType.SCHEDULE),
    7: ("T000", "TECHNOLOGY OVERSHEET", SheetType.LEGEND),
    8: ("T100", "FLOOR PLANS - TECHNOLOGY DEMOLITION", SheetType.DEMO),
    9: ("T200", "FLOOR PLANS - TECHNOLOGY", SheetType.NEW),
    10: ("T300", "TECHNOLOGY DETAILS & RISER DIAGRAMS", SheetType.REFERENCE),
    11: ("T400", "TECHNOLOGY SCHEDULES", SheetType.SCHEDULE),
}


def classify_pages(image_paths: List[str]) -> List[Sheet]:
    """
    Classify all pages from the drawing set.

    For now, uses the known IVCC sheet map.
    Future: Use AI to read title blocks.
    """
    sheets = []

    for i, image_path in enumerate(image_paths, 1):
        if i in IVCC_SHEET_MAP:
            sheet_num, title, sheet_type = IVCC_SHEET_MAP[i]
        else:
            sheet_num = f"UNKNOWN-{i}"
            title = "Unknown Sheet"
            sheet_type = SheetType.REFERENCE

        sheet = Sheet(
            page_number=i,
            sheet_number=sheet_num,
            sheet_type=sheet_type,
            title=title,
            image_path=image_path
        )
        sheets.append(sheet)

    return sheets


def get_sheets_by_type(sheets: List[Sheet], sheet_type: SheetType) -> List[Sheet]:
    """Filter sheets by type."""
    return [s for s in sheets if s.sheet_type == sheet_type]
