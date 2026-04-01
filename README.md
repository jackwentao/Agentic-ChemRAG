# Agentic-ChemRAG

Agentic-ChemRAG is a domain-focused RAG project for chemistry and materials documents.
It provides a FastAPI backend and a React frontend for multi-turn QA with source grounding.

## Project Structure

- `backend/`: API service, RAG chain, retriever and vector build scripts
- `frontend/`: React + Vite web UI
- `data/`: local data and generated artifacts
  - `pdf/`: local source PDFs (not tracked)
  - `extracted_images/`: parsed images from PDFs (not tracked)
  - `chroma_db/`: local vector database (not tracked)
- `assets/`: screenshots and static documentation assets
- `test/`: local test scratch area (optional)

## Tech Stack

- Backend: FastAPI, LangChain, ChromaDB, HuggingFace embeddings
- Frontend: React 18, TypeScript, Vite, Axios

## Data and Git Policy

This repository follows a local-data strategy:

1. `data/pdf/` is not version-controlled.
2. `data/chroma_db/` is not version-controlled.
3. Generated parsing outputs should stay local by default.

If you need to share sample data, use a small redacted demo set and document its source and license.

## Quick Start

### 1) Backend setup

```bash
cd backend
pip install -r requirements.txt
```

If you do not have `requirements.txt` yet, install the packages used in backend code first.

### 2) Build local vector DB

From `backend/`:

```bash
python build_vector_db.py
```

This reads local PDFs under `../data/pdf` and writes vectors to `../data/chroma_db`.

### 3) Run backend

From `backend/`:

```bash
python main.py
```

Backend default endpoint: `http://localhost:8000`

### 4) Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default endpoint: `http://localhost:5173`

## API Overview

`POST /api/chat`

Request:

```json
{
  "session_id": "user-session-id",
  "question": "your question"
}
```

Response (shape):

```json
{
  "answer": "...",
  "images": [
    {
      "image_path": "data/extracted_images/xxx.jpeg",
      "image_desc": "..."
    }
  ],
  "sources": [
    {
      "file_name": "some.pdf",
      "page": "12"
    }
  ]
}
```

## Notes

- Keep backend and frontend running in separate terminals.
- Keep local large files and generated DB artifacts out of Git.
- If you change API schema, update frontend types and rendering together.