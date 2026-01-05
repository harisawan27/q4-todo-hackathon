# Quickstart: Phase II Multi-User Web Todo Application

**Branch**: `001-multi-user-web` | **Date**: 2026-01-05

## Prerequisites

- Node.js 22+ (for Next.js 16)
- Python 3.13+
- Neon PostgreSQL database (provisioned)
- Git

## Environment Setup

### 1. Clone and Navigate

```bash
cd todo-phase-2
```

### 2. Backend Setup

```bash
# Create virtual environment
cd backend
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Unix/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 3. Backend Environment Variables

Edit `backend/.env`:

```env
# Database (from Neon dashboard)
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# Auth (shared with frontend - MUST match exactly)
BETTER_AUTH_SECRET=your-256-bit-secret-here

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 4. Frontend Setup

```bash
cd frontend
npm install

# Copy environment template
cp .env.example .env.local
```

### 5. Frontend Environment Variables

Edit `frontend/.env.local`:

```env
# Auth (shared with backend - MUST match exactly)
BETTER_AUTH_SECRET=your-256-bit-secret-here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_URL=http://localhost:3000
```

### 6. Generate Shared Secret

```bash
# Generate a secure 256-bit secret
openssl rand -base64 32
```

Copy this value to BOTH `backend/.env` and `frontend/.env.local`.

---

## Database Setup

### Run Migrations

```bash
cd backend

# Apply migrations (creates tables)
alembic upgrade head

# Or use SQLModel directly for development
python -c "from app.database import init_db; init_db()"
```

---

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at: http://localhost:8000

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend available at: http://localhost:3000

---

## Verification

### 1. Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"2026-01-05T..."}
```

### 2. API Docs

Open http://localhost:8000/docs for Swagger UI

### 3. Frontend

Open http://localhost:3000 and:
1. Click "Sign Up"
2. Enter email and password
3. Create a task
4. Verify task appears in list

---

## Common Issues

### Secret Mismatch

**Symptom**: 401 errors on all API calls

**Fix**: Ensure `BETTER_AUTH_SECRET` is identical in both `.env` files

### Database Connection

**Symptom**: 500 errors mentioning "connection"

**Fix**:
1. Verify `DATABASE_URL` is correct
2. Check Neon dashboard for connection string
3. Ensure `?sslmode=require` is present

### CORS Errors

**Symptom**: Browser console shows CORS errors

**Fix**: Backend must include frontend origin in CORS config:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Development Commands

### Backend

```bash
# Run tests
pytest

# Format code
black app tests
isort app tests

# Type check
mypy app

# Lint
ruff app tests
```

### Frontend

```bash
# Run tests
npm test

# Format code
npm run format

# Type check
npm run type-check

# Lint
npm run lint
```

---

## Project Structure

```
todo-phase-2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry
│   │   ├── database.py          # SQLModel engine/session
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── jwt_bearer.py    # JWT verification
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── task.py          # Task SQLModel
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py         # Task CRUD endpoints
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing/redirect
│   │   ├── (auth)/
│   │   │   ├── sign-in/page.tsx
│   │   │   └── sign-up/page.tsx
│   │   └── dashboard/
│   │       └── page.tsx         # Task list
│   ├── lib/
│   │   ├── auth.ts              # Better Auth config
│   │   └── api.ts               # API client
│   ├── components/
│   │   ├── task-list.tsx
│   │   ├── task-item.tsx
│   │   └── task-form.tsx
│   ├── .env.example
│   └── package.json
│
├── specs/001-multi-user-web/
│   ├── spec.md
│   ├── plan.md
│   ├── research.md
│   ├── data-model.md
│   ├── quickstart.md
│   └── contracts/openapi.yaml
│
└── CLAUDE.md
```

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement backend first (Backend-First strategy)
3. Implement frontend integration
4. Run security verification (AuthArchitect checklist)
