# User flow and screen behavior

## Primary journey
1. Landing/dashboard: user selects **New project**.
2. Idea intake: user enters a plain-language product idea and optionally chooses a prototype profile.
3. Discovery: user sees progress while the Product Manager Agent prepares the product brief.
4. Product brief: user reviews target users, problems, outcomes, business value, assumptions, uncertainties, and scope.
5. Backlog: user browses epics, capabilities, features, user stories, and acceptance criteria.
6. Design: user previews journeys, screens, components, and design tokens; can export to Figma using the plugin.
7. Build: user sees coding provider, task progress, build logs, and preview.
8. QA: user sees test status, failures, fixes, and remaining limitations.
9. Documents: user opens business and technical deliverables.
10. Publish: user connects GitHub/Cloudflare and approves deployment.
11. Delivery: user receives the verified URL, repository link, design handoff, documents, and QA report.

## Screen inventory
| Screen | Main controls | Behavior |
|---|---|---|
| Dashboard | New project, project cards, filters | Create and resume projects |
| Idea intake | Idea textarea, create button | Submit one-sentence idea and create project |
| Project overview | Status timeline, artifacts | View current stage and outputs |
| Product brief | Edit, approve, regenerate | Review business definition and assumptions |
| Backlog | Epic tree, story detail | Inspect and edit hierarchy and acceptance criteria |
| Design studio | Screen list, preview, export to Figma | Inspect design spec and initiate plugin handoff |
| Build workspace | Preview, logs, provider selector | Review generated app and build progress |
| QA center | Test list, rerun, issue details | Inspect verification evidence |
| Documents | Open/export/download | Access BRD, PRD, functional and technical docs |
| Publish | Connect GitHub, connect Cloudflare, deploy | Authorize and publish a verified build |
| Settings | LLM provider, integrations, budgets | Configure credentials and project defaults |

## Interaction contract
Every interactive control must have: a named purpose, an enabled/disabled rule, an action, a visible loading state, success/failure feedback, and an accessibility label. Destructive actions require confirmation. Publishing requires explicit authorization.
