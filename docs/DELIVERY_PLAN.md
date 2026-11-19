# Delivery plan

## Phase 1 — Foundation and product definition (current)
- Product vision, users, problems, outcomes, assumptions, uncertainties.
- Epic/capability/feature/story hierarchy and acceptance criteria.
- System architecture and service boundaries.
- Repository scaffold and local infrastructure.
- Provider comparison and integration contracts.

Exit criteria: documents reviewed; services start locally; project API health check works; database schema applies.

## Phase 2 — Working Product Manager Agent
- Structured schemas and validation.
- LangGraph discovery graph.
- LLM provider adapter and model routing.
- Persist PRD and backlog.
- Dashboard to view/edit/approve product artifacts.

Exit criteria: a one-sentence idea produces a validated product brief and hierarchy; tests cover missing/ambiguous inputs.

## Phase 3 — Design Agent and Figma
- User journey and screen inventory generation.
- Design tokens and component JSON schema.
- Figma plugin import flow.
- Editable frames and components in the active Figma file.

Exit criteria: plugin imports a sample design specification into editable Figma nodes.

## Phase 4 — Coding engine adapters
- Direct LLM coding workflow in sandbox.
- Bolt/WebContainer proof of concept.
- Lovable API/MCP adapter where account permissions allow.
- Provider capability router and cost ledger.

Exit criteria: at least one coding path exports a runnable project; adapter fallback tests pass.

## Phase 5 — QA and documentation
- Browser automation and API tests.
- Acceptance-criteria traceability.
- BRD, functional, and technical document generation.

Exit criteria: critical journeys pass; documents match canonical project spec.

## Phase 6 — GitHub and Cloudflare deployment
- GitHub App/OAuth installation and repo creation.
- Cloudflare API integration and deployment pipeline.
- Environment variables and secret management.
- Live URL smoke tests and rollback.

Exit criteria: user-authorized project deploys and verified URL is returned.

## Phase 7 — Production hardening
- Tenant isolation and security review.
- Usage metering, quotas, budgets, and billing.
- Observability, retries, rate limiting, abuse controls.
- Backups, retention, deletion, and support workflows.
