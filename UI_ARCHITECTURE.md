# MEP Takeoff Pro — UI Architecture & Claude Code Handoff

## Document Purpose

Complete architectural blueprint for Claude Code to execute. Every decision is pre-made. Follow this sequentially, checking in with the user after each Phase (Section 5).

**RULE: Read this entire document before writing any code.**

---

## 1. WHAT WE'RE BUILDING

A takeoff app. Upload an electrical PDF → pipeline runs → see the material list.

That's it. Don't overthink it.

**One extra feature:** When the uploaded PDF is the IVCC CETLA project (the one we validated), a bonus "Accuracy" tab appears showing the 97% match vs. the senior estimator's manual takeoff. This only shows when we have ground truth to compare against.

### How the Demo Works

1. Open the app
2. Upload the IVCC CETLA electrical drawings PDF
3. Watch the 6-step pipeline process it
4. See the full material list organized by category
5. Click the "Accuracy" tab → show the 97% match side-by-side
6. Tell the GC: "We did this on your drawings. We can calibrate to your rules."

### Target Audience

General Contractors who subcontract MEP work.

---

## 2. TECH STACK

### Frontend
- **Vite + React 18** (no Next.js)
- **Tailwind CSS**
- **shadcn/ui** components: Card, Table, Tabs, Progress, Badge, Button
- **Recharts** for accuracy bar charts
- **Lucide React** for icons
- TypeScript

### Backend
- **FastAPI** (Python) — thin wrapper around existing `takeoff_system/`
- **Uvicorn** ASGI server
- **SSE** (Server-Sent Events) for streaming pipeline progress to frontend
- No database

### Project Structure
```
TO_Demo/
├── takeoff_system/          # EXISTING — DO NOT MODIFY
│   ├── __init__.py
│   ├── main.py              # TakeOffSystem class, run_full_pipeline()
│   ├── models.py            # DeviceCounts, FullTakeoffResult, etc.
│   ├── config.py            # ProjectConfig
│   ├── pdf_extractor.py     # extract_all_from_pdf() — the core engine
│   ├── business_rules.py    # derive_all_materials()
│   ├── ground_truth.py      # IVCC CETLA validated counts
│   ├── validator.py         # validate_counts()
│   ├── output_generator.py  # ITEM_NUMBERS mapping, CSV/JSON export
│   ├── pdf_processor.py     # Sheet classification
│   ├── schedule_reader.py   # E600/E700 parsing
│   ├── routing_analyzer.py  # Conduit estimation
│   └── symbol_counter.py    # AI vision fallback
│
├── api/                     # NEW — FastAPI backend
│   ├── __init__.py
│   ├── server.py            # FastAPI app, CORS, mount routes
│   └── routes/
│       ├── __init__.py
│       └── takeoff.py       # POST /api/takeoff + GET /api/takeoff/{id}/stream
│
├── frontend/                # NEW — Vite React app
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx           # State machine: idle → processing → results
│       ├── components/
│       │   ├── ui/           # shadcn components (installed via CLI)
│       │   ├── Header.tsx
│       │   ├── UploadZone.tsx
│       │   ├── PipelineProgress.tsx
│       │   ├── StepCard.tsx
│       │   ├── ResultsDashboard.tsx
│       │   ├── MaterialTable.tsx
│       │   ├── StatsBar.tsx
│       │   ├── AccuracyComparison.tsx
│       │   └── AccuracyChart.tsx
│       ├── hooks/
│       │   └── useTakeoff.ts  # Single hook manages entire workflow
│       └── lib/
│           ├── api.ts         # fetch helpers
│           └── types.ts       # TypeScript types
│
├── requirements.txt          # UPDATE — add fastapi, uvicorn, etc.
└── UI_ARCHITECTURE.md        # THIS FILE
```

**Note the simplicity:** One API route file. One custom hook. No router, no state library.

---

## 3. BACKEND ARCHITECTURE

### 3.1 Core Principle

The API is a **thin wrapper** around the existing `TakeOffSystem` class. It accepts a PDF upload, runs the real pipeline, and streams progress events via SSE. Zero new business logic.

### 3.2 API Endpoints

There are only 3 endpoints:

#### `POST /api/takeoff`

Accepts a PDF upload. Saves it. Returns a job ID.

