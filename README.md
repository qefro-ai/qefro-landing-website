# Qefro Landing Website

Premium static SaaS marketing site for [Qefro](https://qefro.com) — SEO / AEO / GEO ready.

## Production

| Surface | URL |
| --- | --- |
| Marketing (canonical) | https://qefro.com |
| Customer portal | https://app.qefro.com |
| Cloudflare Pages (preview / optional origin) | https://qefro-landing-website.pages.dev |
| Docker image (legacy / fallback) | `ghcr.io/qefro-ai/qefro-landing-website:latest` |

### Cloudflare Pages (recommended)

CI workflow: `.github/workflows/cloudflare-pages.yml`

GitHub Actions secrets (same values as the docs repo):

- `CLOUDFLARE_API_TOKEN` — Pages Write
- `CLOUDFLARE_ACCOUNT_ID`

```bash
gh secret set CLOUDFLARE_API_TOKEN -R qefro-ai/qefro-landing-website
gh secret set CLOUDFLARE_ACCOUNT_ID -R qefro-ai/qefro-landing-website
```

**Point `qefro.com` at Pages**:

1. Deploy once → open `https://qefro-landing-website.pages.dev` and verify `/privacy`, `/terms`, `/pricing`.
2. In Cloudflare Dashboard → Pages → **qefro-landing-website** → Custom domains → add `qefro.com` (and optionally `www.qefro.com`).
3. Ensure DNS proxy (orange cloud) is enabled in Cloudflare for production web security.
4. Route app and API services through your hardened edge reverse proxy with origin access controls enabled.

Do **not** point API or backend services at the Pages project — those stay on secure backend infrastructure.

## Local

```bash
npm install
npm run build:motion   # bundles Motion into assets/js/qefro-motion.js
python3 generate.py
# optional: docker build -t qefro-landing . && docker run --rm -p 8088:80 qefro-landing
```

Motion animations load from `assets/js/qefro-motion.js` (vanilla Motion API — see https://motion.dev/docs/quick-start).
