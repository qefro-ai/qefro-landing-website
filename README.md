# Qefro Landing Website

Premium static SaaS marketing site for [Qefro](https://qefro.com) — SEO / AEO / GEO ready.

## Production

- Marketing site: https://qefro.com
- Customer portal: https://app.qefro.com
- Docker image: `ghcr.io/qefro-ai/qefro-landing-website:latest`

## Local

```bash
python3 generate.py
docker build -t qefro-landing .
docker run --rm -p 8088:80 qefro-landing
```

## Regenerate HTML

```bash
python3 generate.py
```