```python
@router.post("/api/takeoff")
async def upload_pdf(file: UploadFile = File(...)):
    job_id = str(uuid4())
    job_dir = f"/tmp/takeoff_jobs/{job_id}"
    os.makedirs(job_dir, exist_ok=True)
    
    save_path = os.path.join(job_dir, file.filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {"job_id": job_id, "filename": file.filename}
```

#### `GET /api/takeoff/{job_id}/stream`

SSE endpoint. Client connects, the REAL pipeline runs on the uploaded PDF, events stream back.

**Events emitted (in order):**

```
event: step_start
data: {"step": 1, "name": "PDF Processing", "total_steps": 6}

event: step_complete  
data: {"step": 1, "result": {"sheets_found": 11, "sheets": [...]}}

event: step_start
data: {"step": 2, "name": "Reading Schedules", "total_steps": 6}

event: step_complete
data: {"step": 2, "result": {"fixtures_found": 52, "breakers_found": 15}}

... (steps 3-6) ...

event: complete
data: {"job_id": "...", "results": { <full results JSON> }}

event: error  (if something fails)
data: {"message": "...", "step": 3}
```

**Implementation — this runs the REAL pipeline:**

```python
from takeoff_system.main import TakeOffSystem
from takeoff_system.config import create_config_from_pdf
from takeoff_system.business_rules import derive_all_materials
from takeoff_system.validator import validate_counts
from takeoff_system.ground_truth import ALL_GROUND_TRUTH

async def run_pipeline_with_events(pdf_path: str, job_id: str):
    """Generator that runs the real pipeline and yields SSE events."""
    
    config = create_config_from_pdf(pdf_path)
    system = TakeOffSystem(output_dir=f"/tmp/takeoff_jobs/{job_id}/output", config=config)
    
    # Step 1: Process PDF
    yield sse_event("step_start", {"step": 1, "name": "PDF Processing", "total_steps": 6})
    sheets = system.process_pdf(pdf_path)
    yield sse_event("step_complete", {"step": 1, "result": {
        "sheets_found": len(sheets),
        "sheets": [{"page": s.page_number, "number": s.sheet_number, 
                     "type": s.sheet_type.value, "title": s.title} for s in sheets]
    }})
    
    # Step 2: Read Schedules
    yield sse_event("step_start", {"step": 2, "name": "Reading Schedules", "total_steps": 6})
    fixture_sched, panel_sched = system.read_schedules()
    yield sse_event("step_complete", {"step": 2, "result": {
        "linear_fixtures": sum(fixture_sched.linear_fixtures.values()),
        "pendant_fixtures": sum(fixture_sched.pendant_fixtures.values()),
        "breakers": sum(panel_sched.breakers.values()),
    }})
    
    # Step 3: Count Symbols (the big one — runs real extraction)
    yield sse_event("step_start", {"step": 3, "name": "Counting Symbols", "total_steps": 6})
    new_counts, demo_counts = system.count_all_sheets(use_pdf_extraction=True)
    all_counted = {**new_counts.fixtures, **new_counts.controls, 
                   **new_counts.power, **new_counts.technology}
    yield sse_event("step_complete", {"step": 3, "result": {
        "items_counted": len(all_counted),
        "total_devices": sum(all_counted.values()),
    }})
    
    # Step 4: Routing Analysis
    yield sse_event("step_start", {"step": 4, "name": "Routing Analysis", "total_steps": 6})
    system.analyze_routing(use_ai=False)
    yield sse_event("step_complete", {"step": 4, "result": {
        "conduit_total_ft": sum(system.routing.conduit.conduit_by_size.values()),
        "method": system.routing.estimated_method
    }})
    
    # Step 5: Business Rules
    yield sse_event("step_start", {"step": 5, "name": "Applying Business Rules", "total_steps": 6})
    derived = system.derive_materials()
    yield sse_event("step_complete", {"step": 5, "result": {
        "derived_items": len(derived),
        "total_derived_qty": sum(derived.values()),
    }})
    
    # Step 6: Output
    yield sse_event("step_start", {"step": 6, "name": "Generating Output", "total_steps": 6})
    
    # Detect if this is the IVCC project → enable accuracy comparison
    has_ground_truth = _detect_ivcc_project(sheets)
    
    validation = None
    if has_ground_truth:
        all_materials = system.aggregate_counts()
        all_materials.update(demo_counts.demo)
        validation_results = validate_counts(all_materials)
        exact = sum(1 for v in validation_results if v.status == "exact")
        close = sum(1 for v in validation_results if v.status == "close")
        total = len(validation_results)
        validation = {
            "available": True,
            "exact_matches": exact,
            "close_matches": close,
            "total_items": total,
            "accuracy_pct": round((exact + close) / total * 100, 1),
            "details": [
                {"item": v.item, "expected": v.expected, "actual": v.actual,
                 "difference": v.difference, "status": v.status}
                for v in validation_results
            ]
        }
    
    yield sse_event("step_complete", {"step": 6, "result": {"validation_available": has_ground_truth}})
    
    # Final complete event with ALL data
    yield sse_event("complete", {
        "job_id": job_id,
        "new_materials": {**new_counts.fixtures, **new_counts.controls,
                          **new_counts.power, **new_counts.technology},
        "demo_materials": demo_counts.demo,
        "derived_materials": derived,
        "panel_materials": {**system.panel_schedule.breakers, 
                            **system.panel_schedule.safety_switches},
        "validation": validation,
        "summary": {
            "total_line_items": len(all_counted) + len(demo_counts.demo) + len(derived),
            "processing_time_sec": elapsed,  # Track actual elapsed time
        }
    })


def _detect_ivcc_project(sheets) -> bool:
    """Check if this looks like the IVCC CETLA project."""
    sheet_numbers = {s.sheet_number for s in sheets}
    ivcc_markers = {"E001", "E100", "E200", "E201", "E600", "E700", "T000", "T100", "T200"}
    return len(sheet_numbers & ivcc_markers) >= 7
```

