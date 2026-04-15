# TrainECG App (Monorepo)

Monorepo with a FastAPI backend and a React (Vite) frontend for ECG training and classification with AI support.

## Structure

- `backend/` - FastAPI backend with ML pipeline
- `frontend/` - React + Vite frontend
- `test/` - Automated testing suite (unit, functional, performance, usability)
- `models/` - ML artifacts (not tracked; runtime only)

## Quick Start (Docker)

1) Create root environment file (used by docker compose):

```bash
cp .env.example .env
```

2) Build and run:

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:9000

## Local Development (No Docker)

Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Notes

- Docker reads variables from `.env` in the repository root.
- For local development (no Docker), backend and frontend each use their own `.env` file copied from `backend/.env.example` and `frontend/.env.example`.
- ML models in `backend/models/` are pre-trained artifacts (best_model_Hybrid_CNN_LSTM_Attention.h5, etc.).
- Test suite in `test/` implements plan_pruebas.tex specifications (data quality, model metrics, functional, performance, usability).
