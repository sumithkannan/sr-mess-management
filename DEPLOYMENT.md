# Hosting SR Mess Management — Step by Step

Deploy to **two free services**:

| Piece | Service | URL |
|-------|---------|-----|
| Vue 3 SPA | **Vercel** (free) | `https://sr-mess.vercel.app` |
| FastAPI + SQLite | **PythonAnywhere** (free Beginner) | `https://YOURUSERNAME.pythonanywhere.com` |

```
Browser ──HTTPS──> Vercel (static Vue SPA)
                        │
                        │ XHR  https://YOURUSERNAME.pythonanywhere.com/api/...
                        ▼
                 PythonAnywhere (FastAPI ──> backend/mess.db)
```

**Do Part A before Part C** — the API's CORS allowlist needs your Vercel domain.

---

## Before you start

- Repo pushed to GitHub: `https://github.com/sumithkannan/sr-mess-management`
  (default branch `master`)
- Free [Vercel](https://vercel.com/signup) account
- Free [PythonAnywhere](https://www.pythonanywhere.com/registration/register/beginner/)
  Beginner account — **no credit card required**
- Node 18+ locally (optional, only for testing a production build)

### Why two services

- **`dist/` is never committed to git.** Vercel builds the frontend from source
  on every push, so the repo stays clean.
- **PythonAnywhere stays tiny.** It runs only the Python API — no
  `node_modules`, no 512 MB disk pressure, no CPU spent on `npm install`.
  PythonAnywhere's own docs warn that installing Vue can exceed free-tier limits.
- **Free custom domain.** Vercel provides HTTPS + custom domains free;
  PythonAnywhere does not offer custom domains at all.

---

# Part A — Frontend on Vercel

**A1.** Sign up at https://vercel.com/signup

**A2.** Go to https://vercel.com/new → import `sumithkannan/sr-mess-management`

**A3.** On the **Configure** screen, set:

- **Framework Preset:** Vite
- **Root Directory:** `frontend`  ← **most important step**

> ⚠️ Get this wrong and the build fails with "no build script". The repo-root
> `package.json` only has a `dev` script.

**A4.** Expand **Environment Variables**, add:

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://YOURUSERNAME.pythonanywhere.com` |

Use a placeholder for now if you have not made the PythonAnywhere account yet —
Part D shows you how to update it.

**A5.** Click **Deploy**

**A6.** Note your URL, e.g. `https://sr-mess.vercel.app`

The page will load but login will fail until Part C is done. That is expected.

> `frontend/.env.production` contains an empty `VITE_API_BASE_URL`. Vercel's
> environment variable takes priority over the file, so this is harmless and a
> local `npm run build` still produces relative URLs for same-origin testing.

> **No `vercel.json` is needed.** The router uses `createWebHashHistory()`, so
> URLs look like `/#/dashboard` and the server never needs an SPA rewrite.

---

# Part B — PythonAnywhere account

**B1.** Sign up:
https://www.pythonanywhere.com/registration/register/beginner/ — **no card required**

**B2.** Confirm your email, log in, open the **Dashboard**

**B3.** Go to **Account** page → **API token** → generate a token and copy it

> This token becomes your `SECRET_KEY`. There is no other way to set environment
> variables on PythonAnywhere's ASGI hosting.

---

# Part C — Backend on PythonAnywhere

**C1.** On the Dashboard, click **Bash** under "Start a new console"

**C2.** Install the CLI tool:

```bash
pip install --upgrade pythonanywhere
```

> A `typing-extensions` error during install is known and safe to ignore.

**C3.** Clone and set up Python:

```bash
git clone https://github.com/sumithkannan/sr-mess-management.git
cd sr-mess-management

mkvirtualenv messvenv --python=python3.10
pip install --upgrade pip
pip install -r backend/requirements.txt
```

**C4.** Create the secrets file:

```bash
nano backend/.env
```

Paste in, replacing both placeholders:

```ini
SECRET_KEY=PASTE_YOUR_API_TOKEN_HERE
CORS_ORIGINS=https://sr-mess.vercel.app
```

Save with `Ctrl+O` → `Enter` → `Ctrl+X`

> Use your real Vercel domain from A6, with `https://` and no trailing slash.
> Do not set `DATABASE_URL` — it defaults to `backend/mess.db` on persistent disk.

**C5.** Create the site (replace `YOURUSERNAME`):

```bash
pa website create \
  --domain YOURUSERNAME.pythonanywhere.com \
  --command '/home/YOURUSERNAME/.virtualenvs/messvenv/bin/uvicorn --app-dir /home/YOURUSERNAME/sr-mess-management/backend --uds ${DOMAIN_SOCKET} pythonanywhere_asgi:application'
```

You should see:

```
< All done! Your site is now live at YOURUSERNAME.pythonanywhere.com. >
```

> If you are on the **EU** system the domain is `YOURUSERNAME.eu.pythonanywhere.com`.
> A 404 for the first few seconds after creation is a known bug — refresh.

---

# Part D — Finish the Vercel env var

**D1.** Vercel → your project → **Settings** → **Environment Variables**

**D2.** Update `VITE_API_BASE_URL` to the real value:

```
https://YOURUSERNAME.pythonanywhere.com
```

**D3.** Redeploy — Vercel only reads environment variables at build time

---

# Part E — Verify

**E1.** API works:

```
https://YOURUSERNAME.pythonanywhere.com/api/health
```

Expect `{"status":"ok","app":"Mess Management System"}`

**E2.** Open your Vercel URL and log in:

- Username: `admin`
- Password: `PasswordToBeChanged`

**E3.** Change the password immediately (Users page)

---

# Deploying updates

## Frontend

Just push — Vercel rebuilds automatically:

```bash
git push origin master
```

## Backend

On PythonAnywhere:

```bash
source ~/.virtualenvs/messvenv/bin/activate
cd ~/sr-mess-management
git pull origin master
pip install -r backend/requirements.txt        # only if requirements.txt changed
pa website reload --domain YOURUSERNAME.pythonanywhere.com
```

> ⚠️ There is **no Reload button on the Web tab** — your site is invisible there
> because PythonAnywhere's FastAPI/ASGI support is beta. Always use
> `pa website reload`.

If you changed `backend/.env`, run `pa website reload` again.

If you added a new `VITE_*` variable, add it under Vercel → **Settings →
Environment Variables** and redeploy.

---

# Automated deploys (GitHub Actions)

`.github/workflows/deploy-backend.yml` pushes every `backend/**` change to
PythonAnywhere and reloads the site automatically.

## How it works

The free tier has **no SSH access** (paid-only), so the workflow cannot run
`git pull` on PythonAnywhere. Instead it uses the PythonAnywhere API:

1. Uploads the checked-out `backend/` directory via the **Files API**
   (`Files.tree_post`)
2. Reloads the ASGI site via the **Website API** (`Website.reload`)
3. Polls `/api/health` to confirm the deploy is actually serving

`backend/.env`, `backend/mess.db`, and `backend/venv/` are gitignored, so they
are never uploaded and live data is safe. A guard step fails the job if
`.env` or `venv/` is ever accidentally committed.

The frontend is deployed by **Vercel** directly from GitHub — no action needed.

## One-time setup

**1. Add the API token as a repository secret**

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Name | Value |
|------|-------|
| `PYTHONANYWHERE_API_TOKEN` | your token from the PythonAnywhere **Account** page |

**2. Add repository variables**

**Settings** → **Secrets and variables** → **Actions** → **Variables** tab

| Name | Value |
|------|-------|
| `PYTHONANYWHERE_USERNAME` | `sumithlals` |
| `PYTHONANYWHERE_SITE` | `www.pythonanywhere.com` — or `eu.pythonanywhere.com` if your account is on the EU system |

**3. Commit the workflow**

```bash
git add .github/workflows/deploy-backend.yml
git commit -m "Add GitHub Actions deploy for PythonAnywhere backend"
git push origin master
```

Check **Actions** in the repo for the run. It should end with
`::notice::Deployment healthy`.

You can also trigger it manually from the Actions tab → **Run workflow**.

## ⚠️ What the workflow does NOT do

**It cannot install new Python dependencies.** PythonAnywhere has no API for
running commands, so if you change `backend/requirements.txt` you must install
manually:

```bash
source ~/.virtualenvs/messvenv/bin/activate
pip install -r ~/sr-mess-management/backend/requirements.txt
```

**It does not deploy the frontend.** Vercel handles that from GitHub.

**It cannot edit `.env`.** Edit it in the console and run `pa website reload`.

## Watch your CPU allowance

The free tier allows only **100 CPU-seconds per day**. Every reload costs a few
seconds. Dozens of deploys in a day can exhaust it, at which point the site
stops responding until the allowance resets.

---

# Two things to know

**1. Your site never appears on PythonAnywhere's Web tab.** No Reload button, no
environment-variable UI, no error-log link. Logs live only in `/var/log`:

```bash
tail -f /var/log/YOURUSERNAME.pythonanywhere.com.error.log
```

**2. CORS errors are the #1 failure mode.** If login shows "Network Error", open
the browser console — the message names the blocked origin. Fix `CORS_ORIGINS` in
`backend/.env`, then `pa website reload`.

---

# Reference

## PythonAnywhere ASGI hosting (beta) — what to expect

| Topic | Reality |
|-------|---------|
| Site creation | **Only** via the `pa website` CLI — there is no "ASGI application file" field on the Web tab |
| Web tab | Your site does **not** appear there. No Reload button, no env-var UI |
| Reloading | `pa website reload --domain ...` |
| Static files | Not supported — irrelevant here, Vercel serves the frontend |
| Long-term pricing | Not finalized. PythonAnywhere state they are "99.9% certain" a free plan will exist |

Free tier limits: 1 web app, 512 MB disk, 2 consoles, no custom domain.

## Logs

The API site's logs are in `/var/log`, reachable from the **Files** page, a
console, or `tail`:

```bash
tail -f /var/log/YOURUSERNAME.pythonanywhere.com.error.log    # startup + tracebacks
tail -f /var/log/YOURUSERNAME.pythonanywhere.com.server.log    # requests, 404s
tail -f /var/log/YOURUSERNAME.pythonanywhere.com.access.log    # hit counts
```

A healthy startup looks like:

```
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on unix socket /var/sockets/YOURUSERNAME.pythonanywhere.com/app.sock
```

Frontend logs are in the Vercel dashboard → your project → **Deployments** →
**Logs**.

## Database backups

SQLite persists at `~/sr-mess-management/backend/mess.db` and survives reloads.

```bash
cp ~/sr-mess-management/backend/mess.db ~/mess-backup-$(date +%Y%m%d).db
```

To automate, use the **Tasks** tab (free accounts get one scheduled task):

```bash
cp /home/YOURUSERNAME/sr-mess-management/backend/mess.db /home/YOURUSERNAME/backups/mess-$(date +\%Y\%m\%d).db
```

## Custom domain

Point your domain at **Vercel**, not PythonAnywhere:

1. Vercel → your project → **Settings → Domains** → add `mess.yourdomain.com`
2. Vercel shows the DNS records; add them at your domain registrar
3. Vercel issues HTTPS automatically and renews it on its own

Then add the custom domain to `CORS_ORIGINS` in `backend/.env` and reload:

```ini
CORS_ORIGINS=https://mess.yourdomain.com,https://sr-mess.vercel.app
```

---

# Troubleshooting

### "Network Error" in the browser console

Almost always CORS. Check in order:

1. `backend/.env` has `CORS_ORIGINS=https://<your-vercel-domain>` — exact match,
   with `https://` and no trailing slash
2. You ran `pa website reload` after editing `.env`
3. You set `VITE_API_BASE_URL` in Vercel and **redeployed** (Vercel reads env
   vars at build time only)

The error reads like
`blocked by CORS policy: No 'Access-Control-Allow-Origin' header`.

### Vercel build fails with "No build script" / missing output

**Root Directory** is not set to `frontend`. Vercel → **Settings → General** →
Root Directory → `frontend` → redeploy.

### Requests still go to `localhost:8000`

`VITE_API_BASE_URL` is empty or missing at build time. Confirm it exists in
Vercel's Environment Variables, then redeploy.

### 502 Bad Gateway

```bash
pa website reload --domain YOURUSERNAME.pythonanywhere.com
```

Then read the error log.

### Site shows PythonAnywhere's "Coming Soon!" page

The ASGI site was never created or was deleted:

```bash
pa website get          # list sites
```

Re-run step C5.

### "No module named 'app'"

The `--app-dir` path is wrong. Inspect the site, then recreate it:

```bash
pa website get --domain YOURUSERNAME.pythonanywhere.com
pa website delete --domain YOURUSERNAME.pythonanywhere.com
# fix the path, then re-run step C5
```

### Vercel preview deployments get CORS errors

Preview URLs look like `https://<hash>-sr-mess.vercel.app` — a different origin.
Either add each one to `CORS_ORIGINS` in `backend/.env`, or disable preview
deployments (Vercel → **Settings → Git** → uncheck automatic deployments for
previews). Production URL only is fine for normal use.

### Running out of disk (512 MB free limit)

```bash
du -sh ~/sr-mess-management/* ~/.cache/pip 2>/dev/null
rm -rf ~/.cache/pip
```

---

# File changes made for deployment

| File | Change | Why |
|------|--------|-----|
| `backend/app/config.py` | Added `BASE_DIR`; `DATABASE_URL` and `.env` resolved by absolute path | Under `pa` the working directory is not guaranteed, so a relative `sqlite:///./mess.db` or `env_file=".env"` could silently miss. A missed `.env` means `SECRET_KEY` falls back to an insecure hardcoded default |
| `backend/pythonanywhere_asgi.py` | ASGI entry point exposing `application` | Target of the `pa website create --command` |
| `backend/requirements.txt` | Removed `psycopg2-binary` | SQLite only |
| `frontend/src/api/index.js` | `baseURL` from `VITE_API_BASE_URL` | Empty in dev (Vite proxy), absolute in production |
| `frontend/vite.config.js` | Dev-only `/api` → `localhost:8000` proxy | Local development |
| `frontend/.env.production` | `VITE_API_BASE_URL=` (empty) | Vercel's env var takes priority; local prod build stays same-origin |

`frontend/dist/` is **not** committed — Vercel builds it.