# LinkForge

Distributed URL Shortener and Rate Limiter built for backend engineering and system design practice.

## Features

- Short URL creation
- Custom aliases
- Optional expiry timestamps
- Base62 short code generation
- Collision handling
- Redirect endpoint
- Click tracking
- Analytics dashboard
- Redis-backed rate limiting with local fallback
- PostgreSQL-ready storage with SQLAlchemy
- Docker Compose setup
- GitHub Actions CI
- System design documentation
- Load testing plan with Locust

## Tech Stack

**Frontend:** React, TypeScript, Tailwind CSS, Recharts, Vite

**Backend:** FastAPI, SQLAlchemy, Pydantic

**Database:** SQLite locally, PostgreSQL in production

**Cache and Rate Limiting:** Redis

**DevOps:** Docker, Docker Compose, GitHub Actions

## Project Structure

```text
distributed-url-shortener-rate-limiter/
|-- api/                 # FastAPI backend
|-- frontend/            # React dashboard
|-- docs/                # System design and load test notes
|-- load-tests/          # Locust load test script
|-- docker-compose.yml
|-- package.json
`-- README.md
```

## Local Setup

### Backend

```bash
cd api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend docs:

```text
http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Docker Setup

```bash
docker compose up --build
```

Services:

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## API Overview

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/links` | Create a short URL |
| `GET` | `/api/links` | List recent links |
| `GET` | `/api/links/{code}/analytics` | View analytics |
| `GET` | `/{code}` | Redirect to original URL |
| `GET` | `/health` | Health check |

## System Design

Read the full design document:

[docs/SYSTEM_DESIGN.md](docs/SYSTEM_DESIGN.md)

## Load Testing

Read the load test plan:

[docs/LOAD_TEST_RESULTS.md](docs/LOAD_TEST_RESULTS.md)

## Resume Bullet

Built a distributed URL shortener and rate limiter using FastAPI, React, PostgreSQL-ready SQLAlchemy models, Redis-backed fixed-window rate limiting, Base62 encoding, collision handling, click analytics, Docker, and CI.

## Future Improvements

- Redis read-through cache for hot redirects
- Async analytics pipeline using Celery/RQ/Kafka
- User accounts and API keys
- Abuse detection and IP reputation
- GeoIP enrichment
- Prometheus/Grafana observability
- Database migrations with Alembic
