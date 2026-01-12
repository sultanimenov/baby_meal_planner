# Quickstart: Infant Meal Planner

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- OpenAI API key

## Environment Setup

### 1. Clone and navigate

```bash
cd meal_planner
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

Edit `.env` with your values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/meal_planner

# Auth (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Optional: LangSmith tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=baby-meal-planner
```

### 3. Database setup

Option A: Docker (recommended)

```bash
docker compose up -d postgres
```

Option B: Local PostgreSQL

```bash
createdb meal_planner
```

Run migrations:

```bash
alembic upgrade head
```

Seed reference data:

```bash
python -m app.seed
```

### 4. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Terminal 1: Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Verification Checklist

### Backend health

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### Database connection

```bash
curl http://localhost:8000/health/db
# Expected: {"status": "ok", "tables": [...]}
```

### Auth flow

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'

# Login (returns JWT cookie)
curl -X POST http://localhost:8000/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123" \
  -c cookies.txt

# Get profile (should return 404 for new user)
curl http://localhost:8000/baby-profile \
  -b cookies.txt
```

### Recipe seed verification

```bash
curl http://localhost:8000/recipes | jq '. | length'
# Expected: 50 (or your seed count)
```

## Development Commands

### Backend

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Format code
ruff format .
black .

# Type check
mypy app/

# Lint
ruff check .
```

### Frontend

```bash
# Run tests
npm test

# Type check
npm run type-check

# Lint
npm run lint

# Format
npm run format
```

### Database

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one
alembic downgrade -1

# Reset (careful!)
alembic downgrade base
alembic upgrade head
python -m app.seed
```

## Docker Compose (Full Stack)

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend

# Stop
docker compose down
```

## Troubleshooting

### "Connection refused" on database

Check PostgreSQL is running:

```bash
docker compose ps  # if using Docker
pg_isready -h localhost -p 5432  # if local
```

### "Invalid API key" on plan generation

Verify OpenAI key:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Frontend can't reach backend

Check CORS settings in `backend/app/main.py` include `http://localhost:3000`.

### Slow plan generation

- Check LangSmith traces if enabled
- Verify network connectivity to OpenAI
- Consider increasing timeout in frontend

## Next Steps

1. Create a user account at http://localhost:3000/signup
2. Complete baby profile onboarding
3. Generate your first meal plan
4. Test meal logging workflow

