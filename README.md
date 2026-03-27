# 🎬 YouTube Analyst — Aman's Research Tool

Paste a YouTube URL → get structured investment analysis powered by Gemini.  
Replaces the Colab notebook. Runs as a live web app accessible from any browser.

---

## Project Structure

```
Youtube-Analyser/
├── backend/
│   ├── app.py              ← Flask API (fetches transcript + calls Gemini)
│   └── requirements.txt
├── frontend/
│   └── index.html          ← Web UI (hosted on GitHub Pages)
├── render.yaml             ← Render.com deployment config
└── README.md
```

---

## Step 1 — Push to GitHub

1. Create a new GitHub repo called `yt-analyzer`
2. Upload all these files maintaining the folder structure
3. Commit and push

---

## Step 2 — Deploy Backend on Render (free)

1. Go to [render.com](https://render.com) → New → Web Service
2. Connect your GitHub repo
3. Render will auto-detect `render.yaml` — confirm settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Add Environment Variable:
   - Key: `GEMINI_API_KEY`
   - Value: your Gemini API key
5. Click **Deploy**
6. Wait ~2 min. Copy your Render URL (e.g. `https://yt-analyzer-api.onrender.com`)

---

## Step 3 — Update Frontend with your Backend URL

In `frontend/index.html`, find this line near the top of the `<script>` tag:

```js
const BACKEND_URL = "https://YOUR-RENDER-APP.onrender.com";
```

Replace with your actual Render URL. Commit and push.

---

## Step 4 — Enable GitHub Pages

1. Go to your repo → **Settings** → **Pages**
2. Source: Deploy from branch → `main` → folder: `/frontend`
3. Save → your app will be live at:
   `https://YOUR-USERNAME.github.io/yt-analyzer`

---

## Usage

1. Open the GitHub Pages URL in any browser
2. Paste any YouTube finance video URL
3. Click **Analyze →**
4. Get structured analysis with:
   - What the video is about
   - Core strategy explained
   - Their story with numbers
   - Key actionable lessons
   - Risks & caveats
   - Aman's Takeaway (personalised for your investing context)

---

## Notes

- Render free tier sleeps after 15 min of inactivity — first request after sleep takes ~30s to wake up
- To avoid cold starts, upgrade to Render Starter ($7/mo) or keep the tab open
- Gemini model used: `gemini-2.5-flash-lite` (same as your Colab notebook)
- Supports English transcripts by default; falls back to any available language
