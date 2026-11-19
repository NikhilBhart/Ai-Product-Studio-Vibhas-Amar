# System architecture

## Architecture style
A control-plane / execution-plane split with asynchronous, stateful agent orchestration.

- Control plane: Next.js dashboard + Spring Boot API.
- Agent plane: Python LangGraph service.
- Data plane: PostgreSQL + pgvector and object storage for artifacts.
- Execution plane: disposable, isolated build sandboxes for generated code.
- Integration plane: LLM, coding engines, Figma, GitHub, and deployment providers.

## Service responsibilities

### Next.js frontend
Project creation, project dashboard, workflow timeline, approvals, artifact viewer, settings, integration connection screens, and deployment results.

### Spring Boot API
Authentication/authorization, tenant and project management, project lifecycle, artifact metadata, integration credentials references, audit trail, billing/cost metadata, and calls to LangGraph.

### LangGraph service
Stateful agent graph, prompt and tool routing, product specification generation, engine selection, agent retries, and event updates.

### PostgreSQL + pgvector
Relational source of truth for tenants, users, projects, runs, requirements, artifacts, integrations, deployments, and audit events. pgvector stores embeddings for project context retrieval; it is not a substitute for relational constraints.

### Sandbox
Run untrusted generated code in short-lived isolated containers or microVMs with CPU, memory, time, filesystem, network egress, and secret access restrictions. Never mount platform secrets into the generated app runtime.

## Data flow
1. Browser sends idea to Spring Boot.
2. Spring Boot persists project and starts an agent run.
3. LangGraph produces structured artifacts and emits progress events.
4. Spring Boot persists artifact metadata and exposes project status.
5. Coding adapter writes source into isolated workspace.
6. QA agent runs checks and sends failures into bounded repair loops.
7. Documentation agent generates documents from approved canonical artifacts.
8. GitHub and deployment adapters publish source and deploy.
9. Deployment verifier checks HTTP health and key browser journeys.

## Security boundaries
- Encrypt integration tokens at rest; use a managed secret store in production.
- Use tenant-scoped authorization in every query.
- Use short-lived, scoped GitHub and Cloudflare tokens.
- Use sandbox isolation and deny-by-default network access.
- Scan dependencies and generated artifacts.
- Redact credentials and personal data from model traces.
- Keep immutable audit events for publishing and permission changes.
