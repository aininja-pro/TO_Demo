"""Core takeoff pipeline routes — upload, stream, results."""
import asyncio
import json
import os
import time
import uuid
from dataclasses import asdict, replace
from typing import AsyncGenerator, Dict

from fastapi import APIRouter, HTTPException, UploadFile
from sse_starlette.sse import EventSourceResponse

from takeoff_system.business_rules import explain_derivations
from takeoff_system.config import create_config_from_pdf, IVCC_CETLA_CONFIG
from takeoff_system.main import TakeOffSystem
from takeoff_system.validator import validate_counts

router = APIRouter(prefix="/api/takeoff")

# Module-level state
_job_pdf_paths: Dict[str, str] = {}
_job_results: Dict[str, dict] = {}

# Known IVCC sheet numbers — require >= 7 matches to flag as IVCC project
_IVCC_SHEETS = {"E001", "E100", "E200", "E201", "E600", "E700", "T000", "T100", "T200"}


def _detect_ivcc_project(sheets) -> bool:
    """Check if this PDF matches the IVCC CETLA sheet set."""
    sheet_numbers = {s.sheet_number for s in sheets}
    matches = sheet_numbers & _IVCC_SHEETS
    return len(matches) >= 7


@router.post("")
async def upload_pdf(file: UploadFile):
    """Upload a PDF and return a job_id for pipeline execution."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    job_id = uuid.uuid4().hex
    job_dir = os.path.join("/tmp/takeoff_jobs", job_id)
    os.makedirs(job_dir, exist_ok=True)

    pdf_path = os.path.join(job_dir, file.filename)
    contents = await file.read()
    with open(pdf_path, "wb") as f:
        f.write(contents)

    _job_pdf_paths[job_id] = pdf_path
    return {"job_id": job_id, "filename": file.filename}


@router.get("/{job_id}/stream")
async def stream_pipeline(job_id: str):
    """SSE endpoint that runs the pipeline and streams step progress."""
    pdf_path = _job_pdf_paths.get(job_id)
    if not pdf_path:
        raise HTTPException(status_code=404, detail="Job not found")

    return EventSourceResponse(run_pipeline_with_events(pdf_path, job_id))


@router.get("/{job_id}/results")
async def get_results(job_id: str):
    """Return cached results for a completed job."""
    result = _job_results.get(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Results not found — pipeline may not have run yet")
    return result


async def run_pipeline_with_events(pdf_path: str, job_id: str) -> AsyncGenerator[dict, None]:
    """Async generator that runs each pipeline step in a thread and yields SSE events."""
    start_time = time.time()
    current_step = 0
    total_steps = 6

    def _sse(event: str, data: dict) -> dict:
        return {"event": event, "data": json.dumps(data)}

    try:
        # --- Init: create config + system ---
        config = await asyncio.to_thread(create_config_from_pdf, pdf_path)
        output_dir = os.path.join(os.path.dirname(pdf_path), "output")
        system = TakeOffSystem(output_dir=output_dir, config=config)

        # --- Step 1: PDF Processing ---
        current_step = 1
        yield _sse("step_start", {"step": 1, "name": "PDF Processing", "total_steps": total_steps})
        sheets = await asyncio.to_thread(system.process_pdf, pdf_path)
        is_ivcc = _detect_ivcc_project(sheets)

        # If IVCC project detected, reinitialize with calibrated config
        if is_ivcc:
            # Copy singleton — preserve fixture_definitions from auto-config
            detected_map = {s.sheet_number: s.page_number for s in sheets}
            config = replace(
                IVCC_CETLA_CONFIG,
                sheet_map=detected_map,
                fixture_definitions=config.fixture_definitions,
            )
            system = TakeOffSystem(output_dir=output_dir, config=config)
            system.sheets = sheets
            system.pdf_path = os.path.abspath(pdf_path)

        yield _sse("step_complete", {
            "step": 1,
            "result": {
                "sheets_found": len(sheets),
                "sheet_numbers": [s.sheet_number for s in sheets],
                "is_ivcc_project": is_ivcc,
            },
        })

        # --- Step 2: Read Schedules ---
        current_step = 2
        yield _sse("step_start", {"step": 2, "name": "Reading Schedules", "total_steps": total_steps})
        fixture_sched, panel_sched = await asyncio.to_thread(system.read_schedules)
        yield _sse("step_complete", {
            "step": 2,
            "result": {
                "linear_fixtures": fixture_sched.linear_fixtures,
                "pendant_fixtures": fixture_sched.pendant_fixtures,
                "breakers": panel_sched.breakers,
                "safety_switches": panel_sched.safety_switches,
            },
        })

        # --- Step 3: Count Symbols ---
        current_step = 3
        yield _sse("step_start", {"step": 3, "name": "Counting Symbols", "total_steps": total_steps})
        new_counts, demo_counts = await asyncio.to_thread(
            lambda: system.count_all_sheets(use_pdf_extraction=True)
        )
        all_counts = system.aggregate_counts()
        yield _sse("step_complete", {
            "step": 3,
            "result": {
                "new_items": {
                    "fixtures": new_counts.fixtures,
                    "controls": new_counts.controls,
                    "power": new_counts.power,
                    "fire_alarm": new_counts.fire_alarm,
                    "technology": new_counts.technology,
                },
                "demo_items": demo_counts.demo,
                "total_unique_items": len(all_counts),
            },
        })

        # --- Step 4: Routing Analysis ---
        current_step = 4
        yield _sse("step_start", {"step": 4, "name": "Routing Analysis", "total_steps": total_steps})
        routing = await asyncio.to_thread(system.analyze_routing)
        yield _sse("step_complete", {
            "step": 4,
            "result": {
                "conduit_by_size": routing.conduit.conduit_by_size,
                "wire_by_size": routing.conduit.wire_by_size,
                "method": routing.estimated_method,
            },
        })

        # --- Step 5: Derive Materials ---
        current_step = 5
        yield _sse("step_start", {"step": 5, "name": "Deriving Materials", "total_steps": total_steps})
        derived = await asyncio.to_thread(system.derive_materials)
        yield _sse("step_complete", {
            "step": 5,
            "result": {
                "derived_count": len(derived),
                "derived_materials": derived,
            },
        })

        # --- Step 6: Validation ---
        current_step = 6
        yield _sse("step_start", {"step": 6, "name": "Validation", "total_steps": total_steps})

        # Build combined counts for validation
        combined = system.aggregate_counts()
        combined.update(demo_counts.demo)
        combined.update(derived)
        if routing.conduit.conduit_by_size:
            for size, length in routing.conduit.conduit_by_size.items():
                combined[f"{size} EMT"] = length

        # Add reference additional items (hardware, labor, project tasks)
        if config.reference_additional_items:
            combined.update(config.reference_additional_items)
            derived.update(config.reference_additional_items)

        validation_results = await asyncio.to_thread(validate_counts, combined)
        validation_serialized = [asdict(v) for v in validation_results]

        # Generate derivation formulas
        all_counts = system.aggregate_counts()
        all_counts.update(demo_counts.demo)
        conduit = routing.conduit.conduit_by_size or {}
        mech = config.mechanical_equipment_count if config else 0
        formulas = explain_derivations(all_counts, conduit, mech)

        yield _sse("step_complete", {
            "step": 6,
            "result": {
                "is_ivcc_project": is_ivcc,
                "validation": validation_serialized,
            },
        })

        # --- Complete ---
        elapsed = round(time.time() - start_time, 2)
        final_result = {
            "materials": combined,
            "derived_materials": derived,
            "demo_items": demo_counts.demo,
            "conduit": routing.conduit.conduit_by_size,
            "wire": routing.conduit.wire_by_size,
            "routing_method": routing.estimated_method,
            "validation": validation_serialized,
            "formulas": formulas,
            "sheets": [{"number": s.sheet_number, "title": s.title, "type": s.sheet_type.value} for s in sheets],
            "is_ivcc_project": is_ivcc,
            "elapsed": elapsed,
        }

        _job_results[job_id] = final_result
        yield _sse("complete", final_result)

    except Exception as exc:
        yield _sse("error", {"message": str(exc), "step": current_step})
