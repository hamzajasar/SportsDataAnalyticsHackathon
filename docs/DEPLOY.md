# Deploy (public URL for the jury)

Backend + database on **Render** (free), frontend on **Vercel** (free). Both deploy from the `dev`
branch and redeploy automatically on every push to `dev`. ~10 minutes, once.

## 1. Backend + database — Render
1. https://dashboard.render.com → sign in with GitHub → **New → Blueprint**.
2. Pick the repo `SportsDataAnalyticsHackathon`, branch **`dev`**. Render reads `render.yaml` and creates:
   - `club-footprint-api` (Docker web service) and `club-footprint-db` (free Postgres).
3. When asked for `CORS_ORIGINS`, enter `["http://localhost:5173"]` for now (fixed in step 3).
4. Wait for the first build (~5 min). Open `https://<your-api>.onrender.com/api/health` →
   should show `{"status":"ok","database":true}`. Copy this base URL.

## 2. Frontend — Vercel
1. https://vercel.com → sign in with GitHub → **Add New → Project** → import the repo.
2. **Root Directory:** `frontend` (framework is detected as Vite). **Production branch:** `dev`
   (Settings → Git, if it defaults to `main`).
3. **Environment variable:** `VITE_API_URL` = `https://<your-api>.onrender.com` (no trailing slash).
4. Deploy → copy the URL, e.g. `https://club-footprint.vercel.app`.

## 3. Connect them
Render → `club-footprint-api` → Environment → `CORS_ORIGINS` = `["https://club-footprint.vercel.app"]`
(JSON list, your real Vercel URL) → save (redeploys).

## Before the presentation
- Render's free tier **sleeps after ~15 min idle**; the first request then takes ~1 minute.
  Open the app 2–3 minutes before presenting.
- Production differences: the Data explorer is hidden/disabled (raw data isn't deployed).
