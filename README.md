# FastAPI Support System

A customer support ticket API built with FastAPI. Users can sign up, create tickets, and agents can reply and change ticket status. The project also has WebSocket live updates, Celery background tasks, rate limiting, pytest tests, and a browser test UI.

---

## Features

- JWT authentication with two roles: **user** and **agent**
- Users create tickets; only agents can reply and update status
- Real-time updates over WebSocket when a reply is sent or status changes
- Background tasks with Celery (log replies + simulated email notification)
- Rate limiting on signup, login, and ticket creation
- Automated API tests with pytest

---

## Tech stack

FastAPI · PostgreSQL · SQLAlchemy 2.0 (async) · Alembic · Redis · Celery · JWT (python-jose) · bcrypt · SlowAPI · pytest

---

## Project structure

```
app/
  main.py           # FastAPI app entry point
  core/             # config, security, deps, rate limit
  db/               # database connection
  models/           # User, Ticket, Reply
  schemas/          # request/response models
  api/              # auth, tickets, websocket routes
  celery_app/       # Celery setup and tasks
alembic/            # database migrations
static/             # test UI (HTML, CSS, JS)
tests/              # pytest tests
```

---

## Setup

**1. Install dependencies**

```bash
cd FastAPI_Support_System
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
```

Update `.env` with your PostgreSQL password and a secret key:

```
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/support_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
```

**3. Create database and run migrations**

```bash
psql -U postgres -h localhost
CREATE DATABASE support_db;
\q

alembic upgrade head
```

---

## How to run

Start these in separate terminals:

| Terminal | Command |
|----------|---------|
| 1 | `redis-server` |
| 2 | `uvicorn app.main:app --reload` |
| 3 | `celery -A app.celery_app.celery worker --loglevel=info` |

Open in browser:
- http://127.0.0.1:8000/docs — Swagger API documentation
- http://127.0.0.1:8000/ui — Test UI for manual testing

---

## API overview

### Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/signup` | Create user or agent account |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/me` | Get logged-in user info |

Login example:

```json
POST /auth/login
{ "email": "user@example.com", "password": "123456" }
```

Protected routes need this header:

```
Authorization: Bearer <your_token>
```

### Tickets

| Method | Path | Access | Description |
|--------|------|--------|-------------|
| POST | `/tickets` | Logged in | Create a ticket |
| GET | `/tickets` | Logged in | List tickets |
| GET | `/tickets/{id}` | Owner or agent | Get one ticket |
| POST | `/tickets/{id}/replies` | Agent only | Send a reply |
| PATCH | `/tickets/{id}/status` | Agent only | Update status |

Ticket status values: `open`, `in_progress`, `closed`

### WebSocket

```
ws://127.0.0.1:8000/ws/tickets/{ticket_id}
```

Clients connected to this URL get notified when an agent replies or changes ticket status.

---

## Celery tasks

When an agent sends a reply, two background tasks run:

- `log_reply` — saves reply info to `reply_logs.log`
- `send_email` — simulates email notification (also written to log file)

View logs:

```bash
cat reply_logs.log
```

---

## Rate limits

| Endpoint | Limit |
|----------|-------|
| POST `/auth/signup` | 5 per minute |
| POST `/auth/login` | 10 per minute |
| POST `/tickets` | 20 per minute |

Redis must be running for rate limiting to work.

---

## Running tests

```bash
pytest -v
```

Tests use an in-memory SQLite database. You do not need PostgreSQL or Redis running for pytest.

---

## Common problems

- **Database connection failed** — check `.env` and make sure PostgreSQL is running
- **429 Too Many Requests** — rate limit hit; wait a minute or restart Redis
- **Celery tasks not working** — make sure Redis and the Celery worker are both running
- **psql peer auth error** — use `psql -U postgres -h localhost`
