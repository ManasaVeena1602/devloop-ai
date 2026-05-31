# DevLoop

> AI-powered production incident resolution agent that automatically diagnoses, fixes, tests, and creates pull requests for production bugs.

**Live Demo:** https://devloop-frontend.vercel.app
**Backend API:** https://devloop-qtn8.onrender.com

---

## Overview

DevLoop automates the production incident resolution workflow.

When an error occurs in production, DevLoop:

1. Receives alerts from Sentry
2. Fetches the affected code from GitHub
3. Runs a two-LLM diagnosis and fix pipeline
4. Tests the patch in an isolated Docker environment
5. Creates a GitHub Pull Request
6. Notifies the team through Slack

This reduces manual debugging effort and accelerates incident response.

---

## Architecture

```text
Sentry Webhook ──► POST /webhook/sentry
Manual Trigger ─► POST /trigger
Demo Trigger ───► POST /trigger/demo
                      │
                 orchestrator.py
                 ├── github_client.py
                 ├── codex_client.py
                 ├── sandbox_runner.py
                 └── slack_notify.py
                      │
                      ▼
      Diagnose → Fix → Test → PR → Notify
```

---

## Features

### AI Incident Resolution

* Automated bug diagnosis using LLMs
* Automated code fix generation
* Multi-model fallback architecture
* Retry handling for rate limits
* Production-ready orchestration pipeline

### GitHub Integration

* GitHub OAuth authentication
* Repository management
* Automatic branch creation
* Commit generation
* Pull request creation

### Slack Integration

* Slack OAuth support
* Automatic incident notifications
* PR update notifications

### Dashboard

* Live log streaming via SSE
* Run history tracking
* Repository management
* OAuth account management
* Dark and light themes

### Sandbox Testing

* Docker-based isolated execution
* Automated validation before PR creation
* Test result reporting

### Demo Mode

* One-click execution against demo repository
* No production setup required

---

## Two-LLM Pipeline

### Analyzer

A lightweight model that receives:

* Error message
* Stack trace

Outputs:

```json
{
  "root_cause": "...",
  "buggy_line": "...",
  "fix_strategy": "...",
  "scope": "..."
}
```

### Fixer

A code-focused model that receives:

* Source file
* Analyzer output

Outputs:

```json
{
  "fixed_code": "...",
  "fix_summary": "..."
}
```

Both stages support multiple OpenRouter models with automatic failover.

---

# Tech Stack

| Layer          | Technology                           |
| -------------- | ------------------------------------ |
| Frontend       | Next.js 15, TypeScript, Tailwind CSS |
| Backend        | FastAPI, Python 3.11+                |
| LLM            | OpenRouter                           |
| Authentication | GitHub OAuth, Slack OAuth            |
| Database       | Supabase PostgreSQL                  |
| Realtime Logs  | Server-Sent Events (SSE)             |
| Git Operations | PyGithub                             |
| Sandbox        | Docker                               |
| Deployment     | Vercel, Render                       |

---

# Frontend

## Pages

| Route        | Description                |
| ------------ | -------------------------- |
| `/`          | Landing page               |
| `/dashboard` | Main application dashboard |

### Dashboard Features

* Live log stream
* Run history
* Repository management
* GitHub OAuth connection
* Slack OAuth connection
* Theme toggle
* Demo execution

---

## Frontend Environment

Create:

```bash
dashboard/.env.local
```

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

Production:

```env
NEXT_PUBLIC_BACKEND_URL=https://devloop-qtn8.onrender.com
```

---

## Frontend Setup

```bash
cd dashboard

npm install

npm run dev
```

Runs at:

```text
http://localhost:3000
```

---

# Backend

## Requirements

* Python 3.11+
* Docker

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Backend Environment

Copy:

```bash
cp .env.example .env
```

Configure:

```env
OPENROUTER_API_KEY=
OPENROUTER_API_KEY_2=

GITHUB_TOKEN=

GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=

SUPABASE_URL=
SUPABASE_SERVICE_KEY=

JWT_SECRET=

FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

SENTRY_WEBHOOK_SECRET=
```

---

## Database Setup

Run in Supabase SQL Editor:

```sql
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  github_id text unique not null,
  github_login text,
  github_token text,
  slack_webhook_url text,
  created_at timestamptz default now()
);

create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  error_message text,
  filename text,
  environment text,
  status text default 'running',
  pr_url text,
  branch text,
  test_passed boolean,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists log_lines (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references runs(id) on delete cascade,
  user_id uuid references users(id) on delete cascade,
  level text,
  message text,
  created_at timestamptz default now()
);

create table if not exists user_repos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  repo text not null,
  base_branch text default 'main',
  sentry_secret text,
  created_at timestamptz default now(),
  unique(user_id, repo)
);

create index if not exists idx_user_repos_user_id
on user_repos(user_id);
```

---

## Run Backend

```bash
python -m uvicorn main:app \
--host 0.0.0.0 \
--port 8000 \
--reload
```

API:

```text
http://localhost:8000
```

Optional for webhook testing:

```bash
ngrok http 8000
```

---

# Connecting Sentry

1. Open Sentry Project Settings
2. Navigate to Integrations → Webhooks
3. Add:

```text
https://devloop-qtn8.onrender.com/webhook/sentry
```

4. Enable Issue Events
5. Copy signing secret
6. Configure:

```env
SENTRY_WEBHOOK_SECRET=<secret>
```

---

# Demo Repository

Use the dashboard's **Try Demo Repo** button.

Demo target:

```text
rishikesh183/devloop-demo-app
```

A maintained bug is intentionally kept in the repository for demonstrations.

---

# Deployment

## Backend (Render)

Start Command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Configure all environment variables in Render.

---

## Frontend (Vercel)

Settings:

```text
Root Directory: dashboard
```

Environment Variable:

```env
NEXT_PUBLIC_BACKEND_URL=https://devloop-qtn8.onrender.com
```

No custom build command required.

---

# OAuth Callback URLs

## GitHub

```text
https://devloop-qtn8.onrender.com/auth/github/callback
```

## Slack

```text
https://devloop-qtn8.onrender.com/auth/slack/callback
```

---

# Project Structure

```text
DevLoop
│
├── main.py
│
├── agent
│   ├── orchestrator.py
│   ├── codex_client.py
│   ├── github_client.py
│   ├── sandbox_runner.py
│   └── slack_notify.py
│
├── db
│   ├── client.py
│   ├── users.py
│   ├── runs.py
│   └── repos.py
│
├── dashboard
│   ├── app/page.tsx
│   ├── app/dashboard/page.tsx
│   └── ...
│
└── mock_sentry_payload.json
```

---

# Future Enhancements

* Multi-file patch generation
* Automated rollback support
* Kubernetes deployment testing
* Jira integration
* Incident analytics dashboard
* Self-healing deployment workflows

---



---

Built with ❤️ using FastAPI, Next.js, OpenRouter, Supabase, GitHub, Slack, and Docker.