#### `GET /api/takeoff/{job_id}/results`

Returns cached results for a completed job (if user refreshes page).

### 3.3 New Dependencies

Add to `requirements.txt`:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
sse-starlette>=1.8.0
pdfplumber>=0.10.0
```

### 3.4 Server Entry Point (`api/server.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import takeoff

app = FastAPI(title="MEP Takeoff Pro", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(takeoff.router)
```

---

## 4. FRONTEND ARCHITECTURE

### 4.1 App State Machine

Three states. No router. One state variable in `App.tsx`.

```
idle → processing → results
 ↑                      |
 └────── (reset) ───────┘
```

### 4.2 Page Layouts

#### Upload Page (idle state)

```
┌──────────────────────────────────────────────────────┐
│  HEADER: "MEP Takeoff Pro"                           │
├──────────────────────────────────────────────────────┤
│                                                       │
│   ┌─────────────────────────────────────────────┐    │
│   │                                              │    │
│   │     📄  Drop electrical drawings PDF here    │    │
│   │         or click to browse                   │    │
│   │                                              │    │
│   └─────────────────────────────────────────────┘    │
│                                                       │
│   [Upload & Process]  (appears after file selected)  │
│                                                       │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │ ⚡ < 60s  │  │ 🎯 97%   │  │ 📊 119    │         │
│   │ Process  │  │ Accuracy │  │ Line     │         │
│   │ Time     │  │ Proven   │  │ Items    │         │
│   └──────────┘  └──────────┘  └──────────┘         │
│                                                       │
└──────────────────────────────────────────────────────┘
```

- Drag-and-drop zone (shadcn Card, dashed border, .pdf only)
- Show filename + size after selection, enable "Upload & Process"
- POSTs file to `/api/takeoff`, gets job_id, transitions to processing
- Three stat cards at bottom

#### Processing Page (processing state)

```
┌──────────────────────────────────────────────────────┐
│  HEADER                                              │
├──────────────────────────────────────────────────────┤
│                                                       │
│   Processing: [filename.pdf]                         │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 67%                │
│                                                       │
│   ✅ Step 1: PDF Processing         11 sheets found  │
│   ✅ Step 2: Reading Schedules      70 items parsed  │
│   🔄 Step 3: Counting Symbols...                     │
│   ○  Step 4: Routing Analysis                        │
│   ○  Step 5: Business Rules                          │
│   ○  Step 6: Generating Output                       │
│                                                       │
│   Elapsed: 00:12.4                                    │
└──────────────────────────────────────────────────────┘
```

- Progress bar = current step / 6
- StepCards: ○ pending, 🔄 active (spinner), ✅ complete (with result summary)
- Elapsed timer
- On `complete` SSE event → transition to results

#### Results Dashboard (results state)

```
┌──────────────────────────────────────────────────────┐
│  HEADER                         [New Takeoff] [CSV]  │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐            │
│  │ 119  │  │ 12s  │  │ 54   │  │ 65   │            │
│  │Items │  │Time  │  │Count │  │Deriv │            │
│  └──────┘  └──────┘  └──────┘  └──────┘            │
│                                                       │
│  [All] [Fixtures] [Controls] [Power] [Tech]          │
│  [Demo] [Derived] [Accuracy*]                        │
│                    (* only if IVCC project detected)  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │ Item #  Description              Qty           │  │
│  │ F2      2'x4' LED Lay-In         6             │  │
│  │ F3      4' LED Strip             10             │  │
│  │ ...                                             │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

- StatsBar: total items, time, counted, derived
- Category tabs
- MaterialTable: Item #, Description, Quantity
- "Accuracy" tab ONLY if `results.validation` is not null
- CSV export button
- "New Takeoff" resets to idle

#### Accuracy Tab (conditional — IVCC only)

```
┌──────────────────────────────────────────────────────┐
│  ACCURACY: AI vs. Senior Estimator                   │
│                                                       │
│  97% Match Rate  (115/119 exact or close)            │
│  ████████████████████████████████████████░░ 97%       │
│                                                       │
│  [Recharts horizontal bar chart by category]          │
│  Fixtures:    100%  ████████████████████████          │
│  Controls:    100%  ████████████████████████          │
│  Power:       100%  ████████████████████████          │
│  Technology:  100%  ████████████████████████          │
│                                                       │
│  Item         Estimator  AI    Diff  Status           │
│  F2                6      6      0   EXACT            │
│  Cat 6 Jack       92     92      0   EXACT            │
│  Power Pack       14     14      0   EXACT            │
└──────────────────────────────────────────────────────┘
```

### 4.3 Components

| Component | What it does |
|-----------|-------------|
| `Header.tsx` | App name, nav actions (New Takeoff, Export) |
| `UploadZone.tsx` | Drag-and-drop PDF upload, file preview |
| `PipelineProgress.tsx` | 6 step cards + progress bar + timer |
| `StepCard.tsx` | Single step: pending/active/complete with result |
| `ResultsDashboard.tsx` | StatsBar + Tabs + Table/Accuracy |
| `MaterialTable.tsx` | shadcn Table: Item #, Description, Qty |
| `StatsBar.tsx` | Row of metric cards |
| `AccuracyComparison.tsx` | Overall %, bar chart, detail table |
| `AccuracyChart.tsx` | Recharts horizontal BarChart by category |

### 4.4 Single Hook: `useTakeoff.ts`

```typescript
interface UseTakeoffReturn {
  state: 'idle' | 'processing' | 'results'
  uploadAndProcess: (file: File) => Promise<void>
  currentStep: number
  steps: PipelineStep[]
  elapsedTime: number
  results: TakeoffResults | null
  reset: () => void
}
```

### 4.5 Types (`src/lib/types.ts`)

```typescript
export type AppState = 'idle' | 'processing' | 'results'
export type StepStatus = 'pending' | 'active' | 'complete' | 'error'

export interface PipelineStep {
  step: number
  name: string
  status: StepStatus
  result?: Record<string, any>
}

export interface ValidationItem {
  item: string
  expected: number
  actual: number
  difference: number
  status: 'exact' | 'close' | 'miss'
}

export interface TakeoffValidation {
  available: boolean
  exact_matches: number
  close_matches: number
  total_items: number
  accuracy_pct: number
  details: ValidationItem[]
}

export interface TakeoffResults {
  job_id: string
  new_materials: Record<string, number>
  demo_materials: Record<string, number>
  derived_materials: Record<string, number>
  panel_materials: Record<string, number>
  validation: TakeoffValidation | null
  summary: {
    total_line_items: number
    processing_time_sec: number
  }
}

export type MaterialCategory =
  | 'all' | 'fixtures' | 'controls' | 'power'
  | 'technology' | 'demo' | 'derived' | 'accuracy'
```

### 4.6 Design

- **Header:** dark navy `#1e3a5f`
- **Body:** white / `#f8fafc`
- **Primary blue:** `#2563eb`
- **Exact match:** green `#16a34a`
- **Close match:** yellow `#eab308`
- **Miss:** red `#dc2626`
- **Quantities:** `font-mono tabular-nums`
- **Viewport:** 1280px+ only, no mobile

---

## 5. BUILD PHASES

### Phase 1: Backend
1. Create `api/` directory with `server.py`, `routes/takeoff.py`
2. Install: `pip install fastapi uvicorn sse-starlette python-multipart pdfplumber`
3. Implement POST upload + GET SSE stream
4. SSE stream runs the REAL `TakeOffSystem` pipeline
5. Include IVCC detection + validation in `complete` event
6. Test with curl

**✅ Check-in: "Backend accepts PDF upload, runs pipeline, streams SSE events."**

### Phase 2: Frontend Scaffolding
1. Create Vite React TS project
2. Tailwind + shadcn/ui setup
3. `App.tsx` with 3-state machine
4. `Header.tsx`

**✅ Check-in: "App renders. Tailwind and shadcn working."**

### Phase 3: Upload Page
1. `UploadZone.tsx` (drag-and-drop)
2. Landing page with stat cards
3. Wire upload button → POST → transition to processing

**✅ Check-in: "Can select a PDF and transition to processing."**

### Phase 4: Processing Animation
1. `useTakeoff.ts` hook
2. `StepCard.tsx` + `PipelineProgress.tsx`
3. SSE connection, handle events, auto-transition to results

**✅ Check-in: "Upload PDF → watch 6 steps → auto-shows results."**

### Phase 5: Results Dashboard
1. `StatsBar.tsx`, `MaterialTable.tsx`, `ResultsDashboard.tsx`
2. Category tabs
3. "New Takeoff" + CSV export buttons

**✅ Check-in: "Full material list shows in categorized tabs."**

### Phase 6: Accuracy Tab
1. `AccuracyChart.tsx` + `AccuracyComparison.tsx`
2. Only visible when `validation` is not null
3. Test with IVCC PDF

**✅ Check-in: "Accuracy tab shows 97% for IVCC. Demo complete."**

### Phase 7: Polish
1. Error handling
2. Loading states
3. End-to-end test
4. README

---

## 6. RULES FOR CLAUDE CODE

1. **DO NOT modify any files in `takeoff_system/`.** Wrap it, don't change it.
2. **Keep it simple.** No state libraries. React state + one hook.
3. **No router.** State variable in App.tsx.
4. **SSE, not WebSocket.**
5. **Numbers in monospace.** `font-mono tabular-nums`
6. **Accuracy tab is conditional.** Only when `results.validation` is not null.
7. **The pipeline runs for real.** SSE endpoint calls actual TakeOffSystem on the uploaded PDF.
8. **IVCC detection:** Match sheet numbers against known IVCC pattern. If match → run validation. If not → skip.
9. **Dark header, light body.**
10. **One file at a time.** No batch upload.

---

## 7. DATA MAPPING

### Category mapping for tabs:

| Tab | Source | Keys |
|-----|--------|------|
| Fixtures | `new_materials` | F2-F9, X1, X2, *Linear LED*, F10-*, F11-* |
| Controls | `new_materials` | *Occupancy Sensor, Daylight Sensor, Wireless Dimmer |
| Power | `new_materials` | *Receptacle, *Switch |
| Technology | `new_materials` | Cat 6 Jack |
| Demo | `demo_materials` | All keys |
| Derived | `derived_materials` + `panel_materials` | All keys |
| Accuracy | `validation.details` | Only if validation not null |

### Item numbers:
Use `ITEM_NUMBERS` from `takeoff_system/output_generator.py`.

---

## 8. RUNNING IT

```bash
# Terminal 1
uvicorn api.server:app --reload --port 8000

# Terminal 2
cd frontend && npm run dev
```

Open `http://localhost:5173`. Upload PDF. Watch it work.

---

*Version 2.0 — 2026-03-12*
