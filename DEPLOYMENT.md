# Deployment Guide — SR Mess Management

## Platform: PythonAnywhere (Free Tier)
### No credit card required

---

## Before You Start

1. Create a **GitHub** account: https://github.com/signup
2. Create a **PythonAnywhere** account: https://www.pythonanywhere.com/registration/register/beginner/
   - Choose the **Free** plan (no card needed)
   - Your URL will be: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Step 1: Push Code to GitHub

Open a terminal in the project root folder on your computer:

```bash
git init
git add .
git commit -m "Initial commit"
```

Go to https://github.com/new → create a repo named `sr-mess` (do NOT add README/.gitignore/license).

```bash
git remote add origin https://github.com/YOUR_USERNAME/sr-mess.git
git push -u origin main
```

---

## Step 2: Clone the Repo on PythonAnywhere

1. Log in to https://www.pythonanywhere.com
2. Go to **Dashboard** → Open a **Bash** console (click "Bash" under "Start a new console")
3. In the console, run:

```bash
git clone https://github.com/YOUR_USERNAME/sr-mess.git
cd sr-mess
```

---

## Step 3: Create a Virtual Environment

```bash
cd ~/sr-mess/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, SQLAlchemy, etc. Takes ~2 minutes.

---

## Step 4: Build the Frontend

```bash
cd ~/sr-mess/frontend
npm install
npm run build
```

If `npm` is not found, run first: `nvm install 22 && nvm use 22` then retry.

After this, the built frontend files will be in `~/sr-mess/frontend/dist/`.

---

## Step 5: Set Up the Web App

1. Go to **PythonAnywhere Dashboard** → **Web** tab
2. Click **Add a new web app**
3. Click **Next** (accept default domain)
4. Choose **Manual configuration** (NOT "FastAPI" — manual gives control)
5. Choose **Python 3.11** → click Next
6. Wait for the web app to be created

Now configure it:

### 5a. Set the source code path
- **Code** section → **Working directory**: `/home/YOUR_USERNAME/sr-mess/backend`

### 5b. Set the virtualenv
- **Virtualenv** section → Enter: `/home/YOUR_USERNAME/sr-mess/backend/venv`
- Click **Set**

### 5c. Configure the ASGI app
- **Code** section → Find **ASGI application file**
- Set it to: `/home/YOUR_USERNAME/sr-mess/backend/pythonanywhere_asgi.py`
- Click the pencil icon to edit → Write this content:

```python
import sys
import os

path = '/home/YOUR_USERNAME/sr-mess/backend'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('CORS_ORIGINS', '')

# DATABASE_URL stays at default sqlite:///./mess.db
# The mess.db file will be created in the backend/ directory

from app.main import app
application = app
```

Replace `YOUR_USERNAME` with your actual PythonAnywhere username. Click **Save**.

### 5d. Set environment variables
- **Environment variables** section → click **Add environment variable**:
  - **Variable name:** `SECRET_KEY`
  - **Value:** Generate one: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` (run this in a Bash console and paste the output)

  - **Variable name:** `CORS_ORIGINS`
  - **Value:** `https://YOUR_USERNAME.pythonanywhere.com`
  
  - **Variable name:** `PYTHONANYWHERE_DOMAIN`
  - **Value:** `YOUR_USERNAME.pythonanywhere.com`

### 5e. Set static files for the frontend
- **Static Files** section → Add these entries:

| URL | Directory |
|-----|-----------|
| `/assets` | `/home/YOUR_USERNAME/sr-mess/frontend/dist/assets` |
| `/favicon.ico` | `/home/YOUR_USERNAME/sr-mess/frontend/dist/favicon.ico` |

**Important:** Make sure the `/assets` entry is at the TOP of the list. Use the drag handle to reorder if needed.

### 5f. Reload
- Click the green **Reload** button at the top of the page

---

## Step 6: Verify the Backend

Visit: `https://YOUR_USERNAME.pythonanywhere.com/api/health`

