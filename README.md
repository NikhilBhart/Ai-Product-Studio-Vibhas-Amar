# AI Product Studio

A multi-agent product creation platform. A user submits a product idea; the platform turns it into a structured product brief, design specification, implementation plan, generated application, documentation, QA report, and deployment record.

## Current status

- **Phase 1:** repository foundation, product requirements, architecture, database schema, service skeletons, dashboard starter, and Figma plugin starter.
- **Phase 2:** Product Manager Agent with LangGraph, Pydantic-validated product brief, configurable OpenAI-compatible LLM adapter, PostgreSQL persistence through Spring Boot, and a product brief review dashboard.
- **Not production-ready:** authentication, real tenant isolation, secure code sandbox, complete coding-engine integrations, Figma design import workflow, GitHub automation, Cloudflare deployment, and automated browser QA are future phases.

## Architecture

- `frontend/`: Next.js dashboard for idea intake and product brief review.
- `backend/`: Spring Boot API for project lifecycle and persistence.
- `agent-service/`: Python FastAPI + LangGraph Product Manager Agent.
- `integrations/`: provider adapters and Figma plugin starter.
- `docs/`: requirements, architecture, workflow, engine comparison, phase guides, and acceptance criteria.
- `infra/`: PostgreSQL + pgvector schema and Docker Compose.

## Technology

- Frontend: Next.js + TypeScript
- Core API: Java 21 + Spring Boot 3.5.x + Maven
- Agent runtime: Python 3.12 + LangGraph + Pydantic
- Persistence: PostgreSQL 16 + pgvector
- LLM: provider-independent OpenAI-compatible Chat Completions adapter
- Source control: GitHub
- Deployment target: Cloudflare Workers/Pages for suitable workloads; container hosting for Spring Boot and Python services
- Design output: Figma Plugin API (user-authorized plugin execution)

## Prerequisites

- Node.js 20+
- Java 21+
- Maven 3.9+
- Python 3.12+
- uv
- Docker Desktop

## Start local infrastructure

From repository root:

```bash
docker compose -f infra/docker-compose.yml up -d
```

## Start Phase 2 services

### 1. LangGraph Product Manager Agent

```bash
cd agent-service
# Optional: copy .env.example to .env and configure a real provider
uv sync
uv run uvicorn app.main:app --reload --port 8001
```

Default `LLM_PROVIDER=mock` lets you test without an API key. To use a real model, configure the agent service environment:

```env
LLM_PROVIDER=gemini-compatible
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=your-provider-key
```

Check the provider's current model availability and account limits. Other OpenAI-compatible providers can be configured with their own base URL, model, and key. Never commit secrets.

### 2. Spring Boot API

```bash
cd backend
mvn spring-boot:run
```

Default API: `http://localhost:8080`.

The Docker PostgreSQL container is published on host port `5433` (container port `5432`) to avoid colliding with a locally installed PostgreSQL service. Spring Boot defaults to `localhost:5433`.

### 3. Next.js frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Test endpoints

```bash
curl http://localhost:8001/health
curl http://localhost:8001/v1/discovery/schema
curl -X POST http://localhost:8001/v1/discovery/run -H "Content-Type: application/json" -d '{"idea":"Build a social photo sharing platform for creators"}'
curl -X POST http://localhost:8080/api/projects -H "Content-Type: application/json" -d '{"idea":"Build a social photo sharing platform for creators"}'
```

See `docs/PHASE_2_TESTING_AND_SETUP.md` for persistence queries and troubleshooting.

## Database initialization note

`infra/schema.sql` is mounted into the PostgreSQL container's initialization directory. Docker executes that script only when the data directory is first initialized. For an existing named volume, apply the schema manually or create a fresh development volume after backing up data.

## Important provider strategy

The platform uses provider adapters rather than assuming every product exposes the same API. Bolt/WebContainer, Lovable API/MCP, Figma Plugin API, and direct LLM code generation have different capabilities and authorization models. See `docs/ENGINE_INTEGRATION_COMPARISON.md`.

## Security limitations

The current project-creation endpoint uses fixed development tenant/user UUIDs. Authentication and tenant isolation are not implemented. Do not expose this development service publicly or process real customer data until identity, authorization, rate limits, secret management, audit controls, and isolated generated-code execution are added.

#Instructions to run the code

Docker Running:

Get-Location

Test-Path .\infra\docker-compose.yml

Test-Path .\infra\schema.sql

output -- True

docker version

docker compose version

docker compose -f .\infra\docker-compose.yml config

docker compose -f .\infra\docker-compose.yml up -d

python: -->

cd agent-service

py -3.12 -m venv .venv

.\.venv\Scripts\Activate.ps1

If PowerShell blocks activation, run:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Then activate it again:
.\.venv\Scripts\Activate.ps1

Upgrade pip:
python -m pip install --upgrade pip

Install the AI dependencies:
pip install -r requirements.txt

Run your tests:
pytest -q

Terminal 1 — Python AI Agent
Python

cd agent-service
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8001

Runs LangGraph + FastAPI.

Terminal 2 — Spring Boot
Java 21

cd backend
mvn spring-boot:run

If using Neon, set the three database environment variables in this terminal before starting Maven.

Terminal 3 — Frontend
Next.js

cd frontend
npm install
npm run dev

Runs the website.

Database
Hosted or local

Use your hosted PostgreSQL database, or start the Docker PostgreSQL container if Docker is working.

Local URLs
Service URL
Frontend http://localhost:3000
Spring Boot http://localhost:8080
Python AI Agent http://localhost:8001
Agent health check http://localhost:8001/health
Backend health check http://localhost:8080/api/health

The startup order should be:

1. Database
2. Python AI Agent
3. Spring Boot backend
4. Next.js frontend
   Keep all three application terminals running while using the website.
