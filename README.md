# TrainECG App (Monorepo)

Monorepo with a FastAPI backend and a React (Vite) frontend.

## Structure

- backend/
- frontend/
- models/ (tracked with Git LFS)

## Quick Start (Docker)

1) Create frontend environment file:

```bash
cp frontend/.env.example frontend/.env
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

- Frontend uses `VITE_API_URL` from frontend/.env to reach the backend.
- Models are tracked with Git LFS (see .gitattributes).
