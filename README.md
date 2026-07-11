# Qefro Landing Website

Premium static SaaS marketing site for [Qefro](https://qefro.com) — optimized for SEO, AEO (answer engines), and GEO (generative engines).

## Live site

https://qefro-ai.github.io/qefro-landing-website/

## Pages

- `index.html` — brand-first landing
- `features.html`, `how-it-works.html`, `use-cases.html`, `security.html`, `pricing.html`
- `faq.html` — FAQ with `FAQPage` JSON-LD
- `what-is-qefro.html`, `qefro-pricing.html` — answer-first AEO pages
- `contact.html`, `404.html`
- `llms.txt`, `robots.txt`, `sitemap.xml`

## Regenerate HTML

```bash
python3 generate.py
```

## Deploy

Pushes to `main` deploy via GitHub Pages (Actions workflow). Enable **Settings → Pages → Source: GitHub Actions** once.
