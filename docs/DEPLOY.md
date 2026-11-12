# Deploy (public URL for the jury)

Backend on **Render** (free, Docker, no database: all data ships inside the image from
`backend/app/reference/`), frontend on **Vercel** (free). Both redeploy automatically on every push
to `dev` (the repo's default branch). ~10 minutes, once.

## 1. Backend — Render
1. https://dashboard.render.com → sign in with GitHub → **New → Blueprint**.
2. Pick the repo `SportsDataAnalyticsHackathon` (branch `dev`). Render reads `render.yaml` and creates
   the `sports-analytics-api` web service.
3. When asked for `CORS_ORIGINS`, enter `["http://localhost:5173"]` for now (fixed in step 3).
4. Wait for the first build (~5 min). Open `https://<your-api>.onrender.com/api/health` →
   `{"status":"ok","database":false}` is expected (no database in production). Copy the base URL.

## 2. Frontend — Vercel
1. https://vercel.com → sign in with GitHub → **Add New → Project** → import the repo.
2. **Root Directory:** `frontend` (Vite is detected). **Production branch:** `dev`
   (Settings → Git, if it defaults to `main`).
3. **Environment variable:** `VITE_API_URL` = `https://<your-api>.onrender.com` (no trailing slash).
4. Deploy → copy the URL, e.g. `https://club-footprint.vercel.app`.

## 3. Connect them
Render → service → Environment → `CORS_ORIGINS` = `["https://club-footprint.vercel.app"]`
(JSON list with your real Vercel URL) → save (redeploys).

## Before the presentation
- Render's free tier **sleeps after ~15 min idle**; the first request then takes ~1 minute.
  Open the app 2–3 minutes before presenting.
- In production the Data explorer is hidden and its API disabled (raw data isn't deployed).
