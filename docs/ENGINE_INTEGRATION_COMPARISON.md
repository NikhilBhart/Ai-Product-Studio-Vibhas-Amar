# Coding and design engine comparison

## Decision summary
Use a provider-neutral adapter architecture. Do not treat Bolt, Lovable, and Figma as interchangeable APIs: they solve different parts of the workflow and expose different levels of automation.

| Option | What it is useful for | Automation surface | Main caveat | Recommendation |
|---|---|---|---|---|
| Bolt / StackBlitz WebContainers | Browser-based Node.js development and preview; Bolt ecosystem experiments | WebContainer API can run Node.js projects in-browser; Bolt integrations/OSS components may be evaluated | WebContainer is a runtime, not by itself a complete hosted app-generation API; licensing and commercial use must be reviewed | Prototype adapter first; do not assume it replaces the whole coding agent |
| Lovable | AI app builder and project workflow | Lovable API can manage connected workspace/projects; MCP can enable AI clients to build/edit projects; Build-with-URL can prefill a prompt | API key creation and workspace permissions are plan-dependent; project generation via MCP is distinct from workspace-management REST API | Optional adapter when customer has eligible Lovable workspace; validate current API/MCP contract |
| Figma | Editable UI/UX artifacts | Plugin API can create and modify nodes in the currently open design file; REST API reads files and has limited write operations | Plugin needs to run in Figma with user authorization; REST API is largely read-only for design content | Use a first-party Figma plugin to import generated design spec |
| Direct code-generation LLM | Custom code generation under our orchestration and sandbox | Model API + our own tools, repository operations, terminal and browser test harness | We own reliability, context management, patching, execution sandbox, and evaluation | Core fallback and long-term control path |

## Recommended adapter contracts

### CodingEngine
- `capabilities()` — report supported features: prompt-to-project, edit-existing-project, file export, preview, deploy, streaming.
- `create_project(spec, workspace)` — create initial project where supported.
- `apply_changes(task, workspace)` — modify project.
- `export_source(workspace)` — return source artifact or repository reference.
- `get_status(job_id)` — return provider job status.

### DesignEngine
- `generate_design_spec(product_spec)` — create canonical design JSON.
- `export_figma_plugin_payload(design_spec)` — prepare payload for plugin import.
- `get_export_status(job_id)` — track import/export.

## Selection strategy
1. Check provider connection and account permissions.
2. Check required capability against project needs.
3. Estimate provider cost and execution time.
4. Choose the lowest-cost provider that meets quality and capability thresholds.
5. Fall back to direct LLM code generation if a provider is unavailable, subject to sandbox limits.
6. Record provider, model, version, token usage, duration, and outcome for every run.

## Integration status at scaffold time
- Direct LLM adapter: interface planned; implementation pending.
- Bolt/WebContainer: research/prototype required.
- Lovable API/MCP: optional integration; credentials and eligible workspace required.
- Figma plugin: starter manifest and import scaffold planned; user must run plugin in Figma.

## Official references to re-check during implementation
- Lovable API and MCP documentation: https://docs.lovable.dev/
- Lovable API connector overview: https://docs.lovable.dev/integrations/lovable-api-connector
- StackBlitz WebContainers: https://webcontainers.io/
- Figma Plugin API: https://developers.figma.com/docs/plugins/api/api-reference/
- Figma API comparison: https://developers.figma.com/compare-apis/
