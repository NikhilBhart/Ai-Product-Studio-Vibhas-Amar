# Phase 2 — Local Setup, API Testing, and Troubleshooting

## 1. Configure demo mode

Start with no-cost demo mode:

```env
LLM_PROVIDER=mock
LLM_MODEL=demo-product-manager
```

This verifies the full API and persistence integration without an LLM key. The output is deterministic sample content.

## 2. Configure a real model

Use an OpenAI-compatible provider:

```env
LLM_PROVIDER=gemini-compatible
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=YOUR_KEY
```

Place these variables in the agent service environment. Never put the key in Next.js `NEXT_PUBLIC_*` variables or source control.

## 3. Test the agent directly

```bash
curl -X POST http://localhost:8001/v1/discovery/run \
  -H "Content-Type: application/json" \
  -d '{"idea":"Build a social photo sharing platform for creators"}'
```

Expected: JSON containing `product_brief`, `provider`, `model`, and `warnings`.

## 4. Test through Spring Boot

```bash
curl -X POST http://localhost:8080/api/projects \
  -H "Content-Type: application/json" \
  -d '{"idea":"Build a social photo sharing platform for creators"}'
```

Expected: HTTP 201, project ID, `PRD_READY`, agent run ID, and discovery result.

Then:

```bash
curl http://localhost:8080/api/projects
curl http://localhost:8080/api/projects/PROJECT_UUID
```

## 5. Verify PostgreSQL persistence

```sql
SELECT id, name, status, canonical_spec IS NOT NULL AS has_brief
FROM projects ORDER BY created_at DESC;

SELECT graph_name, status, current_node, started_at, completed_at
FROM agent_runs ORDER BY created_at DESC;

SELECT artifact_type, title, version, created_at
FROM artifacts ORDER BY created_at DESC;
```

## 6. Common issues

- **Agent connection refused:** confirm Uvicorn is listening on port 8001 and `AGENT_SERVICE_URL` is correct.
- **Database connection refused:** confirm the pgvector container is healthy and credentials/port match the environment. The default host port is `5433`, mapped to container port `5432`.
- **Missing table:** the schema init script only runs for a fresh PostgreSQL data volume. Apply the schema manually for an existing volume.
- **HTTP 424 from agent:** provider configuration is incomplete; check `LLM_PROVIDER`, `LLM_MODEL`, and `LLM_API_KEY`.
- **HTTP 502 from agent:** upstream provider call failed or returned invalid structured output. Inspect agent logs; do not paste secrets into logs or support requests.
- **Browser CORS error:** the development API permits `http://localhost:3000`; update the allowlist deliberately for another local origin.
- **Brief warning says DEMO_MODE:** expected until a real provider is configured.

## Security reminder
This is a development MVP. Do not expose the services publicly or connect customer data until authentication, tenant isolation, rate limiting, secret management, sandboxing, and audit controls are implemented.
