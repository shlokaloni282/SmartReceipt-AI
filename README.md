# SmartReceipt AI

**AI receipt-to-expense tracker** — upload a receipt photo, get suggested merchant / date / total, review and correct it, then save it to your expense history.

> **Status: In Progress.** The FastAPI extraction backend works end to end; the React frontend, full expense CRUD and the AI layers are being built. See the [status table](#project-status) for exactly what is and isn't done.

_(Project name is a placeholder — rename the repo, this title and the UI header together once the final name is chosen.)_

---

## Why this project

Typing expenses by hand is where most expense-tracking habits die. This project turns a photo of a paper receipt into a structured expense, with one rule built in: **the user always reviews OCR suggestions before anything is saved**, because OCR on real receipts is imperfect.

Audience for v1: individuals tracking personal spending. Business workflows (approvals, GST, audit trails) are future work.

---

## Project status

| Area                                                                               | Status                                     |
| ---------------------------------------------------------------------------------- | ------------------------------------------ |
| Streamlit prototype (Tesseract OCR, parser, SQLite, charts, CSV export)            | Done (earlier prototype)                   |
| FastAPI app with CORS and `POST /receipts/extract`                                 | Working (tested via Swagger UI at `/docs`) |
| OCR module (`ocr.py`) and rule-based parser (`parser.py`), no Streamlit dependency | Working, being improved                    |
| Pydantic schemas, SQLModel models, DB setup                                        | In progress                                |
| Expense CRUD endpoints, summary, CSV export                                        | In progress                                |
| Parser unit tests (`pytest`)                                                       | Started                                    |
| React + TypeScript frontend (upload, review, history, charts)                      | Scaffolded, not built yet                  |
| LLM fallback extraction + auto-categorization (Gemini)                             | Planned                                    |
| Spending insights                                                                  | Planned                                    |
| "Ask your receipts" (RAG)                                                          | Planned, last                              |

---

## Final tech stack

| Layer                  | Technology                                            |
| ---------------------- | ----------------------------------------------------- |
| Frontend               | React + TypeScript (Vite), Recharts for charts        |
| Backend                | Python, FastAPI, Pydantic, Uvicorn                    |
| OCR / image processing | Tesseract (`pytesseract`), OpenCV, Pillow             |
| Database               | SQLite locally (PostgreSQL if deployed or multi-user) |
| DB layer               | SQLModel                                              |
| Testing                | pytest, FastAPI `TestClient`                          |
| AI layer (planned)     | Gemini API for fallback extraction and categorization |
| Retrieval (planned)    | ChromaDB + embeddings for "Ask your receipts"         |

Optional, added only when needed: Alembic migrations, JWT auth, Docker Compose, TanStack Query and React Hook Form on the frontend.

---

## Architecture

```
React UI  ──►  FastAPI  ──►  core (OCR + parser)  ──►  Database
 (upload,       (REST,         preprocess, multi-pass      (SQLModel,
  review,       validation)    Tesseract, regex/rule       SQLite)
  history)                     field extraction
```

**User flow:** upload image → `/receipts/extract` returns _suggestions only_ (nothing saved) → user reviews and edits → save → history and summary update.

### How extraction works

1. **Preprocess** the image (orientation fix, grayscale, contrast enhancement, resize).
2. Run **Tesseract in multiple page-segmentation modes** and collect the text.
3. A **rule-based parser** (regex + weighted label scoring) extracts the merchant, date and total. It prefers lines like "grand total" / "net amount" / "amount payable" and ignores subtotal, tax and change lines.
4. Fields the parser can't find come back as `null`, and the review form warns the user instead of guessing.

---

## API

| Method         | Endpoint                        | Purpose                                                                    | Status      |
| -------------- | ------------------------------- | -------------------------------------------------------------------------- | ----------- |
| POST           | `/receipts/extract`             | Image in, suggested merchant/date/total + raw OCR text out (nothing saved) | Working     |
| POST           | `/expenses`                     | Save a user-confirmed expense                                              | In progress |
| GET            | `/expenses?category=&from=&to=` | Filtered history                                                           | In progress |
| PATCH / DELETE | `/expenses/{id}`                | Edit or remove an expense                                                  | In progress |
| GET            | `/expenses/summary`             | Totals by category                                                         | Planned     |
| GET            | `/expenses/export.csv`          | CSV export                                                                 | Planned     |

Interactive docs are served at `http://localhost:8000/docs` when the backend is running.

---

## Getting started

### Prerequisites

- Python 3.11+ and Node.js 18+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed and on your `PATH` (check with `tesseract --version`)

### Backend

```bash
cd backend
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\activate
# macOS/Linux:          source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` and try `POST /receipts/extract` with a receipt image.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`. The backend allows this origin via CORS.

### Tests

```bash
cd backend
python -m pytest
```

---

## Project structure

```
backend/
  app/
    main.py        # FastAPI app, CORS, routes
    schemas.py     # Pydantic request/response models
    models.py      # SQLModel tables
    db.py          # engine + session
    ocr.py         # preprocessing + Tesseract passes
    parser.py      # merchant / date / total extraction
  tests/
    test_parser.py
  requirements.txt
frontend/          # Vite + React + TypeScript
README.md
```

---

## Implementation goals

### Phase 1 — Working extraction API (done)

- [x] Move OCR and parsing into framework-independent modules
- [x] `POST /receipts/extract` returning suggestions and raw OCR text

### Phase 2 — Reliable OCR and parsing (current)

- [ ] Remove coloured ink (stamps, pen marks) and resize to a fixed target before OCR
- [ ] Parse each OCR pass separately and **vote** on fields; use agreement as a confidence score
- [ ] Date sanity checks (reject implausible years, try the next candidate)
- [ ] Total fallbacks for receipts with no "Total" label (e.g. "Items / Qty / amount" lines)
- [ ] Exclude "Total Items / Qty" lines from total detection
- [ ] More generic merchant detection (not tuned to one receipt)
- [ ] Unit tests covering each of the above

### Phase 3 — Complete backend

- [ ] Expense CRUD (`POST`, `GET` with filters, `PATCH`, `DELETE`)
- [ ] Summary and CSV export endpoints
- [ ] Duplicate-expense warning

### Phase 4 — React frontend

- [ ] Upload page with image preview
- [ ] Editable review form with warnings for undetected fields
- [ ] Expense history with category/date filters
- [ ] Spending-by-category chart

### Phase 5 — AI layers (only after the base app is solid)

- [ ] **LLM fallback extraction:** when rules have low confidence, Gemini returns schema-validated JSON; the user still reviews
- [ ] **Auto-categorization** from a fixed category list
- [ ] **Spending insights:** statistics are computed in Python/SQL, and the LLM only turns those numbers into plain-language suggestions (aggregates only, no raw receipt text sent)
- [ ] **"Ask your receipts" (RAG):** semantic search over saved expenses with cited sources; numeric questions answered by fixed SQL tools, never by the LLM doing arithmetic

### Evaluation

Accuracy numbers will only be published after measuring on a labelled set of synthetic receipts (target: 30–50 receipts, with per-field accuracy and, for RAG, Recall@k and groundedness).

---

## Known limitations

- OCR quality drops sharply on **crumpled, skewed or low-contrast** receipts, and on receipts with **stamps or handwriting** across the text. In those cases fields may come back empty or wrong — which is why the review step exists.
- Some receipts print the grand total without a "Total" label; handling these is part of Phase 2.
- Merchant detection is heuristic and may miss stylised logos.
- The parser currently targets Indian-style retail receipts (₹, DD/MM/YYYY); other formats are untested.
- No authentication yet; this is a single-user local app.

---

## Privacy

- Real receipts contain personal and purchase data. Keep them out of the repo (they are gitignored); use **synthetic or redacted** samples for screenshots and tests.
- When the LLM features are added, only aggregated data (category totals, merchant names) will be sent to the model, not raw OCR text.

---

## Author

**Shloka Loni** — [GitHub](https://github.com/shlokaloni282)
