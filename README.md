# Store Assistant Monorepo

This repository hosts both the Kerala SMB NL2SQL frontend (Next.js) and the FastAPI backend.

## Directory Layout

- `frontend/` – Next.js 14 application (chat UI, components, Tailwind config, docs)
- `backend/` – FastAPI service for CSV ingestion, NL2SQL, and analytics APIs
- `API_INTEGRATION.md` – REST contract between frontend and backend

## Quick Start

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd ../backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

See `frontend/README.md` and `backend/README.md` for detailed instructions.
