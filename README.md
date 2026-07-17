# Qefro Landing Website

Premium static SaaS marketing site for [Qefro](https://qefro.com) — SEO / AEO / GEO ready.

## Production

- Marketing site: https://qefro.com
- Customer portal: https://app.qefro.com
- Docker image: `ghcr.io/qefro-ai/qefro-landing-website:latest`

## Local

```bash
npm install
npm run build:motion   # bundles Motion into assets/js/qefro-motion.js
python3 generate.py
# optional: docker build -t qefro-landing . && docker run --rm -p 8088:80 qefro-landing
```

Motion animations load from `assets/js/qefro-motion.js` (vanilla Motion API — see https://motion.dev/docs/quick-start).