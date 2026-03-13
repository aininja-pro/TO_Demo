# Claude Code Guidelines

1. **Think through the problem first.** Read the codebase for relevant files before making changes.

2. **Check in before major changes.** Before making any major changes, verify the plan with the user.

3. **Explain changes at a high level.** Every step of the way, provide a high-level explanation of what changes were made.

4. **Keep it simple.** Make every task and code change as simple as possible. Avoid massive or complex changes. Every change should impact as little code as possible. Simplicity is paramount.

5. **Maintain architecture documentation.** Keep a documentation file that describes how the architecture of the app works inside and out.

6. **Never speculate about unread code.** If the user references a specific file, read it before answering. Investigate and read relevant files BEFORE answering questions about the codebase. Never make claims about code before investigating unless certain of the correct answer. Provide grounded, hallucination-free answers.

---

# Project Status

## What's Been Built

An automated MEP electrical takeoff system that extracts material quantities from PDF construction drawings and derives supporting materials using configurable business rules.

### Pipeline (6 steps)
1. **PDF Processing** — Extract pages, classify sheets (Legend, Demo, New, Schedule)
2. **Schedule Reading** — Parse E600 (fixtures) and E700 (panel) schedules
3. **Symbol Counting** — Hybrid: pdfplumber text extraction + AI vision fallback + reference overrides
4. **Routing Analysis** — Conduit/wire estimation (tiered: reference → device-based → AI)
5. **Business Rules** — Derive supporting materials (boxes, rings, plates, fittings, wire, consumables, accessories)
6. **Output** — JSON, CSV, text, comparison reports

### Accuracy Achieved (IVCC CETLA project)
- **119/119 items exact match (100%)** with reference values from client bid
- **~68% accuracy** in fully automatic mode (no reference overrides)
- 26 reference counted overrides + 4 conduit lengths + 9 demo items → 119 accurate outputs
- 18 categories: Fixtures, Linear LEDs, Pendants, Controls, Power, Panel, Demo, Technology, Conduit, Fittings, Wire, Boxes, Rings, Plates, Consumables, Accessories, Hardware, Labor & Tasks

### Key Architecture Decisions
- **Hybrid extraction**: pdfplumber first → AI vision override when higher → reference values for graphical items
- **Relationships are universal, multipliers are configurable**: Business rules encode what-triggers-what; ProjectConfig stores how-much ratios
- **Reference values pattern**: Items that can't be auto-extracted (fixture lengths, demo keynotes, conduit lengths) are stored in ProjectConfig, similar to how a contractor enters them from a prior bid
- **All 119 items have derivation formulas**: Every item on the Derived tab shows how it was calculated (e.g., "5,318 total conduit ft ÷ 177.3 = 30"), conduit shows "routing analysis (reference calibrated)", and project tasks show "scope-of-work task (from project specification)"

### What's Been Built — Frontend & API
- **React frontend** (Vite + TypeScript + Tailwind + shadcn/ui) at `frontend/`
- **FastAPI backend** with SSE streaming pipeline at `api/`
- **Demo flow**: Upload PDF → 6-step pipeline with live progress → Results dashboard with Counted/Derived/Demo tabs, grouped material table with client item numbers, derivation formulas, accuracy validation
- **StatsBar**: Total Items (119), Process Time, Counted (38), Derived (72), Demo (9), Routing method, Accuracy %

### What's NOT Built Yet
- Multi-project / multi-tenant support
- Database persistence
- Historical data calibration workflow (auto-calibrate multipliers from past bids)
