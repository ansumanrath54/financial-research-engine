# ApexAlpha Financial Research Engine

A financial research application with a React interface and a FastAPI backend. Research requests are processed by a LangGraph workflow that gathers market and SEC data, validates a report, and streams progress to the browser. Reports and user sessions are stored in PostgreSQL.

## Requirements

- Python 3.10 or later
- Node.js and npm
- Docker with Docker Compose
- API credentials for a supported language model provider

## Local setup

### 1. Configure the backend

Create a local environment file from the template:

```sh
cp backend/.env.example backend/.env
```

Edit `backend/.env` and:

- Set `LLM_PROVIDER` to `claude`, `gemini`, `azure`, or `aws`.
- Add credentials for the selected provider.
- Set `JWT_SECRET_KEY` to a random secret of at least 32 characters.
- Set `DATABASE_URL` to the PostgreSQL connection string for your local database.

The `.env` file contains credentials and is ignored by Git. Do not commit it.

### 2. Start PostgreSQL

From the project root, start the database service:

```sh
docker compose up -d postgres
```

Compose maps PostgreSQL to port `5433` on your machine. The database name and role are configured in `docker-compose.yml`; make sure the credentials in `DATABASE_URL` match that configuration. PostgreSQL uses a persistent Docker volume, so changing Compose environment values does not change credentials for a database that has already been initialized.

### 3. Install and start the backend

From the project root:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Start the API from the `backend` directory so it loads `backend/.env`:

```sh
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

The API is available at <http://localhost:8000>. Interactive API documentation is at <http://localhost:8000/docs>.

### 4. Install and start the frontend

In a second terminal, from the project root:

```sh
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>.

## Authentication and API

Create an account in the application, then sign in. The backend also provides:

- `POST /api/auth/register` — create an account
- `POST /api/auth/token` — obtain a bearer token
- `GET /api/auth/me` — get the authenticated user
- `GET /api/sessions` and `GET /api/sessions/{thread_id}` — list and retrieve saved research sessions
- `POST /api/research/stream` — run research and receive progress as server-sent events

## Configuration notes

- Supported providers are selected with `LLM_PROVIDER`: `claude`, `gemini`, `azure`, or `aws`.
- Configure the credentials and model settings for the selected provider in `backend/.env`.
- The backend allows the Vite development origin at `http://localhost:5173`.
- If PostgreSQL reports an authentication error, verify that `DATABASE_URL` matches the credentials used when the Docker database volume was initialized.
