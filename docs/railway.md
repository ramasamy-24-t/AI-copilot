# Deploy to Railway

Live project (this workspace): **ai-copilot** → public UI  
https://web-production-5786df.up.railway.app

On the free plan, **worker runs inside the api container** (`backend/start_railway.py`) so document storage stays on one volume. Services: **MySQL**, **Qdrant**, **api** (+worker), **web**.

Railway does not run Compose as one unit; each Compose service becomes a Railway service in one project ([Docker Compose guide](https://docs.railway.com/guides/docker-compose)).

## Recommended: import Compose in the Railway UI

1. Push this repo to GitHub (or use [ramasamy-24-t/AI-copilot](https://github.com/ramasamy-24-t/AI-copilot)).
2. Open [railway.app](https://railway.app) → **New Project**.
3. Drag `compose.yaml` onto the project canvas (Compose import), **or** create five services manually as below.
4. Connect the GitHub repo to **api**, **worker**, and **web** so they build from Dockerfiles.
5. Add volumes:
   - MySQL data
   - Qdrant storage
   - API/worker shared volume at `/data/storage`
6. Set variables (below), generate a public domain on **web** only.
7. Deploy, then create a user:

```bash
railway run -s api -- python -m app.cli create-user --email YOU@example.com --name "Your Name"
```

## Manual service map

| Service | Source | Start / notes |
|---------|--------|----------------|
| mysql | Image `mysql:8.4.11` | Volume on `/var/lib/mysql`. Set `MYSQL_*` |
| qdrant | Image `qdrant/qdrant:v1.19.1` | Volume on `/qdrant/storage`. Set `QDRANT__SERVICE__API_KEY` |
| api | Root Dockerfile `backend/Dockerfile` | Port **8000**. Private only |
| worker | Same image as api | Custom start: `python -m app.worker` |
| web | Root Dockerfile `frontend/Dockerfile` | Public HTTPS. Set `API_UPSTREAM` |

Private DNS uses `http://SERVICE.railway.internal:PORT` ([private networking](https://docs.railway.com/private-networking)).

## Variables

### Shared / api + worker

Copy from your local `.env` (never commit it):

- `SARVAM_API_KEY`, `LAYA_API_KEY`, `LAYA_BASE_URL`, `LAYA_MODEL`
- `GEMINI_API_KEY`, `GEMINI_BASE_URL`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`
- `QDRANT_API_KEY` (same value as Qdrant’s `QDRANT__SERVICE__API_KEY`)
- `STORAGE_DIR=/data/storage`
- `SARVAM_BASE_URL=https://api.sarvam.ai`
- `SUMMARY_MODEL=sarvam-105b`
- `ENVIRONMENT=production`
- `COOKIE_SECURE=true`
- `CORS_ORIGINS=https://YOUR-WEB-DOMAIN.up.railway.app` (exact public web URL)
- `DATABASE_URL=mysql+pymysql://health:PASSWORD@mysql.railway.internal:3306/health_copilot`  
  (or Railway MySQL plugin URL if you use the plugin instead of the MySQL image)
- `QDRANT_URL=http://qdrant.railway.internal:6333`

### web

- `PORT` — Railway injects this; keep the Dockerfile default/`PORT` from Railway
- `API_UPSTREAM=api.railway.internal:8000`

### mysql (image)

- `MYSQL_DATABASE=health_copilot`
- `MYSQL_USER=health`
- `MYSQL_PASSWORD=...` (must match `DATABASE_URL`)
- `MYSQL_ROOT_PASSWORD=...`

## After deploy

1. Open the **web** public URL.
2. Create an account (12+ character password) or use the CLI above.
3. In **Profile & consent**, enable external AI processing before OCR/summary/assistant features.
4. Confirm `/health` on the api service (private or temporary public) returns OK.

## CLI alternative

```powershell
npm install -g @railway/cli
railway login
railway init
# then link / create services, or import compose in the UI
railway up
```

Do **not** paste production secrets into the repo. Set them in the Railway Variables UI.
