# Deployment Guide — SR Mess Management

## Platform: Render.com (Free Tier)

---

## Before You Start

Create accounts:
- [GitHub](https://github.com) account
- [Render](https://render.com) account (sign up with GitHub)

---

## Step 1: Push Code to GitHub

Run in the project root:

```bash
git init
git add .
git commit -m "Initial commit"
```

Go to https://github.com/new → create a repo named `sr-mess` (do NOT add README/`.gitignore`/license).

```bash
git remote add origin https://github.com/YOUR_USERNAME/sr-mess.git
git push -u origin main
```

---

## Step 2: Deploy Database + Backend (via Render Blueprint)

Render Blueprint reads `backend/render.yaml` and creates both the database and the API service in one go.

1. Go to https://dashboard.render.com
2. Click **New +** → **Blueprint**
3. Select your `sr-mess` repository
4. Set **Branch** to `main`
5. Set **Root Directory** to `backend` (important — the `render.yaml` is inside `backend/`)
6. Click **Apply**

Render will create:
- **sr-mess-db** — PostgreSQL database (free)
- **sr-mess-api** — Web service running the FastAPI backend

Wait for both to show green **Live** status. This takes 3–5 minutes.

> If you get an error about `PYTHON_VERSION`, set environment variable `PYTHON_VERSION = 3.11` in the web service's **Environment** tab and Redeploy (Manual Deploy → Clear build cache & deploy).

After deployment, copy your backend URL:
- Go to the **sr-mess-api** dashboard
- Copy the URL at the top (e.g. `https://sr-mess-api.onrender.com`)

---

## Step 3: Confirm Database Connection

Render automatically injects the `DATABASE_URL` into the web service. Verify it:

1. Go to **sr-mess-api** dashboard → **Environment** tab
2. Confirm `DATABASE_URL` is present (blue pill icon means it's auto-injected from the database)
3. Confirm `SECRET_KEY` was auto-generated
4. Add this environment variable (click **Add Environment Variable**):
   - **Key:** `CORS_ORIGINS`
   - **Value:** `https://sr-mess-frontend.onrender.com` (enter this now — you'll update it after deploying frontend)

---

## Step 4: Deploy Frontend

1. Go to https://dashboard.render.com
2. Click **New +** → **Static Site**
3. Select your `sr-mess` repository
4. Configure:
   - **Name:** `sr-mess-frontend`
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
5. Click **Advanced** → **Add Environment Variable**:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://sr-mess-api.onrender.com` (your backend URL from Step 2)
6. Click **Deploy Static Site**

Wait for deployment to finish. Copy the frontend URL (e.g. `https://sr-mess-frontend.onrender.com`).

---

## Step 5: Update CORS with Final Frontend URL

1. Go to **sr-mess-api** dashboard → **Environment** tab
2. Update `CORS_ORIGINS` to: `https://sr-mess-frontend.onrender.com`
3. Click **Save Changes**
4. Go to **Events** tab → click **Manual Deploy** → **Clear build cache & deploy**

---

## Step 6: Seed Admin User

The backend auto-creates an admin account on startup via `seed_admin()` in `app/main.py`. Check the **Logs** tab of **sr-mess-api** to confirm.

Default admin credentials (from your codebase):
- Check `backend/app/services/auth_service.py` for the default admin email/password.

If you need to create additional users or reset the admin, use the API directly:

```bash
# Via API (after deployment)
curl -X POST https://sr-mess-api.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

---

## Step 7: Test the App

1. Open `https://sr-mess-frontend.onrender.com` in a browser
2. Log in with the admin credentials
3. Verify:
   - Dashboard loads correctly
   - Menu creation works
   - Voting/attendance/etc. work
4. Check **sr-mess-api** → **Logs** for any errors

---

## Step 8: Custom Domain (Optional, Paid)

If the college wants a custom domain like `mess.collegename.ac.in`:

1. Go to **sr-mess-frontend** → **Settings** → **Custom Domain**
2. Add your domain and follow Render's DNS instructions
3. Update `CORS_ORIGINS` in the backend to include the new domain
4. Redeploy the backend

---

## Maintenance & Common Issues

### Backend spins down after inactivity
The free Render web service goes idle after 15 minutes. The first request after idle takes ~30 seconds to wake up. This is normal for the free tier.

To keep it awake 24/7, upgrade to the **Starter** plan ($7/month) or use a free uptime monitor like [UptimeRobot](https://uptimerobot.com) to ping `https://sr-mess-api.onrender.com/api/health` every 10 minutes.

### Applying code changes
After pushing new code to GitHub:
- **Backend:** Dashboard → sr-mess-api → Manual Deploy → Deploy latest commit
- **Frontend:** Dashboard → sr-mess-frontend → Manual Deploy → Deploy latest commit

### Database backup
Render automatically backs up the database. You can also export it manually:
1. Go to **sr-mess-db** → **Info** tab
2. Copy the `External Database Connection String`
3. Use `pg_dump` to back up:
   ```bash
   pg_dump "EXTERNAL_CONNECTION_STRING" > mess_backup.sql
   ```

### Reset database
1. Go to **sr-mess-db** → **Settings** → **Reset Database**
2. Redeploy sr-mess-api (the `seed_admin()` function will recreate the admin account)

### View logs
- Backend: **sr-mess-api** → **Logs** tab
- Frontend build: **sr-mess-frontend** → **Events** tab → click on a deploy

---

## Alternative: Docker Deployment (Any Cloud)

If you prefer Docker over the Render blueprint:

1. Ensure `DATABASE_URL` points to your PostgreSQL instance
2. Build and run:

```bash
docker build -t sr-mess-api -f Dockerfile .
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/mess \
  -e SECRET_KEY=your-secret \
  -e CORS_ORIGINS=https://your-frontend.com \
  sr-mess-api
```

---

## Summary of Free Resources

| Resource | What You Get | Limits |
|----------|-------------|--------|
| Render PostgreSQL | 1 GB storage | Max 100 concurrent connections |
| Render Web Service | 512 MB RAM, shared CPU | Spins down after 15 min idle |
| Render Static Site | Global CDN, 100 GB bandwidth | 500 builds/month |
| Total Cost | **$0** | Upgrade to Starter ($7/mo) to remove spin-down |
