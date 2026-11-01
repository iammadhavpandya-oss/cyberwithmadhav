# Deploying CyberWithMadhav

The site is plain static files, so any static host works for free. The backend is optional.

## Static site (pick one)

### GitHub Pages
1. Create a repo and push this folder (`git remote add origin … && git push -u origin main`).
2. Repo → Settings → Pages → Source: *Deploy from a branch* → `main` / `/ (root)`.
3. Site appears at `https://<user>.github.io/<repo>/`. For a custom domain, add it in the Pages settings and create a `CNAME` DNS record.
The `backend/`, `tools/` and `docs/` folders are harmless to publish, but you can exclude them by deploying from a separate `site` branch.

### Netlify
- Drag-and-drop the folder at app.netlify.com/drop, or connect the repo with **Build command:** *(empty)*, **Publish directory:** `.`

### Cloudflare Pages
- Workers & Pages → Create → Pages → connect the repo. Framework preset *None*, build command empty, output directory `/`.
- Or with the CLI: `npx wrangler pages deploy . --project-name cyberwithmadhav`

After deploying, update canonical / `og:url` in `index.html` to the real domain.

## Backend (optional)
Without it, the forms show an "email me" fallback — fine to launch without.

Any host that runs Python works (Render, Railway, Fly.io, PythonAnywhere, a small VPS):
```bash
pip install -r backend/requirements.txt
cd backend
CWM_ALLOWED_ORIGINS=https://your-domain \
CWM_DB_PATH=/var/data/cwm.sqlite3 \
CWM_TRUST_PROXY=1 \
gunicorn -w 1 -b 0.0.0.0:8080 app:app
```
- Use **1 worker** (the rate limiter is in-memory) and a **persistent disk** for the SQLite file (free tiers with ephemeral disks lose data on restart).
- Set `CWM_TRUST_PROXY=1` only when behind exactly one reverse proxy (needed for correct per-IP limits).
- Put it behind HTTPS (the host's proxy, or Caddy/Nginx on a VPS).
- Then add to `index.html` `<head>`: `<meta name="cwm-api" content="https://api.your-domain">`.
- Back up / export with `python export.py subscribers`.
