# STARTUP Guide

This file explains how to start Agentic-ChemRAG locally.

## Prerequisites

- Python 3.10+
- Node.js 16+ (18+ recommended)
- Local PDF data prepared under `data/pdf/`

## 1) Start Backend

From the repository root:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend should be available at:

- `http://localhost:8000`

## 2) Build Vector Database (first run or after data updates)

From `backend/`:

```bash
python build_vector_db.py
```

Expected inputs/outputs:

- Input PDFs: `../data/pdf/`
- Extracted images: `../data/extracted_images/`
- Vector DB: `../data/chroma_db/`

## 3) Start Frontend

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

Frontend should be available at:

- `http://localhost:5173`

## 4) Connectivity Check

Simple backend health check via chat endpoint:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"local-test","question":"What is this project for?"}'
```

## Troubleshooting

1. Backend fails to start:
- Verify Python version and dependency installation.
- Check if port 8000 is occupied.

2. Frontend fails to start:
- Remove and reinstall dependencies in `frontend/`.

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

3. Images not shown:
- Confirm backend static mount for `/data` is active.
- Confirm files exist under `data/extracted_images/`.

## Data Governance Reminder

By design, these paths are local-only and ignored by Git:

- `data/pdf/`
- `data/chroma_db/`
- `data/extracted_images/`

If you need reproducibility, share scripts and metadata, not full local datasets.