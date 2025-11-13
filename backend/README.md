# Store Assistant Backend

FastAPI backend powering Malayalam + English NL2SQL workflows for small retail stores in Kerala. Handles CSV uploads, automatic schema detection, SQL generation via OpenAI, safe query execution on SQLite, and Malayalam/English explanations for results.

## Features

- CSV upload with automatic SQLite table creation
- Dataset registry for uploaded store data
- Schema inspection and sample statistics
- Natural-language-to-SQL using OpenAI GPT models (Malayalam, Manglish, or English)
- Safe SQL execution with guardrails, row limits, and simple sandboxing
- Automatic visualization suggestions (tables, metrics, charts)
- Malayalam or English natural-language explanations for query results
- REST API ready for the existing React frontend

## Getting Started

1. **Install dependencies**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Create environment file**

```bash
cp .env.example .env
```

Edit `.env` with:

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
DATA_STORAGE_PATH=./storage
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

3. **Run the server**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Open API docs**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/routes/     # FastAPI routers for datasets, query, NL2SQL, health
│   ├── core/           # Settings + logging utilities
│   ├── models/         # Pydantic request/response schemas
│   ├── services/       # Dataset manager, NL2SQL, SQL executor, explanations
│   └── utils/          # Helper utilities (language detection, string helpers)
├── storage/            # Uploaded datasets (gitignored)
├── main.py             # FastAPI entrypoint (imports from app.*)
├── requirements.txt
└── README.md
```

## Frontend Integration

Refer to `API_INTEGRATION.md` in the project root for endpoint details on upload, NL2SQL ask, manual SQL execution, and visualization metadata.

## Deployment

- Designed to deploy on Render/Railway (Gunicorn + Uvicorn workers)
- SQLite files stored on disk (`DATA_STORAGE_PATH`), ensure persistent volume in production
- If you plan to enable NL2SQL + explanations, ensure `OPENAI_API_KEY` is supplied (install the optional `openai` package separately when needed)

## Testing

- Unit tests (coming soon) will live under `tests/`
- Use `pytest` to run backend tests once added