You should see: `{"status":"ok","app":"Mess Management System"}`

If not, check the **Error log** link on the Web tab to debug.

---

## Step 7: Verify the Frontend

Visit: `https://YOUR_USERNAME.pythonanywhere.com`

You should see the login page of the Mess Management app.

If it doesn't load the API data, open **Browser DevTools** → **Console** tab to see error messages.

---

## Step 8: Admin Account (Auto-Created)

The app auto-creates an admin account on first startup. Default credentials are defined in `backend/app/services/auth_service.py` — check that file for the email and password. Typically:

- **Email:** `admin@example.com`
- **Password:** `admin123`

If the database file already exists (from local dev), the admin is already there. You can log in directly.

---

## Step 9: Custom Domain (Optional, Paid)

PythonAnywhere free tier does NOT support custom domains. To use a custom domain like `mess.collegename.ac.in`:

1. Upgrade to a **Hacker** plan ($5/month) or higher
2. **Web** tab → **Add a custom domain**
3. Follow PythonAnywhere's DNS instructions to add a CNAME record with your domain provider

---

## Maintenance

### Updating after code changes

```bash
# In PythonAnywhere Bash console:
cd ~/sr-mess
git pull

# Rebuild frontend if frontend code changed:
cd frontend
npm install
npm run build
cd ..

# Reinstall backend deps if requirements.txt changed:
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Then go to Web tab → click Reload
```

### Viewing logs
- **Web** tab → **Error log** — most important, check this first for 500 errors
- **Web** tab → **Server log** — shows all requests, useful for debugging 404s
- Inside the app, you can also run: `cat /var/log/YOUR_USERNAME.pythonanywhere.com.error.log`

### Resetting the database
```bash
cd ~/sr-mess/backend
rm mess.db
source venv/bin/activate
python -c "from app.main import app; from app.database import Base, engine; Base.metadata.create_all(bind=engine); from app.services.auth_service import seed_admin; seed_admin()"
```

Then **Reload** the web app.

### Database backup
The database file is at: `~/sr-mess/backend/mess.db`
Copy it to back up:
```bash
cp ~/sr-mess/backend/mess.db ~/mess_backup_$(date +%Y%m%d).db
```

---

## Troubleshooting

### 502 Bad Gateway
- Go to **Web** tab → **Reload**
- Check **Error log**

### Module not found errors
- Make sure **Virtualenv** path is correct and all deps are installed:
  ```bash
  cd ~/sr-mess/backend
  source venv/bin/activate
  pip list
  pip install -r requirements.txt
  ```

### "No module named 'app'"
- Your **Working directory** must be `/home/YOUR_USERNAME/sr-mess/backend`
- The ASGI file must start with the sys.path.append line shown above

### Frontend shows blank page
- Check **Server log** for 404 errors on `.js`/`.css` files
- Make sure **Static Files** entries are correct in the Web tab
- Rebuild the frontend: `cd ~/sr-mess/frontend && npm install && npm run build`
- Check **Browser DevTools** → **Console** tab (F12)

### Login says "Network Error"
- Open **Browser DevTools** → **Network** tab → Log in again
- Check what URL the API call goes to
- It should be `https://YOUR_USERNAME.pythonanywhere.com/api/auth/login`
- If it's still `http://localhost:8000`, rebuild the frontend (the `.env.production` might not have been picked up)

---

## File Changes Made for Deployment (Summary)

| File | What Changed |
|------|-------------|
| `backend/requirements.txt` | Removed psycopg2-binary (SQLite only for PA) |
| `backend/app/main.py` | Added catch-all route to serve frontend for SPA routing |
| `backend/pythonanywhere_asgi.py` | **NEW** — ASGI entry point for PythonAnywhere |
| `frontend/vite.config.js` | Added dev proxy for `/api` → `localhost:8000` |
| `frontend/src/api/index.js` | Uses relative URLs by default (same origin in prod) |
| `frontend/.env.production` | Empty VITE_API_BASE_URL (uses same origin) |
