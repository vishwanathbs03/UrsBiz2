# UrsBiz Environment Setup Guide

This document describes the environment configuration required to run the UrsBiz full-stack application.

## 🛠️ Architecture Overview
- **Frontend**: Next.js (App Router)
- **Backend**: Python/FastAPI
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **AI**: OpenAI-compatible API (Gemini 2.0 Flash default)

## 🔑 Backend Configuration (`backend/.env`)

### Required Variables
| Variable | Description | Secret? | Default / Example |
| :--- | :--- | :---: | :--- |
| `DATABASE_URL` | Connection string for the database | Yes | `sqlite:///./ursbiz.db` |
| `AI_API_KEY` | API key for the AI provider | Yes | `your_gemini_api_key_here` |
| `JWT_SECRET_KEY` | Secret for signing auth tokens | Yes | `generate_a_secure_secret_here` |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | No | `http://localhost:3000` |

### AI Provider Settings
The app supports multiple providers via `AI_PROVIDER`:
- `openai_compatible`: Uses `AI_BASE_URL` and `AI_API_KEY` (Default).
- `ollama`: Uses `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.
- `placeholder`: Deterministic rule-based responses (No key needed).

### Production Hardening
When `APP_ENV=production`, the following must be configured:
- `COOKIE_SECURE=true` (Requires HTTPS).
- `JWT_SECRET_KEY` must be a strong, randomly generated string.
- `CORS_ORIGINS` must not contain wildcards (`*`).
- `STRICT_TRANSPORT_SECURITY` should be set for HSTS.

---

## 🎨 Frontend Configuration (`frontend/.env.local`)

### Variables
| Variable | Description | Secret? | Default / Example |
| :--- | :--- | :---: | :--- |
| `NEXT_PUBLIC_APP_NAME` | Name of the application | No | `UrsBiz` |
| `NEXT_PUBLIC_APP_URL` | Base URL of the frontend | No | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Direct Backend URL (Optional) | No | `http://127.0.0.1:8001` |

**Note on `NEXT_PUBLIC_API_URL`**: In local development, this is typically left **unset**. The Next.js configuration uses a rewrite proxy to map `/api/v1/*` to the backend, which avoids CORS issues and ensures authentication cookies are handled as Same-Origin.

---

## 🚀 Deployment (Render)

### Backend Service
Ensure the following Environment Variables are set in the Render Dashboard:
- `DATABASE_URL` (Provided by Render PostgreSQL)
- `AI_API_KEY`
- `JWT_SECRET_KEY`
- `APP_ENV=production`
- `CORS_ORIGINS` (Set to your Render frontend URL)

### Frontend Service
Ensure the following Environment Variables are set in the Render Dashboard:
- `NEXT_PUBLIC_APP_URL` (Your Render frontend URL)

---

## 🔒 Security & Secrets Management

### Generating Secure Secrets
To generate a secure `JWT_SECRET_KEY`, run:
```bash
openssl rand -hex 32
```

### Critical Rules
1. **NEVER** commit `.env` or `.env.local` files to Git.
2. **NEVER** put secrets in `NEXT_PUBLIC_` variables (they are visible to the client).
3. **NEVER** use default "change-me" secrets in any production environment.

### Git Safety
The `.gitignore` is configured to block all `.env` files while allowing `.env.example` files to be tracked.
