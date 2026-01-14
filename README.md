# Infant Meal Planner

A web application that helps parents plan and manage complementary feeding meals for their babies. The app generates AI-powered meal plans with safety validation, provides shopping lists, and tracks meal outcomes.

## Features

- **Account Management**: Sign up, login, and create baby profiles
- **AI Meal Planning**: Generate 3-day or 7-day meal plans tailored to your baby's age, feeding style, and preferences
- **Safety Validation**: All plans are validated against CDC safety guidelines before display
- **Shopping Lists**: Export categorized shopping lists with batch prep suggestions
- **Meal Logging**: Track meal outcomes (ate/partial/refused) and reactions
- **Food History**: View introduced foods with preference tracking

## Tech Stack

- **Backend**: FastAPI (Python 3.11), SQLModel, Alembic, LangChain/LangGraph
- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS, shadcn/ui
- **Database**: PostgreSQL 15+
- **AI**: OpenAI GPT-4o-mini for meal plan generation

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- OpenAI API key

## Quick Start

### 1. Clone and Setup

```bash
cd meal_planner
```

### 2. Environment Configuration

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` with your values:
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `OPENAI_API_KEY`: Your OpenAI API key
- Database credentials (if not using Docker defaults)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (using Docker)
cd ..
docker compose up -d postgres

# Run migrations
cd backend
alembic upgrade head

# Seed reference data
python -m app.seed
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create frontend environment file
cp ../.env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development

### Backend Commands

```bash
# Run tests
pytest

# Format code
ruff format .
black .

# Lint
ruff check .

# Type check
mypy app/

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend Commands

```bash
# Run tests
npm test

# Lint
npm run lint

# Format
npx prettier --write .
```

### Docker Compose

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Production Deployment

### Backend Deployment

The backend includes a production-ready Dockerfile:

```bash
cd backend

# Build the image
docker build -t meal-planner-backend .

# Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@db:5432/meal_planner" \
  -e SECRET_KEY="your-production-secret-key" \
  -e OPENAI_API_KEY="sk-your-key" \
  -e ENVIRONMENT="production" \
  -e CORS_ORIGINS_PRODUCTION="https://your-frontend.com" \
  meal-planner-backend
```

### Environment Variables (Production)

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | Secret key for JWT signing | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `ENVIRONMENT` | Set to "production" | Yes |
| `CORS_ORIGINS_PRODUCTION` | Comma-separated allowed origins | Yes |

### Frontend Deployment (Vercel)

```bash
cd frontend

# Deploy to Vercel
npx vercel

# Set environment variable in Vercel dashboard:
# NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

### Health Checks

- Backend: `GET /health` returns `{"status": "ok"}`
- Database: `GET /health/db` returns connection status

## Project Structure

```
meal_planner/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API route handlers
│   │   ├── models/      # SQLModel database models
│   │   ├── schemas/     # Pydantic request/response schemas
│   │   ├── services/    # Business logic
│   │   ├── rules/       # Safety validation rules
│   │   ├── planner/     # LangGraph meal plan generation
│   │   └── core/        # Configuration and database
│   ├── alembic/         # Database migrations
│   ├── tests/           # Test suite
│   └── seed/            # Seed data
├── frontend/            # Next.js frontend
│   ├── src/
│   │   ├── app/         # Next.js App Router pages
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities and API client
│   └── public/
├── specs/               # Design documents
└── docker-compose.yml   # PostgreSQL service
```

## Safety & Validation

All meal plans are validated against:
- CDC guidelines (honey under 12 months, choking hazards)
- Baby's age and feeding style
- Allergen and avoid list restrictions
- Age-appropriate meal frequency (WHO guidance)

## API Endpoints

### Authentication
- `POST /auth/register` - Create account
- `POST /auth/jwt/login` - Login with credentials
- `POST /auth/jwt/logout` - Logout
- `POST /auth/forgot-password` - Request password reset

### Baby Profile
- `GET /baby-profile/me` - Get current profile
- `POST /baby-profile` - Create profile
- `PUT /baby-profile/me` - Update profile
- `DELETE /baby-profile/me` - Delete profile

### Meal Plans
- `GET /plans` - List plans
- `POST /plans` - Generate new plan
- `GET /plans/{id}` - Get specific plan
- `PATCH /plans/{id}/swap-meal` - Swap a meal

### Logging
- `POST /logs/meal` - Log meal outcome
- `GET /logs/meal` - Get meal logs
- `GET /logs/today` - Get today's meals with status
- `POST /logs/reaction` - Log reaction
- `GET /logs/reaction` - Get reactions
- `GET /logs/foods/introduced` - Get food history

## Testing

```bash
# Run all backend tests
cd backend && pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/contract/      # Contract tests
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

