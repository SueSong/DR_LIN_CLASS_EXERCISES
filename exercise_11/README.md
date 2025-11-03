# Exercise 11: Child Growth Assistant (Week 8)

This exercise bootstraps a Child Growth/Parenting Coach assistant as an evolution of Exercise 10. It includes:

- **Backend (FastAPI)**: Health endpoints, coach WebSocket chat for parenting advice
- **Frontend (Next.js)**: Beautiful, production-quality UI with parent sign-in and real-time chat

## 🚀 Quick Start

**Easiest way to get started:**

```bash
# Mac/Linux
./start.sh

# Windows
start.bat
```

This will automatically start both servers and open the app at http://localhost:3082

**For detailed instructions, troubleshooting, and manual setup**, see [QUICKSTART.md](./QUICKSTART.md)

## 🌐 URLs

Once running:
- **Frontend App**: http://localhost:3082
- **Backend API**: http://localhost:8011
- **API Docs**: http://localhost:8011/docs
- **Health Check**: http://localhost:8011/healthz

## 🏗️ Architecture

### Backend (Port 8011)
- FastAPI with WebSocket support
- Health endpoints: `/healthz` and `/readyz`
- Coach WebSocket: `ws://localhost:8011/ws/coach/{session_id}`
- Auto-reload enabled for development

### Frontend (Port 3082)
- Next.js 14 with App Router
- Tailwind CSS with custom animations
- Real-time WebSocket chat
- Responsive, accessible design

## Student Tasks (Week 8)

Complete the following to harden the MVP and prepare an internal alpha launch. Each item has a concrete deliverable and pass/fail criteria.

1) Safety & scope policy
- Deliverables: `docs/safety_scope.md`, `config/safety_policy.json`, backend guard hook with refusal templates.
- Pass: 20 red-team prompts trigger correct refusal/redirect (unit tests).

2) Curated RAG pack (citations required)
- Deliverables: `rag/ingest.py`, `rag/index.json`, retrieval helper, citation badges/links in UI.
- Pass: In 10 sampled sessions, ≥90% responses include ≥1 citation.

3) SSE advice streaming
- Deliverables: backend SSE endpoint that streams advice chunks; frontend consumer in `/coach/chat`.
- Pass: First token <1.5s; streaming updates visible.

4) Playwright e2e suite
- Deliverables: expand `frontend/e2e/assistant.spec.ts` to ≥10 scenarios (screen time, bedtime, sibling conflict, motivation, ADHD-like guidance → safe referral, etc.).
- Pass: All scenarios green; asserts response structure (empathy, 3 steps, citation, safety footer).

5) Dockerize & health checks
- Deliverables: `Dockerfile`(API), `Dockerfile.web`(Next), `docker-compose.yml`, `/readyz` checks RAG + model key.
- Pass: `docker compose up` → both services healthy ≤20s.

6) CI/CD pipelines
- Deliverables: `.github/workflows/ci.yml` (lint/type, unit, e2e, build), `.github/workflows/cd.yml` (staging smoke deploy).
- Pass: Red blocks merge; green tag auto-deploys to staging.

7) SLOs & observability
- Deliverables: `observability/` with OpenTelemetry spans (retrieval, model, guard), dashboards (JSON exports).
- Pass: 15‑min load test p95 ≤ 2.5s; failure rate ≤ 1%.

8) Guardrails + HITL queue
- Deliverables: `backend/app/guardrails.py` (PII/crisis/medical classifier) ↔ HITL UI `web/app/(hitl)/queue.tsx`.
- Pass: Crisis prompts route to HITL in <500ms; mentor reply appears in parent chat.

9) Prompt versioning & snapshots
- Deliverables: `prompts/child_coach_vX.json`, `tests/snapshots/*`, prompt changelog.
- Pass: Changing prompts without version bump fails CI.

10) Token/cost watchdog
- Deliverables: `billing/ledger.py` (per‑turn tokens/cost), caps + "lite mode" fallback, nightly CSV + admin sparkline.
- Pass: Over‑budget requests return lite mode with notice; report generated daily.

11) Load testing
- Deliverables: Use scaffolds in `load/k6/coach_scenario.js` and `load/locust/locustfile.py`.
- Pass: Report includes throughput, p95, error rate; meets SLOs.

12) Accessibility & UX polish
- Deliverables: keyboard navigation, ARIA roles for chat, disclaimers.
- Pass: Axe scan has no critical issues.

## What to Submit

- 3–5 merged PRs covering: Safety+RAG, Docker+CI, E2E+SLOs.
- 2‑minute demo: refusal flow → normal advice with citations → HITL escalation.
- One‑pager: metrics (p95, fail rate, citation rate), cost/day, key risks, next‑week plan.

## 📖 Documentation Index

- **[WELCOME.md](./WELCOME.md)** - 👋 Start here! Introduction and overview
- **[QUICKSTART.md](./QUICKSTART.md)** - 🚀 Setup guide and troubleshooting
- **[SCRIPTS.md](./SCRIPTS.md)** - 🛠️ Scripts reference and commands
- **[PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md)** - 📁 Codebase layout and architecture
- **[load/README.md](./load/README.md)** - 🧪 Load testing guide (K6 & Locust)

## Tips

- Keep `.env` and secrets out of source control; use templates.
- Add feature flags for streaming vs non‑streaming and model choices.
- Prefer small, reviewable PRs; ensure CI is green before merging.
