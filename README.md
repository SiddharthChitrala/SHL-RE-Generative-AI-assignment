# SHL Assessment Recommendation System

🎯 **Project:** SHL Assessment Recommender

A small retrieval + recommendation app that returns SHL individual assessments given a natural language query or job description. The project includes a FastAPI backend, an interactive Streamlit frontend, a data processing script to extract assessments, optional embeddings + FAISS for vector search, and helper scripts for tests and PDF extraction.

---

## ✅ Features

- Extract SHL product catalog into `shl_assessments.csv` (from provided Excel dataset).
- TF-IDF retrieval-based recommender (default).
- Optional embeddings + FAISS index (requires heavy ML deps).
- FastAPI endpoints: GET `/health`, POST `/recommend`.
- Streamlit frontend for interactive usage and CSV download.
- Script to generate predictions for the provided unlabeled test set (`test_predictions.csv`).

---

## ⚙️ Requirements (Recommended)

- Python 3.11 (recommended) or 3.10. Python 3.12 may have wheel/build issues for `numpy`, `sentence-transformers`, and `faiss`.
- PowerShell on Windows (instructions below assume PowerShell).

Optional (for embeddings):
- `sentence-transformers`, `faiss-cpu` (install via conda for best results)

---

## Quickstart (no embeddings)

1. Activate the virtual environment (PowerShell):

```powershell
.\shl_simple_env\Scripts\Activate.ps1
```

2. Install Python deps (lightweight deps):

```powershell
pip install -r requirements.txt
```

> If `numpy` build fails, upgrade build tools first:
> ```powershell
> pip install -U pip setuptools wheel
> ```

3. Generate the assessments CSV without embeddings:

```powershell
python data_processor.py --no-embeddings
# Produces: shl_assessments.csv
```

4. Run the backend (development):

```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
# or: python app.py
```

5. Run smoke tests (make sure backend is reachable locally):

```powershell
python run_smoke_tests.py
```

6. Start the frontend (interactive):

```powershell
streamlit run streamlit_app.py
```

7. Generate test predictions (produces `test_predictions.csv`):

```powershell
# Optionally set GEMINI_API_KEY in this session if you want LLM re-ranking
$env:GEMINI_API_KEY = "YOUR_KEY_HERE"
python generate_test_predictions.py
```

8. Extract the assignment PDF text (helper):

```powershell
python extract_pdf_text.py
# Produces: assignment_text.txt
```

---

## Enabling embeddings & FAISS (optional)

If you want vector search using `sentence-transformers` + `faiss`, prefer a conda environment with prebuilt wheels.

Recommended (conda):

```bash
conda create -n shl-env python=3.11 -y
conda activate shl-env
conda install -c conda-forge faiss-cpu sentence-transformers -y
pip install -r requirements.txt
```

Or try pip with prebuilt binaries (may still fail on some platforms):

```powershell
pip install -U pip setuptools wheel
pip install sentence-transformers faiss-cpu --prefer-binary
```

Once installed, run without the `--no-embeddings` flag:

```powershell
python data_processor.py
# Produces: embeddings files and a faiss index (if enabled)
```

---

## API Reference

Base URL: `http://localhost:8000`

- GET `/health`
  - Returns: `{ "status": "healthy" }`

- POST `/recommend`
  - Request JSON (example):

```json
{ "query": "Java developer who collaborates with business teams" }
```

  - Response JSON (example snippet):

```json
{
  "recommended_assessments": [
    {
      "url": "https://www.shl.com/...",
      "name": "Assessment Name",
      "adaptive_support": "No",
      "description": "...",
      "duration": 40,
      "remote_support": "Yes",
      "test_type": ["Knowledge & Skills"]
    }
  ]
}
```

Sample curl:

```bash
curl -X POST "http://localhost:8000/recommend" -H "Content-Type: application/json" -d '{"query": "Java developer who collaborates"}'
```

---

## Submission CSV format (Appendix 3)

The CSV should have two columns: `Query` and `Assessment_url` with one row per recommendation. If a query has multiple recommendations, each goes on its own row.

Example:

```
Query,Assessment_url
"Query 1","https://.../assessment-1"
"Query 1","https://.../assessment-2"
"Query 2","https://.../assessment-a"
```

Make sure the CSV matches the exact format required by the assignment pipeline.

---

## Troubleshooting & Notes

- Streamlit may stop automatically in headless or non-interactive automated runners — run it interactively on your machine.
- If `pip install -r requirements.txt` fails due to `numpy` or `faiss` builds, use a conda environment or switch to Python 3.10/3.11 where prebuilt wheels exist.
- `data_processor.py` has `--no-embeddings` to allow quick CSV generation without installing heavy ML deps.
- The code uses TF-IDF retrieval by default; GEMINI/LLM re-ranking is optional and requires setting `GEMINI_API_KEY`.

---

## Project structure (important files)

- `app.py` — FastAPI application & endpoints
- `rag_system.py` — recommender logic (TF-IDF, optional LLM)
- `data_processor.py` — build dataset CSV and optional embeddings
- `streamlit_app.py` — frontend UI
- `generate_test_predictions.py` — create `test_predictions.csv` from test queries
- `run_smoke_tests.py` — quick API tests
- `extract_pdf_text.py` — helper to extract the assignment PDF text

---
# Test 1: API Health Check
curl https://shl-re-generative-ai-assignment.onrender.com/health

# Test 2: Frontend Loading
# Visit in browser: https://shl-re-generative-ai-assignment-5a6qn3stbsjntc2h7ib2af.streamlit.app/
