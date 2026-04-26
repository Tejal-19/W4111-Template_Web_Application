# FastAPI Starter

Minimal FastAPI application with a couple endpoints and a small pytest suite.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Option A (recommended): run via uvicorn
uvicorn app.main:app --port 8000

# Option B: run via the module entrypoint
#   (respects env vars: HOST, PORT)
python -m app.main
```

Then open:

* `http://localhost:8000/`
* `http://localhost:8000/health`

## Run tests

```bash
pytest -q
```
