#!/usr/bin/env python3
"""Generate Qefro static pages — portal-inspired dark design + SEO/AEO markup."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from seo_landings import (
    all_landings,
    feature_link_grid,
    industry_link_grid,
    topic_link_grid,
    vertical_link_grid,
    sitemap_slugs,
)

ROOT = Path(__file__).resolve().parent
SITE = "https://qefro.com"
PORTAL = "https://app.qefro.com"
API = "https://api.qefro.com"
WIDGET_CDN = "https://cdn.qefro.com/widget.js"
PORTAL_LOGIN = f"{PORTAL}/login"
PORTAL_SIGNUP = f"{PORTAL}/login?mode=signup"
DOCS = "https://docs.qefro.com"
ASSET_VERSION = "40"
OG_IMAGE = f"{SITE}/assets/images/og-cover.png"
OG_IMAGE_ALT = (
    "Qefro is the AI platform that connects conversations to your business — "
    "Customer AI, Employee AI, and Admin Console."
)
DEMO_WIDGET_TOKEN = "demo-qefro-widget-token"
BUILD_DATE = date.today().isoformat()
WIDGET_WELCOME = (
    "Hi! I'm the Qefro assistant. Ask how Qefro connects conversations to your "
    "business — Customer AI, Employee AI, business actions, pricing, and security."
)
META_KEYWORDS = (
    "AI Workspace, Enterprise AI Platform, AI Customer Support Platform, "
    "Internal AI Assistant, Customer Support AI, Business AI, AI Knowledge Platform, "
    "AI Employee Assistant, AI Powered Helpdesk, AI Business Automation, "
    "Organizational AI, WhatsApp AI"
)

# Inline SVG icons (lucide-like)
ICONS = {
    "sparkles": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15z"/></svg>',
    "zap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>',
    "play": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="6 4 20 12 6 20 6 4"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l8 4v5c0 5-3.5 8.5-8 10-4.5-1.5-8-5-8-10V7l8-4z"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/></svg>',
    "server": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><path d="M7 7h.01M7 17h.01"/></svg>',
    "file": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8l-5-5z"/><path d="M14 3v5h5"/></svg>',
    "globe": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18"/></svg>',
    "bot": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="8" width="16" height="12" rx="3"/><path d="M9 8V6a3 3 0 016 0v2M9 14h.01M15 14h.01"/></svg>',
    "msg": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a8 8 0 01-8 8H7l-4 3V12a8 8 0 018-8h2a8 8 0 018 8z"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19V5M4 19h16"/><path d="M8 16v-5M12 16V8M16 16v-3"/></svg>',
    "building": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 21V5a1 1 0 011-1h8a1 1 0 011 1v16M14 9h5a1 1 0 011 1v11"/><path d="M8 8h2M8 12h2M8 16h2M17 13h1M17 17h1"/></svg>',
    "headphones": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 13a8 8 0 0116 0"/><path d="M4 13v5a2 2 0 002 2h1v-7H6a2 2 0 00-2 2zM20 13v5a2 2 0 01-2 2h-1v-7h1a2 2 0 012 2z"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="1"><path d="M12 3l2.4 7.2H22l-6 4.4 2.3 7L12 17.8 5.7 21.6 8 14.6 2 10.2h7.6L12 3z"/></svg>',
    "chevron": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>',
    "chevr": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 6l6 6-6 6"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>',
    "sun": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>',
}

for _name, _svg in list(ICONS.items()):
    ICONS[_name] = _svg.replace(
        "<svg ",
        '<svg class="icon" width="20" height="20" aria-hidden="true" ',
        1,
    )

NAV = [
    ("how-it-works", "Platform"),
    ("features", "Features"),
    ("use-cases", "Solutions"),
    ("security", "Security"),
    ("pricing", "Pricing"),
]

# Canonical indexable URLs for sitemap (extensionless; nginx 301s .html → these).
# Images listed here are included via the image sitemap extension.
SITEMAP_ENTRIES: list[tuple[str, list[tuple[str, str]]]] = [
    ("", [(f"{SITE}/assets/images/og-cover.png", "Qefro AI Workspace Platform")]),
    ("features", []),
    ("how-it-works", []),
    ("use-cases", []),
    ("security", []),
    ("pricing", []),
    ("faq", []),
    ("contact", []),
    ("what-is-qefro", []),
    ("qefro-pricing", []),
    ("benchmark", []),
    ("privacy", []),
    ("terms", []),
]

# Programmatic SEO landings (topics, industries, features) — appended for sitemap.
for _slug in sitemap_slugs():
    SITEMAP_ENTRIES.append((_slug, []))


def site_url(path: str) -> str:
    """Canonical absolute URL (extensionless, trailing slash on home)."""
    if not path or path in {"index.html", "/"}:
        return f"{SITE}/"
    clean = path.removesuffix(".html")
    return f"{SITE}/{clean}"


def meta_block(
    title: str,
    description: str,
    path: str,
    *,
    robots: str = (
        "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    ),
    include_canonical: bool = True,
) -> str:
    url = site_url(path)
    # Absolute HTTPS canonicals only — Google prefers absolute URLs for rel=canonical
    canonical = f'  <link rel="canonical" href="{url}" />\n' if include_canonical else ""
    return f"""  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}" />
  <meta name="keywords" content="{escape(META_KEYWORDS)}" />
  <meta name="robots" content="{robots}" />
  <meta name="googlebot" content="{robots}" />
  <meta name="author" content="Qefro" />
  <meta name="format-detection" content="telephone=no" />
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#080a12" media="(prefers-color-scheme: dark)" />
  <meta name="theme-color" content="#ffffff" id="theme-color-meta" />
  <script>
    (function () {{
      var saved = localStorage.getItem("theme");
      if (saved === "dark") document.documentElement.setAttribute("data-theme", "dark");
    }})();
  </script>
{canonical}  <link rel="alternate" type="text/plain" href="{SITE}/llms.txt" title="LLM-readable summary" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Qefro" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(description)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{OG_IMAGE}" />
  <meta property="og:image:secure_url" content="{OG_IMAGE}" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{OG_IMAGE_ALT}" />
  <meta property="og:locale" content="en_US" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@qefro" />
  <meta name="twitter:title" content="{escape(title)}" />
  <meta name="twitter:description" content="{escape(description)}" />
  <meta name="twitter:image" content="{OG_IMAGE}" />
  <meta name="twitter:image:alt" content="{OG_IMAGE_ALT}" />
  <meta name="geo.region" content="IN" />
  <meta name="geo.placename" content="Global" />
  <!-- Favicons: stable URLs, square, ≥48px PNG for Google Search eligibility
       https://developers.google.com/search/docs/appearance/favicon-in-search#guidelines -->
  <link rel="icon" href="/assets/images/favicon-192.png" type="image/png" sizes="192x192" />
  <link rel="icon" href="/assets/images/favicon.png" type="image/png" sizes="64x64" />
  <link rel="icon" href="/assets/images/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/assets/images/apple-touch-icon.png" sizes="180x180" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="dns-prefetch" href="https://www.googletagmanager.com" />
  <link rel="dns-prefetch" href="https://www.clarity.ms" />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet" />
  <link rel="preload" href="/assets/css/styles.css?v={ASSET_VERSION}" as="style" />
  <link rel="stylesheet" href="/assets/css/styles.css?v={ASSET_VERSION}" />"""


def header(active: str | None = None) -> str:
    # Root-relative hrefs so Google resolves the same canonical path from every page
    # https://developers.google.com/search/docs/crawling-indexing/links-crawlable
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if active == href else ""
        links.append(f'        <a href="/{href}"{cur}>{label}</a>')
    mobile = "\n".join(
        f'      <a href="/{href}"{" aria-current=\"page\"" if active == href else ""}>{label}</a>'
        for href, label in NAV
    )
    return f"""  <a class="skip-link" href="#main">Skip to content</a>
  <div class="ambient" aria-hidden="true">
    <div class="ambient-blob ambient-a"></div>
    <div class="ambient-blob ambient-b"></div>
    <div class="ambient-blob ambient-c"></div>
    <div class="ambient-grid"></div>
  </div>
  <header class="site-header">
    <div class="wrap nav" data-nav>
      <a class="brand" href="/" aria-label="Qefro home">
        <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI Workspace Platform logo" width="40" height="40" decoding="async" fetchpriority="high" />
        <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" decoding="async" />
      </a>
      <nav class="nav-links" aria-label="Primary">
{chr(10).join(links)}
        <a href="/faq"{' aria-current="page"' if active == "faq" else ""}>FAQ</a>
        <a href="{DOCS}" rel="noopener noreferrer">Docs</a>
      </nav>
      <div class="nav-cta">
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to dark mode">
          <span class="icon-moon" aria-hidden="true">{ICONS["moon"]}</span>
          <span class="icon-sun" aria-hidden="true">{ICONS["sun"]}</span>
        </button>
        <a class="btn-link" href="{PORTAL_LOGIN}">Sign In</a>
        <a class="btn btn-primary" href="{PORTAL_SIGNUP}">Free Trial {ICONS["arrow"]}</a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false">{ICONS["menu"]}</button>
      </div>
    </div>
    <div class="mobile-panel wrap">
{mobile}
      <a href="/faq">FAQ</a>
      <a href="{DOCS}" rel="noopener noreferrer">Docs</a>
      <a class="btn btn-primary" href="{PORTAL_SIGNUP}" style="justify-content:center;margin-top:0.5rem">Free Trial</a>
      <a href="{PORTAL_LOGIN}">Sign In</a>
      <div class="mobile-panel-tools">
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to dark mode">
          <span class="icon-moon" aria-hidden="true">{ICONS["moon"]}</span>
          <span class="icon-sun" aria-hidden="true">{ICONS["sun"]}</span>
        </button>
      </div>
    </div>
  </header>"""


def widget_embed(theme: str = "light") -> str:
    return f"""  <script id="qefro-widget-script"
    src="{WIDGET_CDN}"
    data-token="{DEMO_WIDGET_TOKEN}"
    data-endpoint="{API}"
    data-theme="{theme}"
    data-position="bottom-right"
    data-primary-color="#7c3aed"
    data-welcome-message="{WIDGET_WELCOME}"></script>"""


def page_scripts(extra: str = "") -> str:
    return f"""{widget_embed()}
  <script src="/assets/js/main.js?v={ASSET_VERSION}" defer></script>
  <script type="module" src="/assets/js/qefro-motion.js?v={ASSET_VERSION}"></script>{extra}"""


def footer() -> str:
    return f"""  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-top">
        <a class="brand" href="/" aria-label="Qefro home">
          <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI Workspace Platform logo" width="40" height="40" decoding="async" />
          <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" decoding="async" />
        </a>
        <nav class="footer-links" aria-label="Footer">
          <a href="/how-it-works">Platform</a>
          <a href="/features">Features</a>
          <a href="/use-cases">Solutions</a>
          <a href="/ai-customer-support">AI Support</a>
          <a href="/ai-customer-support-by-industry">By Industry</a>
          <a href="/ai-for-saas">AI for SaaS</a>
          <a href="/pricing">Pricing</a>
          <a href="/security">Security</a>
          <a href="/what-is-qefro">What is Qefro</a>
          <a href="/benchmark">Benchmark</a>
          <a href="/faq">FAQ</a>
          <a href="{DOCS}">Docs</a>
          <a href="/contact">Contact</a>
          <a href="/privacy">Privacy</a>
          <a href="/terms">Terms</a>
          <a href="/llms.txt">llms.txt</a>
          <a href="/sitemap.xml">Sitemap</a>
        </nav>
      </div>
      <div class="footer-bottom">
        <p>© <span data-year></span> qefro AI. All rights reserved.</p>
        <p>Configure once. Deploy AI for customers and employees everywhere.</p>
      </div>
    </div>
  </footer>"""


def page(
    title: str,
    description: str,
    path: str,
    body: str,
    active: str | None = None,
    jsonld: list[str] | None = None,
    *,
    robots: str = (
        "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    ),
    include_canonical: bool = True,
    extra_scripts: str = "",
) -> str:
    schemas = "\n".join(f'  <script type="application/ld+json">\n{b}\n  </script>' for b in (jsonld or []))
    clarity = """  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "xmaswr5i7h");
  </script>"""
    gtag = """  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-BD3M2H7X1E"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-BD3M2H7X1E');
  </script>"""
    return f"""<!DOCTYPE html>
<html lang="en" data-api-url="{API}" data-widget-cdn="{WIDGET_CDN}">
<head>
{meta_block(title, description, path, robots=robots, include_canonical=include_canonical)}
{schemas}
{gtag}
{clarity}
</head>
<body>
  <div class="page-shell">
{header(active)}
  <main id="main">
{body}
  </main>
{footer()}
  </div>
{page_scripts(extra_scripts)}
</body>
</html>
"""


def crumbs(items: list[tuple[str, str]]) -> str:
    bits = []
    for name, href in items:
        if href:
            bits.append(f'<a href="{href}">{name}</a><span aria-hidden="true">/</span>')
        else:
            bits.append(f"<span>{name}</span>")
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb">{"".join(bits)}</nav>'


def breadcrumb_json(items: list[tuple[str, str]]) -> str:
    elements = []
    for i, (name, href) in enumerate(items, start=1):
        if href in {"", "/"}:
            item = f"{SITE}/"
        else:
            item = site_url(href.removeprefix("/"))
        elements.append({"@type": "ListItem", "position": i, "name": name, "item": item})
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}, indent=2)


def webpage_json(title: str, description: str, path: str) -> str:
    """WebPage + dateModified so Google can understand freshness signals."""
    url = site_url(path)
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{SITE}/#website"},
            "about": {"@id": f"{SITE}/#organization"},
            "dateModified": BUILD_DATE,
            "inLanguage": "en-US",
            "primaryImageOfPage": {
                "@type": "ImageObject",
                "url": OG_IMAGE,
                "width": 1200,
                "height": 630,
            },
        },
        indent=2,
    )


ORG_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE}/#organization",
        "name": "Qefro",
        "alternateName": ["Qefro AI", "qefro"],
        "url": SITE,
        "logo": {
            "@type": "ImageObject",
            "url": f"{SITE}/assets/images/qefro-logo.png",
            "width": 512,
            "height": 512,
            "contentUrl": f"{SITE}/assets/images/qefro-logo.png",
        },
        "image": OG_IMAGE,
        "description": (
            "Qefro is the AI platform that connects conversations to your business. "
            "Build AI assistants that answer questions and take secure business actions "
            "across Customer AI, Employee AI, and the Admin Console."
        ),
        "email": "support@qefro.com",
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "contactType": "customer support",
                "email": "support@qefro.com",
                "url": f"{SITE}/contact",
                "availableLanguage": ["English"],
            },
            {
                "@type": "ContactPoint",
                "contactType": "sales",
                "email": "support@qefro.com",
                "url": f"{SITE}/contact",
                "availableLanguage": ["English"],
            },
        ],
        "sameAs": ["https://github.com/qefro-ai"],
        "foundingDate": "2024",
        "knowsAbout": [
            "AI Workspace Platform",
            "Customer support AI",
            "Internal AI assistants",
            "Retrieval-augmented generation",
            "Business process automation",
        ],
    },
    indent=2,
)

# Site name preference for Google Search results
# https://developers.google.com/search/docs/appearance/site-names
WEBSITE_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE}/#website",
        "name": "Qefro",
        "alternateName": ["Qefro AI", "qefro.com"],
        "url": f"{SITE}/",
        "description": (
            "Qefro is the AI platform that connects conversations to your business. "
            "Build AI assistants that answer questions and take secure business actions."
        ),
        "publisher": {"@id": f"{SITE}/#organization"},
        "inLanguage": "en-US",
        "copyrightHolder": {"@id": f"{SITE}/#organization"},
    },
    indent=2,
)

# SoftwareApplication: required name + offers.price. Do NOT invent AggregateRating —
# Google requires real ratings/reviews for software-app rich results.
# https://developers.google.com/search/docs/appearance/structured-data/software-app
SOFTWARE_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": ["SoftwareApplication", "WebApplication"],
        "name": "Qefro",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web browser",
        "browserRequirements": "Requires JavaScript. Requires HTML5.",
        "url": SITE,
        "image": OG_IMAGE,
        "screenshot": OG_IMAGE,
        "description": (
            "Qefro is the AI platform that connects conversations to your business. "
            "Build AI assistants that answer questions and take secure business actions "
            "across Customer AI, Employee AI, and the Admin Console — via REST/OpenAPI "
            "or the Backend SDK."
        ),
        "keywords": META_KEYWORDS,
        "author": {"@id": f"{SITE}/#organization"},
        "publisher": {"@id": f"{SITE}/#organization"},
        "offers": {
            "@type": "Offer",
            "price": 0,
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock",
            "url": f"{SITE}/pricing",
            "description": "14-day free trial available — no credit card required",
        },
        "featureList": [
            "AI Workspaces",
            "Knowledge platform with multilingual RAG",
            "Business actions via REST/OpenAPI or Backend SDK",
            "Customer AI website widget and WhatsApp",
            "Employee AI Internal Portal",
            "Admin Console",
            "Tenant isolation and encrypted secrets",
        ],
    },
    indent=2,
)

# Use SoftwareApplication — not Product — so Google does not evaluate /pricing as a Merchant listing
# (shipping/return fields are for physical goods). SaaS belongs in software-app rich results.
PRICING_OFFERS_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": ["SoftwareApplication", "WebApplication"],
        "name": "Qefro",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web browser",
        "url": f"{SITE}/pricing",
        "image": OG_IMAGE,
        "description": (
            "AI Workspace Platform with knowledge retrieval, business actions, "
            "website widget, Internal Portal, and WhatsApp."
        ),
        "brand": {"@type": "Brand", "name": "Qefro"},
        "offers": [
            {
                "@type": "Offer",
                "name": "Trial (14 Days)",
                "price": 0,
                "priceCurrency": "USD",
                "description": "Full access for 14 days. No credit card required.",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
            {
                "@type": "Offer",
                "name": "Starter",
                "price": 29,
                "priceCurrency": "USD",
                "description": "Billed annually ($39/month if billed monthly)",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
            {
                "@type": "Offer",
                "name": "Growth",
                "price": 99,
                "priceCurrency": "USD",
                "description": "Billed annually ($119/month if billed monthly)",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
        ],
    },
    indent=2,
)

FAQ_ACCURACY_ANSWER_HTML = (
    "Qefro retrieves only from your verified content and is designed to decline answering when "
    "no relevant information exists in your knowledge base, rather than guessing. "
    'See our <a href="/benchmark">benchmark methodology</a> for how we evaluate accuracy and refusal behavior.'
)
FAQ_ACCURACY_ANSWER_PLAIN = (
    "Qefro retrieves only from your verified content and is designed to decline answering when "
    "no relevant information exists in your knowledge base, rather than guessing. "
    f"See our benchmark methodology at {SITE}/benchmark for evaluation details."
)

PRICE_FAIR_USE_NOTE = (
    '<p class="price-desc price-fair-use">'
    "Conversation and document allowances are listed above. "
    'Contact <a href="/contact">Sales</a> for storage and processing volume details on Growth and Enterprise.'
    "</p>"
)


def price_feat(text: str, meta: str | None = None) -> str:
    """Feature row with check icon; keep text in a body so the icon never orphans on wrap."""
    body = text if meta is None else f'{text} <span class="price-meta">{meta}</span>'
    return f'<li>{ICONS["check"]}<span class="price-feat-body">{body}</span></li>'


def price_cards_html(*, interactive: bool = False) -> str:
    """Shared Trial / Starter / Growth / Enterprise cards for homepage + /pricing."""
    cta = ' data-price-cta' if interactive else ""
    clarity = (
        lambda event: f' data-clarity-event="{event}"' if interactive else ""
    )
    return f"""          <article class="price-card{cta}">
            <h3>Trial (14 Days)</h3>
            <p class="price-best">Best for evaluating the platform</p>
            <div class="price-amount">$0</div>
            <p class="price-desc">14-day free trial — no credit card</p>
            <ul class="price-feats">
              {price_feat("Full premium access for 14 days")}
              {price_feat("AI support, WhatsApp, voice &amp; widget")}
              {price_feat("Knowledge base, crawler &amp; uploads")}
              {price_feat("Team management &amp; analytics")}
              {price_feat("Custom domains &amp; automation")}
              {price_feat("No credit card required")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_start_free")}>Start 14-Day Free Trial</a>
          </article>
          <article class="price-card{cta}">
            <h3>Starter</h3>
            <p class="price-best">Best for startups</p>
            <div class="price-amount" data-price-annual="$29" data-price-monthly="$39">$29 <span>/month</span></div>
            <p class="price-billed">billed annually · or $39/mo monthly</p>
            <p class="price-desc">For one team going live</p>
            <ul class="price-feats">
              {price_feat("1,000 conversations/month")}
              {price_feat("Knowledge for one team", "50 documents")}
              {price_feat("Connect up to 5 business systems")}
              {price_feat("Widget + WhatsApp + voice")}
              {price_feat("Custom branding")}
              {price_feat("Email support")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>Get Started</a>
          </article>
          <article class="price-card is-popular{cta}">
            <div class="price-pop">{ICONS["star"]} Most Popular</div>
            <h3>Growth</h3>
            <p class="price-best">Best for growing companies</p>
            <div class="price-amount" data-price-annual="$99" data-price-monthly="$119">$99 <span>/month</span></div>
            <p class="price-billed">billed annually · or $119/mo monthly</p>
            <p class="price-desc">For teams deploying across channels</p>
            <ul class="price-feats">
              {price_feat("10,000 conversations/month")}
              {price_feat("Knowledge across teams", "500 documents")}
              {price_feat("Widget + WhatsApp + voice")}
              {price_feat("Unlimited business system connections")}
              {price_feat("Analytics &amp; agent handoff")}
              {price_feat("Priority support")}
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-primary" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>Get Started</a>
          </article>
          <article class="price-card{cta}">
            <h3>Enterprise</h3>
            <p class="price-best">Best for regulated organizations</p>
            <div class="price-amount">Custom</div>
            <p class="price-desc">For advanced security and scale</p>
            <ul class="price-feats">
              {price_feat("Unlimited conversations")}
              {price_feat("Unlimited knowledge")}
              {price_feat("Private deployment")}
              {price_feat("SSO &amp; SAML (roadmap)")}
              {price_feat("Dedicated CSM")}
              {price_feat("Unlimited business system connections")}
              {price_feat("SLA guarantee")}
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-plan" href="/contact"{clarity("cta_talk_to_sales")}>Talk to Sales</a>
          </article>"""

PRODUCT_SCREENSHOTS = [
    ("inbox.webp", "Inbox", "Review conversations and hand off customer support when needed."),
    ("ai-widget.webp", "AI Widget", "Answer website visitors using your approved business knowledge."),
    ("knowledge-base.webp", "Knowledge Base", "Manage the sources your assistant can retrieve from."),
    ("analytics.webp", "Analytics", "Understand conversations, answer quality, and knowledge gaps."),
    ("document-upload.webp", "Document Upload", "Add PDFs and other business documents to your knowledge base."),
    ("team-dashboard.webp", "Team Dashboard", "Configure your workspace, team access, and assistants."),
]


def product_screenshots_html() -> str:
    """Render real product imagery only when the complete supplied set is available."""
    image_dir = ROOT / "assets" / "images" / "product"
    if not all((image_dir / filename).is_file() for filename, _, _ in PRODUCT_SCREENSHOTS):
        return ""

    cards = "\n".join(
        f"""          <figure class="product-shot-card">
            <img src="/assets/images/product/{filename}" alt="Qefro {title}: {description}" loading="lazy" decoding="async" width="1440" height="900" />
            <figcaption><strong>{title}</strong><span>{description}</span></figcaption>
          </figure>"""
        for filename, title, description in PRODUCT_SCREENSHOTS
    )
    return f"""    <section class="section section-alt" id="product">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["chart"]} Product</span>
          <h2>See Qefro in Action</h2>
          <p>Everything your team needs to configure, deploy, and improve organizational AI.</p>
        </div>
        <div class="product-shot-grid reveal">
{cards}
        </div>
      </div>
    </section>
"""


FAQ_ITEMS = [
    (
        "What is Qefro?",
        "Qefro is the AI platform that connects conversations to your business. "
        "Build AI assistants that answer questions and take secure business actions across "
        "Customer AI, Employee AI, and the Admin Console — sharing one knowledge platform, "
        "permission system, and set of business actions.",
    ),
    ("How much does Qefro cost?", "Every new organization gets a 14-day free trial with full premium access. No credit card required. Starter is $29/month billed annually ($39 monthly, connect up to 5 business systems). Growth is $99/month billed annually ($119 monthly, unlimited business system connections). Enterprise is custom."),
    ("What types of content can I upload?", "PDFs, Word documents, Markdown, plain text — or crawl entire websites automatically. Every workspace has its own isolated knowledge base with source citations when answering."),
    ("How accurate are the answers?", FAQ_ACCURACY_ANSWER_HTML),
    (
        "Is my data secure?",
        "Qefro provides tenant isolation and workspace isolation, encryption at rest and in transit, "
        "end-user identity forwarding, zero-trust style authorization for business actions, "
        "audit and execution logs, and encrypted storage for API secrets. End-user passwords are never stored, "
        "and your data is never used to train AI models. Private deployment is available for Enterprise. "
        "SOC 2 compliance is on our roadmap. Contact Sales for our current timeline.",
    ),
    (
        "Can Qefro take action in my systems?",
        "Yes. Two integration paths: connect existing APIs with REST/OpenAPI as Business Tools, "
        "or use the Backend SDK for authentication and workflows. AI can retrieve live data, "
        "create tickets, look up orders, and more — with encrypted credentials or end-user "
        "identity you forward via identify().",
    ),
    (
        "How long does setup take?",
        "Most teams embed the website widget in under 5 minutes. Connecting business systems and "
        "rolling out the Internal Portal depends on your APIs and knowledge prep — "
        "typically a day or less for straightforward integrations.",
    ),
    (
        "Can I use this for employees as well as customers?",
        "Yes. Customer AI runs on your website and WhatsApp. Employee AI runs in a branded Internal Portal "
        "(yourcompany.qefro.com) connected to company knowledge, business actions, and workspace permissions.",
    ),
    ("Do you offer enterprise pricing?", "Yes. Enterprise plans include unlimited conversations, private deployment, dedicated support, and custom SLAs. SSO/SAML is on the roadmap — talk to sales about your timeline."),
    (
        "What languages does Qefro support?",
        "Qefro supports multilingual document indexing and multilingual retrieval from the languages present "
        "in your knowledge base — including English, Arabic, Tamil, Hindi, and more. "
        "Upload non-English PDFs and docs, crawl multilingual websites, and answer multilingual customer questions. "
        "OCR extracts text from scanned pages and images so those sources can be indexed too.",
    ),
    (
        "How does widget authentication work?",
        "The embed script loads with a short-lived widget JWT issued by your backend or our portal. "
        "For signed-in users, call identify() with a user id and optional JWT so business actions can run on their behalf — "
        "Qefro never stores end-user passwords.",
    ),
    (
        "Can customers talk to a human agent?",
        "Yes. When the AI cannot answer or the customer asks for a person, conversations can be handed off to your team from the inbox. "
        "Full message history and tool execution logs stay attached for context.",
    ),
    (
        "What channels can I deploy on?",
        "Configure once, deploy everywhere: website widget (with optional voice), public chat pages, "
        "branded Internal Portal for employees, WhatsApp on Starter+, and direct API/WebSocket access for custom UIs.",
    ),
    (
        "How are workspaces and team roles handled?",
        "Each organization can create AI Workspaces (for example Customer Support, HR, or IT) with their own knowledge, "
        "instructions, business actions, conversations, and access rules. "
        "Owner, Admin, and Member roles control who can upload documents, configure actions, manage billing, and invite teammates.",
    ),
]

USE_CASES = [
    ("internal", "Employee AI", "building", [
        "Internal Portal access", "HR & policy queries", "IT helpdesk", "SOP & compliance lookup",
        "Team wiki search", "Benefits lookup", "Finance procedures", "Knowledge sharing",
    ]),
    ("support", "Customer Support", "headphones", [
        "Website & WhatsApp AI", "Order & refund policies", "Product documentation", "Self-service support",
        "Business actions via APIs", "Returns handling", "Lead capture", "Human handoff",
    ]),
    ("regulated", "Regulated Industries", "shield", [
        "Hospital staff protocols", "Medical guidelines", "Operations manuals", "Compliance docs",
        "Policy lookup", "Audit preparation", "Safety procedures", "Workspace isolation",
    ]),
    ("engineering", "Tech & Engineering", "server", [
        "Engineering runbooks", "Internal wikis", "API documentation", "Incident playbooks",
        "Dev onboarding", "Architecture docs", "OpenAPI tools", "Troubleshooting guides",
    ]),
]


def uc_tabs_html() -> str:
    tabs = []
    panels = []
    for i, (slug, label, icon, items) in enumerate(USE_CASES):
        active = " is-active" if i == 0 else ""
        hidden = "" if i == 0 else ' hidden'
        tabs.append(
            f'          <button type="button" class="uc-tab{active}" data-uc-tab="{slug}" aria-selected="{"true" if i == 0 else "false"}">{label}</button>'
        )
        lis = "\n".join(f'              <li>{ICONS["chevr"]} {item}</li>' for item in items)
        panels.append(
            f'          <div class="uc-panel{active}" data-uc-panel="{slug}"{hidden}>\n            <ul class="uc-tab-list">\n{lis}\n            </ul>\n          </div>'
        )
    return (
        '        <div class="uc-tabs reveal" data-uc-tabs>\n'
        '          <div class="uc-tablist" role="tablist">\n'
        + "\n".join(tabs)
        + "\n          </div>\n"
        '          <div class="uc-panels">\n'
        + "\n".join(panels)
        + "\n          </div>\n        </div>"
    )


def faq_schema(items=FAQ_ITEMS) -> str:
    # Keep FAQPage only on /faq (single instance). FAQ rich results are limited to
    # health/government sites and are being deprecated in 2026 — markup still helps
    # other systems understand Q&A content.
    # https://developers.google.com/search/docs/appearance/structured-data/faqpage
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": FAQ_ACCURACY_ANSWER_PLAIN if q == "How accurate are the answers?" else a,
                    },
                }
                for q, a in items
            ],
        },
        indent=2,
    )


def contact_page_json(title: str, description: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "ContactPage",
            "@id": f"{SITE}/contact#webpage",
            "url": f"{SITE}/contact",
            "name": title,
            "description": description,
            "isPartOf": {"@id": f"{SITE}/#website"},
            "about": {"@id": f"{SITE}/#organization"},
            "mainEntity": {
                "@type": "Organization",
                "@id": f"{SITE}/#organization",
            },
            "dateModified": BUILD_DATE,
            "inLanguage": "en-US",
        },
        indent=2,
    )


PAGES: dict[str, str] = {}

# ── Home ────────────────────────────────────────────────────────────
def home_faq_preview(n: int = 8) -> str:
    return "".join(
        f"""          <div class="faq-item">
            <button type="button" aria-expanded="false"><span>{q}</span><span class="faq-chevron">{ICONS["chevron"]}</span></button>
            <div class="faq-a"><p>{a}</p></div>
          </div>
"""
        for q, a in FAQ_ITEMS[:n]
    )


def home_body() -> str:
    return f"""    <section class="hero" aria-label="Hero" data-motion="hero">
      <div class="hero-grid" aria-hidden="true"></div>
      <div class="wrap-5xl hero-inner">
        <span class="eyebrow" data-motion="hero-badge">{ICONS["sparkles"]} Qefro</span>
        <h1 data-motion="hero-title">
          <span class="hero-line">The AI platform that connects</span>
          <span class="hero-accent">conversations to your business</span>
        </h1>
        <p class="hero-sub" data-motion="hero-sub">Build AI assistants that answer questions and take secure business actions.</p>
        <div class="hero-actions" data-motion="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_start_free">Start 14-Day Free Trial {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="#demo" data-open-demo data-clarity-event="cta_try_live_demo">Try Live Demo</a>
        </div>
        <div class="hero-checks" data-motion="hero-checks">
          <span>{ICONS["check"]} Customer AI · Employee AI · Admin Console</span>
          <span>{ICONS["check"]} REST/OpenAPI or Backend SDK</span>
          <span>{ICONS["check"]} Full access for 14 days · no credit card</span>
          <span>{ICONS["check"]} Web · WhatsApp · internal teams</span>
        </div>
        <p class="hero-diff" data-motion="hero-diff">Answer, act, and scale across web, WhatsApp, and internal teams — from one platform.</p>
        <p class="hero-scroll-cue" data-motion="hero-cue"><a href="#demo" data-open-demo data-clarity-event="cta_scroll_demo">Try the live demo {ICONS["arrow"]}</a></p>
      </div>
    </section>

    <section class="section-facts trust-strip" id="trust" aria-label="Trust highlights">
      <div class="wrap-5xl">
        <p class="facts-label">Why teams choose Qefro</p>
        <div class="logo-cloud" role="list">
          <span class="logo-placeholder" role="listitem">{ICONS["headphones"]} Built for modern support teams</span>
          <span class="logo-placeholder" role="listitem">{ICONS["shield"]} Secure multi-tenant architecture</span>
          <span class="logo-placeholder" role="listitem">{ICONS["server"]} Self-host or cloud</span>
          <span class="logo-placeholder" role="listitem">{ICONS["lock"]} Privacy-first AI</span>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="demo" aria-labelledby="demo-heading">
      <div class="wrap">
        <div class="demo-split reveal">
          <div class="demo-copy">
            <span class="badge badge-green">{ICONS["play"]} Live demo</span>
            <h2 id="demo-heading">Try Customer AI on this page</h2>
            <p>Open the chat bubble in the corner. Ask about the platform, workspaces, business actions, <a href="/pricing">pricing</a>, or <a href="/security">security</a>.</p>
            <div class="widget-demo-hint">
              <div class="widget-demo-card">
                <div class="widget-demo-icon">{ICONS["bot"]}</div>
                <div>
                  <strong>Live assistant is active on this page</strong>
                  <p>Answers come from Qefro&rsquo;s demo knowledge base.</p>
                </div>
              </div>
              <p class="widget-demo-suggestions">Try: <button type="button" class="demo-chip" data-open-demo data-clarity-event="demo_chip">What is Qefro?</button> · <button type="button" class="demo-chip" data-open-demo data-clarity-event="demo_chip">What are AI Workspaces?</button> · <button type="button" class="demo-chip" data-open-demo data-clarity-event="demo_chip">Is my data secure?</button></p>
            </div>
            <p class="integrations-note" style="margin-top:1.25rem">
              <a class="btn btn-primary" href="#demo" data-open-demo data-clarity-event="cta_open_live_chat">Open live chat</a>
              <a class="btn btn-ghost" href="{PORTAL_SIGNUP}" style="margin-left:0.5rem" data-clarity-event="cta_start_free">Start 14-Day Free Trial</a>
            </p>
          </div>
          <button type="button" class="demo-chat" data-open-demo data-clarity-event="cta_chat_mock" aria-label="Open live chat demo">
            <div class="chat-mock tilt-3d" data-motion="hero-float">
              <div class="chat-mock-head">
                <div class="chat-mock-avatar">{ICONS["bot"]}</div>
                <div><strong>Qefro Assistant</strong><span>AI Workspace Platform</span></div>
              </div>
              <div class="chat-mock-body" data-demo-script>
                <div class="chat-bubble ai">Hi! I connect conversations to your business — answers plus secure actions.</div>
                <div class="chat-bubble user">What makes Qefro different?</div>
                <div class="chat-bubble ai">Conversation → Knowledge → Business Tool → Action. Customer AI, Employee AI, and Admin Console on one platform.</div>
              </div>
              <div class="chat-mock-input">
                <span>Type your question…</span>
                <span class="chat-mock-send" aria-hidden="true">{ICONS["arrow"]}</span>
              </div>
            </div>
          </button>
        </div>
      </div>
    </section>

    <section class="section" id="platform" aria-labelledby="platform-heading">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Three surfaces</span>
          <h2 id="platform-heading">Customer AI. Employee AI. Admin Console.</h2>
          <p>One platform for customers, employees, and operators — shared knowledge, permissions, and business actions. <a href="/how-it-works">See how the platform works</a>.</p>
        </div>
        <div class="exp-grid reveal">
          <article class="exp-card tilt-3d">
            <div class="exp-icon">{ICONS["headphones"]}</div>
            <h3>Customer AI</h3>
            <p>Website widget and WhatsApp — answer questions, run business actions, capture leads, and hand off to humans.</p>
          </article>
          <article class="exp-card exp-card-featured tilt-3d">
            <div class="exp-icon">{ICONS["building"]}</div>
            <h3>Employee AI</h3>
            <p>Branded Internal Portal for internal teams — workspaces, conversations, documents, and source citations.</p>
          </article>
          <article class="exp-card tilt-3d">
            <div class="exp-icon">{ICONS["server"]}</div>
            <h3>Admin Console</h3>
            <p>Configure knowledge, actions, teams, branding, channels, analytics, and inbox in one place.</p>
          </article>
        </div>
        <div class="section-head reveal" style="margin-top:3rem">
          <span class="badge badge-purple">{ICONS["zap"]} How it works</span>
          <h2>From conversation to action</h2>
          <p>Every turn follows a simple path through knowledge and your business tools.</p>
        </div>
        <div class="pipeline pipeline-flow reveal" role="img" aria-label="Conversation to Knowledge to Business Tool to Action">
          <div class="pipeline-node">
            <span class="pipeline-k">01</span>
            <span class="pipeline-v">Conversation</span>
            <span class="pipeline-d">Customer or employee asks</span>
          </div>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <div class="pipeline-node">
            <span class="pipeline-k">02</span>
            <span class="pipeline-v">Knowledge</span>
            <span class="pipeline-d">Grounded retrieval &amp; citations</span>
          </div>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <div class="pipeline-node">
            <span class="pipeline-k">03</span>
            <span class="pipeline-v">Business Tool</span>
            <span class="pipeline-d">REST/OpenAPI or Backend SDK</span>
          </div>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <div class="pipeline-node pipeline-node-accent">
            <span class="pipeline-k">04</span>
            <span class="pipeline-v">Action</span>
            <span class="pipeline-d">Secure business outcome</span>
          </div>
        </div>
        <div class="section-head reveal" style="margin-top:3rem">
          <span class="badge badge-blue">{ICONS["server"]} Integrations</span>
          <h2>Two ways to connect your systems</h2>
          <p>Use the path that fits your stack — existing APIs or backend-controlled workflows.</p>
        </div>
        <div class="exp-grid reveal" style="grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))">
          <article class="exp-card tilt-3d">
            <div class="exp-icon">{ICONS["globe"]}</div>
            <h3>REST / OpenAPI</h3>
            <p>Connect existing APIs as Business Tools. Import an OpenAPI spec or configure REST endpoints — encrypted credentials, scoped per workspace.</p>
          </article>
          <article class="exp-card tilt-3d">
            <div class="exp-icon">{ICONS["lock"]}</div>
            <h3>Backend SDK</h3>
            <p>Handle authentication and workflows in your backend with the Qefro Backend SDK — identity, tool callbacks, and secure action execution.</p>
          </article>
        </div>
        <div class="arch-diagram arch-diagram-flow reveal" style="margin-top:3rem" role="img" aria-label="Admin Console configures once, then deploys Customer AI and Employee AI" data-motion="architecture">
          <div class="arch-hub">
            <span class="arch-hub-label">Admin Console</span>
            <span class="arch-hub-sub">Configure Once</span>
          </div>
          <svg class="arch-lines" data-motion="arch-lines" viewBox="0 0 320 48" fill="none" aria-hidden="true">
            <path d="M160 4 V28" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M160 28 H72 V44" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M160 28 H248 V44" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <p class="arch-flow-label">Knowledge · Actions · Permissions · Branding</p>
          <div class="arch-channels">
            <div class="arch-channel">
              <span class="arch-channel-icon">{ICONS["headphones"]}</span>
              <strong>Customer AI</strong>
              <span>Website · WhatsApp · Voice</span>
            </div>
            <div class="arch-channel arch-channel-accent">
              <span class="arch-channel-icon">{ICONS["building"]}</span>
              <strong>Employee AI</strong>
              <span>Internal Portal</span>
            </div>
          </div>
        </div>
        <div class="workspace-pills reveal" aria-label="Example AI Workspaces">
          <span class="workspace-pill">Customer Support</span>
          <span class="workspace-pill">HR</span>
          <span class="workspace-pill">IT</span>
          <span class="workspace-pill">Sales</span>
          <span class="workspace-pill">Finance</span>
          <span class="workspace-pill">Engineering</span>
        </div>
        <p class="integrations-note reveal" style="text-align:center;margin-top:1rem">Each AI Workspace has its own isolated knowledge, instructions, actions, and permissions.</p>
        <div class="product-mock-grid reveal" style="margin-top:2.5rem">
          <figure class="product-mock tilt-3d">
            <figcaption><strong>Admin Console</strong><span>Configure workspaces, knowledge, actions &amp; permissions</span></figcaption>
            <div class="mock-ui mock-console" role="img" aria-label="Illustration of the Admin Console with workspaces, knowledge, and actions">
              <div class="mock-sidebar" aria-hidden="true">
                <span class="is-active">Workspaces</span>
                <span>Knowledge</span>
                <span>Actions</span>
                <span>Members</span>
                <span>Analytics</span>
              </div>
              <div class="mock-main" aria-hidden="true">
                <div class="mock-toolbar"><strong>Customer Support</strong><em>Public workspace</em></div>
                <div class="mock-rows">
                  <div><b>Knowledge</b><span>124 docs indexed</span></div>
                  <div><b>Business actions</b><span>8 APIs connected</span></div>
                  <div><b>Permissions</b><span>Owner · Admin · Member</span></div>
                  <div><b>Channels</b><span>Widget · WhatsApp</span></div>
                </div>
              </div>
            </div>
          </figure>
          <figure class="product-mock tilt-3d">
            <figcaption><strong>Internal Portal</strong><span>Employee AI with workspaces and sources</span></figcaption>
            <div class="mock-ui mock-portal" role="img" aria-label="Illustration of the Internal Portal chat with workspace selector and sources">
              <div class="mock-sidebar" aria-hidden="true">
                <span class="is-active">HR</span>
                <span>IT Helpdesk</span>
                <span>Finance</span>
                <span>Engineering</span>
              </div>
              <div class="mock-main" aria-hidden="true">
                <div class="mock-chat">
                  <div class="mock-bubble user">What is our parental leave policy?</div>
                  <div class="mock-bubble ai">Employees are eligible for 16 weeks of parental leave…</div>
                  <div class="mock-sources">Sources: HR Handbook.pdf · Benefits FAQ</div>
                </div>
              </div>
            </div>
          </figure>
        </div>
      </div>
    </section>

{product_screenshots_html()}
    <section class="section section-alt" id="features" aria-labelledby="features-heading">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["sparkles"]} Features</span>
          <h2 id="features-heading">Knowledge, business actions, and channels</h2>
          <p>Grounded answers from your content, secure actions via REST/OpenAPI or the Backend SDK, and deployment where your people already work. <a href="/features">Explore all features</a>.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card tilt-3d">
            <h3>Business Actions</h3>
            <ul>
              <li>Powered by Business Tools</li>
              <li>REST &amp; OpenAPI import</li>
              <li>Backend SDK workflows</li>
              <li>Encrypted credentials</li>
              <li>Identity forwarding</li>
            </ul>
          </article>
          <article class="outcome-card tilt-3d">
            <h3>Knowledge Platform</h3>
            <ul>
              <li>PDF, DOCX, Markdown, TXT</li>
              <li>Website crawling &amp; OCR</li>
              <li>Multilingual retrieval</li>
              <li>Source citations</li>
              <li>Workspace-isolated bases</li>
            </ul>
          </article>
          <article class="outcome-card tilt-3d">
            <h3>Channels</h3>
            <ul>
              <li>Website widget &amp; voice</li>
              <li>Internal Portal</li>
              <li>WhatsApp (Starter+)</li>
              <li>Human handoff</li>
              <li>Lead capture</li>
            </ul>
          </article>
          <article class="outcome-card tilt-3d">
            <h3>Security controls</h3>
            <ul>
              <li>Tenant isolation</li>
              <li>Encryption at rest &amp; in transit</li>
              <li>Identity forwarding</li>
              <li>Audit &amp; execution logs</li>
              <li>Encrypted secret storage</li>
            </ul>
          </article>
        </div>
        <div class="scenario-grid reveal" style="margin-top:2.5rem">
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Customer</span> Where is my order?</p>
            <div class="scenario-flow"><span>AI calls your Order API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Live tracking returned</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Employee</span> Approve my leave request</p>
            <div class="scenario-flow"><span>AI calls your HR API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Request submitted</span></div>
          </article>
        </div>
        <p class="integrations-note reveal" style="text-align:center;margin-top:1.75rem"><a href="/security">Read the security overview</a> · <a href="/use-cases">Explore solutions</a></p>
      </div>
    </section>

    <section class="section" id="why-qefro" aria-labelledby="compare-heading">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["chart"]} Comparison</span>
          <h2 id="compare-heading">Traditional AI chatbot vs Qefro</h2>
          <p>Answering questions is table stakes. Organizations need actions, employee access, and workspace permissions.</p>
        </div>
        <div class="table-wrap reveal">
          <table class="compare-table">
            <caption class="compare-caption">Capabilities represent typical off-the-shelf AI chatbot platforms. See our <a href="/benchmark">benchmark methodology</a> for how we evaluate retrieval accuracy, grounding, and refusal behaviour.</caption>
            <thead>
              <tr>
                <th scope="col">Capability</th>
                <th scope="col">Traditional AI Chatbot</th>
                <th scope="col">Qefro</th>
              </tr>
            </thead>
            <tbody>
              <tr><td>Answers questions</td><td>✓</td><td>✓</td></tr>
              <tr><td>Company knowledge</td><td>✓</td><td>✓</td></tr>
              <tr><td>Business actions</td><td>✗</td><td>✓</td></tr>
              <tr><td>Employee portal</td><td>✗</td><td>✓</td></tr>
              <tr><td>Website widget</td><td>✓</td><td>✓</td></tr>
              <tr><td>WhatsApp</td><td>Limited</td><td>✓</td></tr>
              <tr><td>Workspace permissions</td><td>✗</td><td>✓</td></tr>
              <tr><td>Team RBAC</td><td>✗</td><td>✓</td></tr>
              <tr><td>OpenAPI integrations</td><td>Rare</td><td>✓</td></tr>
              <tr><td>Multi-workspace AI</td><td>✗</td><td>✓</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="pricing" aria-labelledby="pricing-heading">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Pricing</span>
          <h2 id="pricing-heading">Plans that scale with your organization</h2>
          <p>14-day free trial with full access. Save ~26% with yearly billing — Starter from $29/mo, Growth from $99/mo. <a href="/pricing">Full pricing details</a>.</p>
        </div>
        <div class="direct-answer reveal">
          <p>Every new organization gets a <strong>14-day free trial</strong> with full premium access (no credit card), then <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly), and custom Enterprise plans.</p>
        </div>
        <div class="billing-toggle reveal" role="group" aria-label="Billing period">
          <button type="button" data-billing="monthly" aria-pressed="false">Monthly</button>
          <button type="button" data-billing="annual" class="is-active" aria-pressed="true">Yearly <span>Save 26%</span></button>
        </div>
        <div class="price-grid reveal">
{price_cards_html(interactive=True)}
        </div>
      </div>
    </section>

    <section class="section" id="faq" aria-labelledby="faq-heading">
      <div class="wrap-narrow">
        <div class="section-head reveal">
          <h2 id="faq-heading">Frequently asked questions</h2>
          <p>Everything you need to know before you start.</p>
        </div>
        <div class="faq-list reveal">
{home_faq_preview()}
        </div>
        <p style="text-align:center;margin-top:1.5rem"><a class="btn btn-ghost" href="/faq">View all FAQ</a></p>
      </div>
    </section>

    <section class="cta-final" aria-labelledby="cta-heading">
      <div class="cta-final-glow" aria-hidden="true"></div>
      <div class="wrap-narrow reveal">
        <span class="badge badge-indigo">{ICONS["sparkles"]} Get started today</span>
        <h2 id="cta-heading">Build AI assistants that answer and act.</h2>
        <p>Start a 14-day free trial for Customer AI, Employee AI, and the Admin Console — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_start_free">Start 14-Day Free Trial {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="#demo" data-open-demo data-clarity-event="cta_try_live_demo">Try Live Demo</a>
        </div>
        <p class="integrations-note" style="margin-top:1.25rem"><a href="/contact">Talk to Sales</a> for Enterprise · <a href="{DOCS}">Documentation</a> · <a href="/benchmark">Benchmark methodology</a> · <a href="/security">Security</a></p>
      </div>
    </section>
"""


PAGES["index.html"] = page(
    title="Qefro — Connect Conversations to Your Business",
    description=(
        "Build AI assistants that answer questions and take secure business actions. "
        "Customer AI, Employee AI, and Admin Console — via REST/OpenAPI or Backend SDK."
    ),
    path="",
    jsonld=[
        ORG_JSON,
        WEBSITE_JSON,
        SOFTWARE_JSON,
        webpage_json(
            "Qefro — Connect Conversations to Your Business",
            "Build AI assistants that answer questions and take secure business actions. Customer AI, Employee AI, and Admin Console — via REST/OpenAPI or Backend SDK.",
            "",
        ),
    ],
    body=home_body(),
    extra_scripts='',
)

# Inner pages — detailed content for menu-linked pages
def features_page_content() -> str:
    return f"""        <div class="outcome-grid reveal">
          <article class="outcome-card tilt-3d"><h3>AI Workspaces</h3><ul><li>Per-team AI contexts</li><li>Isolated knowledge bases</li><li>Scoped business actions</li><li>Public &amp; private workspaces</li><li>Owner / Admin / Member RBAC</li><li>Separate conversations &amp; permissions</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Knowledge Platform</h3><ul><li>PDF, DOCX, Markdown, TXT</li><li>Website crawler</li><li>OCR for scans &amp; images</li><li>Multilingual (EN, AR, TA, HI+)</li><li>Hybrid BM25 + vector search</li><li>Source citations &amp; refusal when unsure</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Business Actions</h3><ul><li>Powered by Business Tools</li><li>REST &amp; OpenAPI import</li><li>Backend SDK for auth &amp; workflows</li><li>Encrypted API credentials</li><li>End-user identity via identify()</li><li>Execution logs &amp; schema validation</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>AI Experiences</h3><ul><li>Website widget (JWT auth)</li><li>Internal Portal for employees</li><li>WhatsApp (Starter+)</li><li>Voice STT/TTS in widget</li><li>WebSocket streaming</li><li>Handoff to human agents</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-blue">{ICONS["building"]} AI Workspaces</span>
          <h2>The mental model of Qefro</h2>
          <p>Structure organizational AI by workspace — Customer Support, HR, IT, Sales, Finance, Engineering — each with its own knowledge, instructions, business actions, and permissions.</p>
        </div>
        <div class="workspace-grid reveal">
          <article class="workspace-card"><h3>Customer Support</h3><p>Policies, order lookups, tickets, and handoff.</p></article>
          <article class="workspace-card"><h3>HR</h3><p>Handbooks, benefits, leave, and onboarding.</p></article>
          <article class="workspace-card"><h3>IT Helpdesk</h3><p>Runbooks, access requests, and SOPs.</p></article>
          <article class="workspace-card"><h3>Sales Assistant</h3><p>Product knowledge, CRM queries, and playbooks.</p></article>
          <article class="workspace-card"><h3>Finance</h3><p>Policies, approvals, and internal procedures.</p></article>
          <article class="workspace-card"><h3>Engineering</h3><p>Docs, APIs, incidents, and architecture notes.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["file"]} Knowledge</span>
          <h2>Grounded answers from your content — in any language</h2>
          <p>Upload documents or crawl your site. Qefro chunks, embeds, and indexes automatically. Every workspace has its own isolated knowledge base. Answers cite sources and refuse when nothing relevant is found.</p>
        </div>
        <div class="cap-grid reveal">
          <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>PDF &amp; DOCX ingestion</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>Multilingual RAG</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>OCR for images &amp; scans</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Hybrid retrieval</span></div>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-purple">{ICONS["zap"]} Business Actions</span>
          <h2>AI that gets work done — not just answers questions</h2>
          <p>Two integration paths: import OpenAPI or configure REST endpoints as Business Tools, or use the Backend SDK for authentication and workflows. Credentials are encrypted; outbound calls use HTTPS with SSRF protections.</p>
        </div>
        <div class="scenario-grid reveal">
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Customer</span> Where is my order #4821?</p>
            <div class="scenario-flow"><span>AI calls Order API with user JWT</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Live tracking returned</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Employee</span> Create an IT ticket</p>
            <div class="scenario-flow"><span>AI calls Helpdesk API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Ticket created with context</span></div>
          </article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-blue">{ICONS["msg"]} Experiences</span>
          <h2>Configure once. Deploy everywhere.</h2>
          <p>One Admin Console for knowledge, actions, permissions, and branding — then deploy Customer AI on website and WhatsApp, and Employee AI on a branded Internal Portal.</p>
        </div>
        <div class="dev-split reveal">
          <div class="dev-copy">
            <h3>End-user identity forwarding</h3>
            <p>Your app owns login. Forward identity with <code>identify()</code> so business actions run on behalf of signed-in users — passwords never touch Qefro.</p>
          </div>
          <pre class="code-panel" tabindex="0"><code>widget.identify({{
  id: user.id,
  email: user.email,
  auth: {{ mode: "jwt", token: userJwt }}
}});</code></pre>
        </div>"""


def how_it_works_page_content() -> str:
    return f"""        <div class="steps-grid reveal">
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">01</div></div><h3>Configure once</h3><p>In the Admin Console, create AI Workspaces, upload knowledge, set instructions, define business actions, invite teams, and set Owner / Admin / Member permissions.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">02</div></div><h3>Connect business systems</h3><p>Two paths: import OpenAPI or configure REST as Business Tools, or use the Backend SDK for authentication and workflows. Store encrypted credentials or forward end-user JWTs via identify(). Scope actions per workspace.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">03</div></div><h3>Deploy everywhere</h3><p>Launch Customer AI on website and WhatsApp, and Employee AI on a branded Internal Portal — same knowledge, actions, and permissions underneath.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">04</div></div><h3>Monitor &amp; improve</h3><p>Review conversations, analytics, and action logs. Hand off to humans when needed. Reindex documents as policies change.</p></article>
        </div>
        <div class="deploy-flow reveal" style="margin-top:3rem">
          <div class="deploy-col">
            <h3>Configure once</h3>
            <ul>
              <li>{ICONS["check"]} Knowledge</li>
              <li>{ICONS["check"]} Business actions</li>
              <li>{ICONS["check"]} Permissions</li>
              <li>{ICONS["check"]} Branding</li>
              <li>{ICONS["check"]} Workspaces</li>
            </ul>
          </div>
          <div class="deploy-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <div class="deploy-col deploy-col-accent">
            <h3>Deploy everywhere</h3>
            <ul>
              <li>{ICONS["check"]} Website widget</li>
              <li>{ICONS["check"]} WhatsApp</li>
              <li>{ICONS["check"]} Internal Portal</li>
              <li>{ICONS["check"]} Voice</li>
              <li>{ICONS["check"]} Future channels</li>
            </ul>
          </div>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>What we handle for you</h2>
          <p>No RAG pipeline to build, no LLM hosting, no embedding model management. Qefro runs retrieval, business actions, PII scrubbing, and rate limits — you focus on knowledge, APIs, and permissions.</p>
        </div>
        <div class="facts-grid reveal">
          <div class="fact"><div class="fact-v">&lt; 5 min</div><div class="fact-k">Typical widget deploy</div></div>
          <div class="fact"><div class="fact-v">WebSocket</div><div class="fact-k">Streaming responses</div></div>
          <div class="fact"><div class="fact-v">Workspaces</div><div class="fact-k">Isolated AI contexts</div></div>
          <div class="fact"><div class="fact-v">8 KB</div><div class="fact-k">Message size guardrails</div></div>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Developer integration</h2>
          <p>Register via email OTP — no password storage. For production widgets, issue short-lived JWTs from your backend or use portal-issued tokens for testing.</p>
          <ul>
            <li>REST / OpenAPI — connect existing APIs as Business Tools</li>
            <li>Backend SDK — authentication, workflows, and tool callbacks in your stack</li>
            <li>REST API for documents, conversations, and billing</li>
            <li>WebSocket chat with streaming tokens and tool-call events</li>
            <li>Widget SDK with identify(), lazy voice, and theme customization</li>
            <li>Internal Portal at yourcompany.qefro.com for employees</li>
          </ul>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Feature pages</h2>
          <p>Each capability has its own page for deeper detail — from live chat and WhatsApp to RAG, APIs, and audit logs.</p>
        </div>
        <div class="workspace-pills reveal" aria-label="Feature landing pages" style="margin-top:1rem">
{"".join(f'          <a class="workspace-pill" href="/{slug}">{escape(label)}</a>\n' for slug, label in feature_link_grid())}
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Popular topic pages</h2>
          <p>Looking for a specific keyword journey? Start here.</p>
        </div>
        <div class="workspace-pills reveal" aria-label="Topic landing pages" style="margin-top:1rem">
{"".join(f'          <a class="workspace-pill" href="/{slug}">{escape(label)}</a>\n' for slug, label in topic_link_grid())}
        </div>"""


def use_cases_page_content() -> str:
    return f"""        <div class="uc-grid reveal">
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["building"]}</div><h3>Employee AI</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Branded Internal Portal</li><li>{ICONS["chevr"]} HR, IT, Finance, Sales workspaces</li><li>{ICONS["chevr"]} Policy &amp; compliance lookup</li><li>{ICONS["chevr"]} Role-based knowledge access</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["headphones"]}</div><h3>Customer Support</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Order &amp; shipment lookups via your APIs</li><li>{ICONS["chevr"]} Refund policy with citations</li><li>{ICONS["chevr"]} Ticket creation in your helpdesk</li><li>{ICONS["chevr"]} Handoff to agents from inbox</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["shield"]}</div><h3>Regulated Industries</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Protocol &amp; guideline search</li><li>{ICONS["chevr"]} PII scrubbing in conversations</li><li>{ICONS["chevr"]} Tenant-isolated knowledge</li><li>{ICONS["chevr"]} Audit-ready execution logs</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["server"]}</div><h3>Engineering &amp; Ops</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Runbook &amp; incident playbooks</li><li>{ICONS["chevr"]} API docs + OpenAPI actions</li><li>{ICONS["chevr"]} Multilingual wiki search</li><li>{ICONS["chevr"]} Internal self-service portal</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["zap"]} Real scenarios</span>
          <h2>Knowledge plus live business actions</h2>
          <p>Every solution combines grounded document answers with optional business actions through your existing systems — powered by Business Tools.</p>
        </div>
        <div class="scenario-grid reveal">
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Employee</span> What is our parental leave policy?</p>
            <div class="scenario-flow"><span>Retrieves HR handbook</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Cited answer in employee&rsquo;s language</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Customer</span> Cancel my subscription</p>
            <div class="scenario-flow"><span>AI calls Billing API with identify()</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Cancellation confirmed</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Engineer</span> How do I roll back deploy?</p>
            <div class="scenario-flow"><span>Retrieves runbook</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Step-by-step with doc link</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Customer</span> I need a human</p>
            <div class="scenario-flow"><span>Handoff triggered</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Agent sees full thread in inbox</span></div>
          </article>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Industries</h2>
          <p>Teams in SaaS, healthcare, education, manufacturing, retail, hospitality, travel, real estate, and internal IT use Qefro to deploy organizational AI without building a platform from scratch.</p>
        </div>
        <div class="workspace-pills reveal" aria-label="Industry landing pages" style="margin-top:1rem">
{"".join(f'          <a class="workspace-pill" href="/{slug}">{escape(label)}</a>\n' for slug, label in industry_link_grid())}
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Topic pages</h2>
          <p>Explore how Qefro maps to common search intents — from RAG chatbots to WhatsApp agents.</p>
        </div>
        <div class="workspace-pills reveal" aria-label="Topic landing pages" style="margin-top:1rem">
{"".join(f'          <a class="workspace-pill" href="/{slug}">{escape(label)}</a>\n' for slug, label in topic_link_grid())}
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>AI customer support by industry</h2>
          <p>Programmatic pages for niche search intent — dental clinics, hotels, logistics, and more.</p>
        </div>
        <div class="workspace-pills reveal" aria-label="Vertical landing pages" style="margin-top:1rem">
{"".join(f'          <a class="workspace-pill" href="/{slug}">{escape(label)}</a>\n' for slug, label in vertical_link_grid())}
        </div>"""


def security_page_content() -> str:
    return f"""        <div class="trust-grid reveal">
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["bot"]}</div><h3>End-user identity forwarding</h3><p>Forward signed-in identity via <code>identify()</code> so business actions run as the real user — passwords never touch Qefro.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["lock"]}</div><h3>Zero-trust style authorization</h3><p>Business actions authorize with the end-user&rsquo;s identity by default — not a shared organization secret.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["file"]}</div><h3>Audit &amp; execution logs</h3><p>Conversation history and Business Tool runs stay attached for accountability and review.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["building"]}</div><h3>Tenant &amp; workspace isolation</h3><p>Multi-tenant by design at the database and vector store level. AI Workspaces control which knowledge and actions each experience can use.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["shield"]}</div><h3>Widget JWT auth</h3><p>Embeds load with short-lived widget tokens. Messages are bounded (8 KB), PII is scrubbed before model calls, and tenants cannot access each other&rsquo;s data.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["server"]}</div><h3>Encrypted secrets &amp; secure actions</h3><p>Business Tool credentials encrypted at rest. HTTPS-only outbound calls with SSRF protections and DNS-pinned webhooks.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>Enterprise platform controls</h2>
          <p>Built for organizational AI — not demo chat experiences.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card tilt-3d"><h3>Access control</h3><ul><li>Owner / Admin / Member RBAC</li><li>Email OTP — no password storage</li><li>Billing actions restricted to owners</li><li>Workspace-scoped documents &amp; actions</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Data handling</h3><ul><li>PII scrubbing on outbound LLM calls</li><li>Never used to train AI models</li><li>Encrypted at rest &amp; in transit</li><li>Conversation isolation</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Action execution</h3><ul><li>OpenAPI schema validation</li><li>SSRF &amp; DNS pinning for webhooks</li><li>Per-action allow-from-public-chat toggle</li><li>Execution logs for accountability</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Enterprise roadmap</h3><ul><li>SSO / SAML (roadmap)</li><li>Platform admin audit trail (roadmap)</li><li>Private deployment available today</li><li>SOC 2 program in progress</li></ul></article>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Compliance &amp; deployment</h2>
          <p>Enterprise customers can run Qefro in a private environment with dedicated support and custom SLAs. Contact sales for the current compliance roadmap and data processing terms.</p>
        </div>"""


def pricing_page_content() -> str:
    return f"""        <div class="direct-answer reveal">
          <p>Every new organization gets a <strong>14-day free trial</strong> with full premium access (no credit card), then <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly, WhatsApp + unlimited business system connections), and custom <strong>Enterprise</strong> plans.</p>
        </div>
        <div class="billing-toggle reveal" role="group" aria-label="Billing period">
          <button type="button" data-billing="monthly" aria-pressed="false">Monthly</button>
          <button type="button" data-billing="annual" class="is-active" aria-pressed="true">Yearly <span>Save 26%</span></button>
        </div>
        <div class="price-grid reveal">
{price_cards_html(interactive=False)}
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>Included on every plan</h2>
          <p>Core platform capabilities — not nickel-and-dimed add-ons.</p>
        </div>
        <div class="cap-grid reveal">
          <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>Multilingual RAG &amp; OCR</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["lock"]}</div><span>Widget JWT &amp; identify()</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["shield"]}</div><span>PII scrubbing &amp; tenant isolation</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>Source citations</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>Business actions &amp; OpenAPI</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Execution logs</span></div>
        </div>
        <div class="prose reveal" style="margin-top:2rem">
          <p>Billing is prepaid via Razorpay in the portal. Upgrade or top up anytime; owners manage subscriptions and invoices from the billing page. Also see the short answer page: <a href="/qefro-pricing">How much does Qefro cost?</a></p>
        </div>"""


def privacy_page_content() -> str:
    return f"""        <div class="prose">
          <p><strong>Last updated:</strong> {BUILD_DATE}</p>
          <p>
            This Privacy Policy explains how Qefro (&ldquo;Qefro,&rdquo; &ldquo;we,&rdquo; &ldquo;us&rdquo;) collects, uses, and shares
            information when you visit <a href="{SITE}">qefro.com</a>, use the Admin Console at
            <a href="{PORTAL_LOGIN}">app.qefro.com</a>, the Internal Portal, the website widget, WhatsApp experiences,
            or related APIs at <strong>api.qefro.com</strong>.
          </p>

          <h2>1. Who we are</h2>
          <p>
            Qefro provides an AI Workspace Platform for organizations — Customer AI, Employee AI, knowledge retrieval,
            and Business Actions. Contact: <a href="mailto:support@qefro.com">support@qefro.com</a>.
          </p>

          <h2>2. Information we collect</h2>
          <h3>Account and organization data</h3>
          <ul>
            <li>Name, work email, organization name, and authentication-related data needed to create and secure accounts</li>
            <li>Role and membership information (Owner, Admin, Member), team and workspace assignments</li>
            <li>Billing and subscription records processed via our payment provider (Razorpay), including invoices and payment status</li>
          </ul>
          <h3>Customer content (organization-controlled)</h3>
          <ul>
            <li>Documents and crawled content you upload to workspaces</li>
            <li>Assistant instructions, Business Tool configurations, and encrypted credentials you store for integrations</li>
            <li>Conversation transcripts, citations, feedback, leads captured by the widget, and tool execution logs</li>
          </ul>
          <h3>End-user identity you forward</h3>
          <p>
            If you call the widget <code>identify()</code> API, your application may send end-user identifiers
            (such as id, email, name) and authentication material (JWT or session token) so Business Actions can run
            in that user&rsquo;s context. Qefro does not replace your identity provider; you remain responsible for
            how you obtain and forward that identity.
          </p>
          <h3>Technical and usage data</h3>
          <ul>
            <li>IP address, device/browser metadata, approximate location derived from IP, and request logs</li>
            <li>Product analytics needed to operate quotas, rate limits, reliability, and abuse prevention</li>
            <li>Cookies or local storage for theme preference, session continuity, and (where enabled) marketing analytics such as Microsoft Clarity on the marketing site</li>
          </ul>

          <h2>3. How we use information</h2>
          <ul>
            <li>Provide, secure, and improve the Qefro platform</li>
            <li>Authenticate users, enforce RBAC, isolate tenants and workspaces, and prevent abuse</li>
            <li>Process payments, send transactional email (verification, invites, invoices, security notices)</li>
            <li>Generate AI answers and Business Actions using your organization&rsquo;s configured knowledge and tools</li>
            <li>Respond to support requests and legal obligations</li>
          </ul>
          <p>
            <strong>We do not use your organization&rsquo;s customer content to train foundation AI models.</strong>
            Outbound model calls may include PII scrubbing controls as described on our
            <a href="/security">Security</a> page.
          </p>

          <h2>4. Sharing</h2>
          <p>We share information only as needed to operate the service, including:</p>
          <ul>
            <li><strong>Infrastructure and subprocessors</strong> that host compute, storage, email, and related services under contract</li>
            <li><strong>Payment processors</strong> (Razorpay) for checkout and billing</li>
            <li><strong>Model / inference providers</strong> required to generate answers, subject to our security controls</li>
            <li><strong>Your own systems</strong> when Business Tools or webhooks call APIs you configure</li>
            <li><strong>Legal</strong> disclosure when required by law or to protect rights and safety</li>
          </ul>
          <p>We do not sell personal information.</p>

          <h2>5. Retention</h2>
          <p>
            We retain account, billing, conversation, and log data for as long as needed to provide the service,
            meet legal/accounting requirements, resolve disputes, and enforce agreements. Organizations may delete
            documents, members, and certain configurations from the Admin Console; contact
            <a href="mailto:support@qefro.com">support@qefro.com</a> for account closure requests.
          </p>

          <h2>6. Security</h2>
          <p>
            We use multi-tenant isolation, workspace isolation, encryption in transit, encrypted secrets for Business Tools,
            SSRF protections for outbound tool calls, and access controls described on
            <a href="/security">qefro.com/security</a>. No method of transmission or storage is 100% secure.
          </p>

          <h2>7. International transfers</h2>
          <p>
            Qefro is operated globally. Your information may be processed in countries other than where you are located.
            Enterprise customers seeking private deployment or specific data-processing terms should contact Sales.
          </p>

          <h2>8. Your choices and rights</h2>
          <p>
            Depending on your location, you may have rights to access, correct, delete, or export personal data,
            or to object to certain processing. Organization Owners/Admins control most workspace content.
            Email <a href="mailto:support@qefro.com">support@qefro.com</a> to exercise privacy requests.
            You can also stop using the service and request account deletion.
          </p>

          <h2>9. Children</h2>
          <p>Qefro is designed for business use and is not directed to children under 16.</p>

          <h2>10. Changes</h2>
          <p>
            We may update this policy. Material changes will be reflected by updating the &ldquo;Last updated&rdquo; date
            on this page and, when appropriate, notifying account Owners by email or in-product notice.
          </p>

          <h2>11. Contact</h2>
          <p>
            Privacy questions: <a href="mailto:support@qefro.com">support@qefro.com</a> ·
            <a href="/contact">Contact form</a> · Related: <a href="/terms">Terms of Service</a>,
            <a href="/security">Security</a>.
          </p>
        </div>"""


def terms_page_content() -> str:
    return f"""        <div class="prose">
          <p><strong>Last updated:</strong> {BUILD_DATE}</p>
          <p>
            These Terms of Service (&ldquo;Terms&rdquo;) govern access to and use of Qefro&rsquo;s websites, Admin Console,
            Internal Portal, website widget, WhatsApp integrations, APIs, and related services (the &ldquo;Service&rdquo;).
            By creating an account or using the Service, you agree to these Terms.
          </p>

          <h2>1. The Service</h2>
          <p>
            Qefro is an AI Workspace Platform. You configure organizations, workspaces, knowledge, Business Tools,
            and channels to deploy Customer AI and Employee AI. Features and plan limits are described on
            <a href="/pricing">Pricing</a> and in the Admin Console and may change over time.
          </p>

          <h2>2. Accounts and organizations</h2>
          <ul>
            <li>You must provide accurate registration information and keep credentials secure.</li>
            <li>Organization Owners are responsible for members, billing, and configuration under their tenant.</li>
            <li>You must be authorized to bind your company to these Terms when signing up for a business account.</li>
          </ul>

          <h2>3. Customer content and responsibilities</h2>
          <p>
            You retain ownership of content you upload or connect (&ldquo;Customer Content&rdquo;), including documents,
            instructions, conversation data generated for your organization, and integration credentials you provide.
            You grant Qefro a limited license to host, process, transmit, and display Customer Content solely to provide
            and secure the Service.
          </p>
          <p>You are responsible for:</p>
          <ul>
            <li>Having rights to the Customer Content you submit</li>
            <li>Configuring workspaces, RBAC, and Business Tools safely (including least-privilege API scopes)</li>
            <li>Compliance with laws applicable to your use (including privacy notices to your end users)</li>
            <li>Outputs you act on — AI answers and actions can be incorrect; review critical decisions</li>
          </ul>

          <h2>4. Acceptable use</h2>
          <p>You may not:</p>
          <ul>
            <li>Probe, abuse, or disrupt the Service, or bypass rate limits, quotas, or security controls</li>
            <li>Use the Service for unlawful, harmful, or infringing activity</li>
            <li>Resell the Service except as expressly permitted in writing</li>
            <li>Attempt to extract model weights or reverse engineer the Service except where prohibited by law cannot be waived</li>
            <li>Upload malware or content that creates undue risk to Qefro or other customers</li>
          </ul>

          <h2>5. AI and Business Actions</h2>
          <p>
            The Service may retrieve from your knowledge, call models, and invoke Business Tools you configure.
            Business Actions call <em>your</em> systems of record; Qefro is not your CRM/ERP. You must validate
            tool configurations, identity forwarding (<code>identify()</code>), and outbound webhook targets.
          </p>

          <h2>6. Plans, billing, and taxes</h2>
          <p>
            Paid plans are billed via Razorpay as shown in the Admin Console. Fees are generally prepaid and
            non-refundable except where required by law or expressly stated otherwise. You authorize recurring charges
            for subscriptions you enable. Taxes may apply. Failure to pay may result in suspension.
          </p>

          <h2>7. Third-party services</h2>
          <p>
            The Service may interoperate with third parties (payment, messaging, model providers, your APIs).
            Their terms and privacy policies apply to those services. Qefro is not responsible for third-party outages
            or changes outside our reasonable control.
          </p>

          <h2>8. Confidentiality and security</h2>
          <p>
            Each party will protect the other&rsquo;s confidential information with reasonable care.
            Our security practices are summarized at <a href="/security">qefro.com/security</a>.
            You must protect widget tokens, API credentials, and Admin Console access.
          </p>

          <h2>9. Privacy</h2>
          <p>
            Personal data is handled as described in our <a href="/privacy">Privacy Policy</a>.
            Enterprise DPAs are available on request via Sales / <a href="mailto:support@qefro.com">support@qefro.com</a>.
          </p>

          <h2>10. Intellectual property</h2>
          <p>
            Qefro and its licensors own the Service, branding, and underlying software. These Terms do not transfer
            ownership of Qefro IP. Feedback you provide may be used to improve the Service without obligation to you.
          </p>

          <h2>11. Disclaimers</h2>
          <p>
            THE SERVICE IS PROVIDED &ldquo;AS IS&rdquo; AND &ldquo;AS AVAILABLE.&rdquo; TO THE MAXIMUM EXTENT PERMITTED BY LAW,
            QEFRO DISCLAIMS WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
            WE DO NOT WARRANT THAT AI OUTPUTS WILL BE ACCURATE, COMPLETE, OR ERROR-FREE.
          </p>

          <h2>12. Limitation of liability</h2>
          <p>
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, QEFRO WILL NOT BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL,
            CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR FOR LOST PROFITS, REVENUE, OR DATA. QEFRO&rsquo;S AGGREGATE LIABILITY
            ARISING OUT OF THESE TERMS WILL NOT EXCEED THE AMOUNTS PAID BY YOU TO QEFRO FOR THE SERVICE IN THE
            TWELVE (12) MONTHS BEFORE THE CLAIM (OR USD $100 IF YOU ARE ON A FREE PLAN).
          </p>

          <h2>13. Indemnity</h2>
          <p>
            You will defend and indemnify Qefro against claims arising from your Customer Content, your end users,
            your Business Tool configurations, or your unlawful use of the Service.
          </p>

          <h2>14. Suspension and termination</h2>
          <p>
            You may stop using the Service at any time. We may suspend or terminate access for breach, non-payment,
            risk to the platform, or legal requirements. Upon termination, your right to use the Service ends;
            provisions that should survive (including IP, disclaimers, limitations, and indemnity) will survive.
          </p>

          <h2>15. Changes</h2>
          <p>
            We may update these Terms. Continued use after the updated &ldquo;Last updated&rdquo; date constitutes acceptance,
            except where applicable law requires additional consent.
          </p>

          <h2>16. Contact</h2>
          <p>
            Questions: <a href="mailto:support@qefro.com">support@qefro.com</a> ·
            <a href="/contact">Contact</a> · <a href="/privacy">Privacy Policy</a> ·
            <a href="/security">Security</a>.
          </p>
        </div>"""


def inner(title, h1, desc, path, active, answer, content, extra_jsonld=None, extra_sections="", badge=""):
    jl = [
        webpage_json(title, desc, path),
        breadcrumb_json([("Home", "/"), (h1, path)]),
    ]
    if extra_jsonld:
        jl.extend(extra_jsonld)
    badge_html = f'\n        <span class="badge badge-indigo">{badge}</span>' if badge else ""
    return page(
        title=title,
        description=desc,
        path=path,
        active=active,
        jsonld=jl,
        body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), (h1, "")])}
        <div class="page-hero-inner">{badge_html}
          <h1>{h1}</h1>
          <div class="direct-answer" style="text-align:left">{answer}</div>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
{content}
      </div>
    </section>
{extra_sections}
    <section class="cta-final">
      <div class="cta-final-glow" aria-hidden="true"></div>
      <div class="wrap-narrow reveal">
        <span class="badge badge-indigo">{ICONS["sparkles"]} Get started today</span>
        <h2>Deploy your company&rsquo;s AI workspace.</h2>
        <p>Start a 14-day free trial for Customer AI, Employee AI, and the Admin Console — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start 14-Day Free Trial {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="#demo" data-open-demo>Try Live Demo</a>
        </div>
        <p class="integrations-note" style="margin-top:1.25rem"><a href="/contact">Talk to Sales</a> for Enterprise · <a href="{DOCS}">Documentation</a> · <a href="/security">Security overview</a></p>
      </div>
    </section>
""",
    )


PAGES["features.html"] = inner(
    "Features | Qefro AI Workspace Platform",
    "Features",
    "Qefro AI Workspace Platform: AI Workspaces, knowledge RAG, business actions (REST/OpenAPI or Backend SDK), Customer AI, Employee AI, Admin Console, WhatsApp, voice, and RBAC.",
    "features.html",
    "features",
    "<p>Qefro combines <strong>AI Workspaces</strong>, a <strong>knowledge platform</strong>, <strong>business actions</strong>, and <strong>three surfaces</strong> — Customer AI, Employee AI, and Admin Console — so organizations can answer questions, take secure actions, and govern access from one platform.</p>",
    features_page_content(),
    badge=f'{ICONS["sparkles"]} Features',
)

PAGES["how-it-works.html"] = inner(
    "Platform | Qefro — configure once, deploy everywhere",
    "Platform",
    "How Qefro works: Conversation → Knowledge → Business Tool → Action. Connect via REST/OpenAPI or Backend SDK. Configure once in the Admin Console, deploy Customer AI and Employee AI everywhere.",
    "how-it-works.html",
    "how-it-works",
    "<p><strong>Configure once. Deploy everywhere.</strong> Four steps from Admin Console setup to production organizational AI. Connect systems via REST/OpenAPI or the Backend SDK — we handle vectors, models, PII scrubbing, and action execution.</p>",
    how_it_works_page_content(),
    badge=f'{ICONS["zap"]} Platform overview',
)

PAGES["use-cases.html"] = inner(
    "Solutions | Qefro for Customer AI, Employee AI, HR, and IT",
    "Solutions",
    "Teams use Qefro for Customer AI with live API actions, Employee AI portals for HR/IT, regulated compliance lookup, and engineering runbooks — multilingual RAG included.",
    "use-cases.html",
    "use-cases",
    "<p>Same AI Workspace Platform for customer-facing experiences and internal operations — grounded answers from docs plus optional business actions through your existing APIs.</p>",
    use_cases_page_content(),
    badge=f'{ICONS["building"]} Solutions',
)

PAGES["security.html"] = inner(
    "Security | Qefro enterprise AI Workspace Platform",
    "Security",
    "Enterprise security for organizational AI: end-user identity forwarding, zero-trust style authorization, audit logs, multi-tenant isolation, workspace RBAC, and encrypted secrets.",
    "security.html",
    "security",
    "<p>Authentication stays in your app. Qefro never stores passwords. Lead with the controls that matter: tenant isolation, encryption, identity forwarding, audit logs, and secure secret storage. SOC 2 compliance is on our roadmap — contact Sales for the current timeline.</p>",
    security_page_content(),
    badge=f'{ICONS["shield"]} Security',
)

PAGES["pricing.html"] = inner(
    "Pricing | Qefro — Trial, Starter from $29/mo, Growth from $99/mo",
    "Pricing",
    "Qefro pricing: 14-day free trial with full premium access (RAG, widget, WhatsApp, voice). Starter $29/mo annual, Growth $99/mo with WhatsApp and unlimited business system connections.",
    "pricing.html",
    "pricing",
    "<p>Start a 14-day free trial with multilingual RAG, widget JWT auth, WhatsApp, and voice. Scale to unlimited business system connections on Growth. Enterprise adds private deployment and custom SLAs.</p>",
    pricing_page_content(),
    # No FAQPage here — Google asks to mark up each FAQ only once (on /faq).
    extra_jsonld=[PRICING_OFFERS_JSON],
    badge=f'{ICONS["zap"]} Pricing',
)

faq_html = "".join(
    f"""          <div class="faq-item">
            <button type="button" aria-expanded="false"><span>{q}</span><span class="faq-chevron">{ICONS["chevron"]}</span></button>
            <div class="faq-a"><p>{a}</p></div>
          </div>
"""
    for q, a in FAQ_ITEMS
)

PAGES["faq.html"] = page(
    title="FAQ | Qefro AI Workspace Platform",
    description="FAQ about the Qefro AI Workspace Platform: pricing, accuracy, security, business actions, Internal Portal, workspaces, and setup.",
    path="faq.html",
    active="faq",
    jsonld=[
        webpage_json(
            "FAQ | Qefro AI Workspace Platform",
            "FAQ about the Qefro AI Workspace Platform: pricing, accuracy, security, business actions, Internal Portal, workspaces, and setup.",
            "faq",
        ),
        breadcrumb_json([("Home", "/"), ("FAQ", "faq")]),
        faq_schema(),
    ],
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), ("FAQ", "")])}
        <h1>Frequently Asked Questions</h1>
        <p class="hero-sub" style="margin-bottom:0">Everything you need to know before you start.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap-narrow">
        <div class="faq-list reveal">
{faq_html}
        </div>
      </div>
    </section>
""",
)

PAGES["benchmark.html"] = page(
    title="Benchmark methodology | Qefro",
    description="How Qefro measures answer accuracy: test set composition, evaluation methodology, results, and known limitations.",
    path="benchmark.html",
    jsonld=[
        webpage_json(
            "Benchmark methodology | Qefro",
            "How Qefro measures answer accuracy: test set composition, evaluation methodology, results, and known limitations.",
            "benchmark",
        ),
        breadcrumb_json([("Home", "/"), ("Benchmark Methodology", "benchmark")]),
    ],
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), ("Benchmark Methodology", "")])}
        <h1>Benchmark Methodology</h1>
        <p class="hero-sub" style="margin-bottom:0">How we measure Qefro&rsquo;s accuracy and refusal behavior.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
        <div class="section-head" style="text-align:left">
          <h2>Methodology</h2>
          <p>We evaluate Qefro on a fixed set of question&ndash;answer pairs drawn from customer-style knowledge bases (policies, product docs, FAQs). Each query is scored as <strong>correct</strong>, <strong>appropriate refusal</strong> (no relevant source), or <strong>incorrect</strong> (hallucination or wrong citation). Scores are computed per category and release.</p>
        </div>
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap reveal">
        <div class="section-head" style="text-align:left">
          <h2>Test set composition</h2>
          <p>Benchmarks include factual lookups, multi-step policy questions, out-of-scope queries, and ambiguous phrasing across English and multilingual samples. Knowledge bases range from small FAQ sets to larger document collections so results reflect real deployment sizes.</p>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
        <div class="section-head" style="text-align:left">
          <h2>Results</h2>
          <p>Published accuracy and refusal metrics are updated when we ship meaningful RAG or model changes. Contact <a href="mailto:support@qefro.com">support@qefro.com</a> for the latest benchmark report for your industry or use case.</p>
        </div>
      </div>
    </section>
    <section class="section section-alt">
      <div class="wrap reveal">
        <div class="section-head" style="text-align:left">
          <h2>Limitations</h2>
          <p>Benchmarks measure retrieval and answering behavior on curated test sets; they do not guarantee performance on every production corpus. Your content quality, chunking, and access rules materially affect live accuracy.</p>
        </div>
      </div>
    </section>
""",
)

PAGES["contact.html"] = inner(
    "Contact | Qefro sales, support, and demos",
    "Contact Qefro",
    "Book a Qefro demo or email support. Tell us about your team and we will get back within one business day.",
    "contact.html",
    None,
    '<p>Book a demo below, or email <a href="mailto:support@qefro.com"><strong>support@qefro.com</strong></a> for product help and Enterprise questions.</p>',
    f"""        <form class="contact-form glass-card" method="post" action="mailto:support@qefro.com?subject=Qefro%20demo%20request" enctype="text/plain">
          <div class="contact-grid">
            <label>Name
              <input class="input" name="name" type="text" required autocomplete="name" placeholder="Your name" />
            </label>
            <label>Work email
              <input class="input" name="email" type="email" required autocomplete="email" placeholder="you@company.com" />
            </label>
            <label>Company
              <input class="input" name="company" type="text" required autocomplete="organization" placeholder="Company name" />
            </label>
            <label>Use case
              <textarea class="input" name="use_case" rows="4" required placeholder="Where will you deploy AI — customers, employees, or both?"></textarea>
            </label>
          </div>
          <button class="btn btn-primary" type="submit">Request a demo</button>
          <p class="contact-alt">Prefer email? <a href="mailto:support@qefro.com?subject=Qefro%20demo%20request">support@qefro.com</a> · or <a href="{PORTAL_SIGNUP}">start 14-day free trial</a></p>
        </form>
        <div class="cap-grid" style="margin-top:2rem">
          <a class="cap-card" href="mailto:support@qefro.com"><div class="cap-icon">{ICONS["msg"]}</div><span>support@qefro.com</span></a>
          <a class="cap-card" href="{PORTAL_SIGNUP}"><div class="cap-icon">{ICONS["zap"]}</div><span>Start 14-day free trial</span></a>
          <a class="cap-card" href="/pricing"><div class="cap-icon">{ICONS["chart"]}</div><span>View pricing</span></a>
        </div>""",
    extra_jsonld=[
        contact_page_json(
            "Contact | Qefro sales, support, and demos",
            "Book a Qefro demo or email support. Tell us about your team and we will get back within one business day.",
        )
    ],
    badge=f'{ICONS["msg"]} Contact',
)

PAGES["privacy.html"] = page(
    title="Privacy Policy | Qefro",
    description="How Qefro collects, uses, and protects personal data across the Admin Console, Internal Portal, website widget, WhatsApp, and APIs.",
    path="privacy.html",
    active=None,
    jsonld=[
        webpage_json(
            "Privacy Policy | Qefro",
            "How Qefro collects, uses, and protects personal data across the Admin Console, Internal Portal, website widget, WhatsApp, and APIs.",
            "privacy.html",
        ),
        breadcrumb_json([("Home", "/"), ("Privacy Policy", "privacy")]),
    ],
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), ("Privacy Policy", "")])}
        <h1>Privacy Policy</h1>
        <div class="direct-answer" style="text-align:left">
          <p>How Qefro handles personal data for the marketing site, Admin Console, Internal Portal, website widget, WhatsApp, and APIs.</p>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
{privacy_page_content()}
      </div>
    </section>
""",
)

PAGES["terms.html"] = page(
    title="Terms of Service | Qefro",
    description="Terms governing use of the Qefro AI Workspace Platform, including accounts, billing, acceptable use, and liability.",
    path="terms.html",
    active=None,
    jsonld=[
        webpage_json(
            "Terms of Service | Qefro",
            "Terms governing use of the Qefro AI Workspace Platform, including accounts, billing, acceptable use, and liability.",
            "terms.html",
        ),
        breadcrumb_json([("Home", "/"), ("Terms of Service", "terms")]),
    ],
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), ("Terms of Service", "")])}
        <h1>Terms of Service</h1>
        <div class="direct-answer" style="text-align:left">
          <p>The agreement between you and Qefro for using the AI Workspace Platform and related websites.</p>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
{terms_page_content()}
      </div>
    </section>
""",
)

PAGES["404.html"] = page(
    title="Page not found — Qefro",
    description="The page you requested was not found on the Qefro website.",
    path="404.html",
    robots="noindex, nofollow",
    include_canonical=False,
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        <h1>Page not found</h1>
        <p class="hero-sub">That URL is not on our site. Try the links below or return home.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="/">Go home</a>
          <a class="btn btn-ghost" href="/faq">Read FAQ</a>
        </div>
      </div>
    </section>
""",
)

for slug, title, q, a, extra in [
    (
        "what-is-qefro.html",
        "What is Qefro? | AI Workspace Platform for Organizations",
        "What is Qefro?",
        "Qefro is the AI platform that connects conversations to your business. Build AI assistants that answer questions and take secure business actions across Customer AI, Employee AI, and the Admin Console — sharing one knowledge platform, permission system, and set of business actions.",
        "<p>Conversation → Knowledge → Business Tool → Action. Connect systems via REST/OpenAPI or the Backend SDK. Configure once in the Admin Console, then deploy Customer AI and Employee AI everywhere — with workspace-level isolation.</p>",
    ),
    (
        "qefro-pricing.html",
        "How much does Qefro cost? | Pricing overview",
        "How much does Qefro cost?",
        "Every new organization gets a 14-day free trial with full premium access. No credit card required. Starter from $29/month billed annually (connect up to 5 business systems). Growth from $99/month billed annually (unlimited business system connections). Enterprise is custom.",
        '<p>See the full comparison on the <a href="/pricing">pricing page</a>.</p>',
    ),
]:
    PAGES[slug] = page(
        title=title,
        description=a,
        path=slug,
        # No FAQPage on AEO pages — Google guidelines: mark up each FAQ only once (on /faq).
        jsonld=[
            webpage_json(title, a, slug),
            breadcrumb_json([("Home", "/"), (q, slug.removesuffix(".html"))]),
        ],
        body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), (q, "")])}
        <h1>{q}</h1>
        <div class="direct-answer"><p>{a}</p></div>
        <div class="prose" style="margin-top:1.5rem">{extra}
          <p><a class="btn btn-primary" href="{PORTAL_LOGIN}">Start 14-day free trial</a></p>
        </div>
      </div>
    </section>
""",
    )


def _related_href(slug: str) -> str:
    if slug == "docs":
        return DOCS
    return f"/{slug.removesuffix('.html')}"


def seo_landing_content(landing) -> str:
    paras = "\n".join(f"          <p>{escape(p)}</p>" for p in landing.paragraphs)
    bullets = "\n".join(
        f"            <li>{ICONS['check']} {escape(b)}</li>" for b in landing.bullets
    )
    related = ""
    if landing.related:
        pills = "\n".join(
            f'          <a class="workspace-pill" href="{_related_href(slug)}">{escape(label)}</a>'
            for slug, label in landing.related
        )
        related = f"""
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Related pages</h2>
        </div>
        <div class="workspace-pills reveal" style="justify-content:flex-start;margin-top:1rem">
{pills}
        </div>"""
    faqs = ""
    if landing.faqs:
        items = "".join(
            f"""          <div class="faq-item">
            <button type="button" aria-expanded="false"><span>{escape(q)}</span><span class="faq-chevron">{ICONS["chevron"]}</span></button>
            <div class="faq-a"><p>{escape(a)}</p></div>
          </div>
"""
            for q, a in landing.faqs
        )
        faqs = f"""
        <div class="section-head reveal" style="text-align:left;margin-top:3rem">
          <h2>FAQ</h2>
          <p>Common questions about {escape(landing.h1)}.</p>
        </div>
        <div class="faq-list reveal">
{items}        </div>"""
    return f"""        <div class="prose reveal">
{paras}
          <h2>How Qefro delivers {escape(landing.h1)}</h2>
          <p>
            Configure knowledge, instructions, and Business Tools once in the Admin Console.
            Deploy <strong>Customer AI</strong> on your website widget and WhatsApp, and
            <strong>Employee AI</strong> on a branded Internal Portal — with the same retrieval,
            permissions, and action layer underneath.
          </p>
          <p>
            Answers are grounded in your documents and crawled pages. Hybrid search combines
            keyword and vector retrieval, returns source citations, and is designed to decline
            when nothing relevant exists — so teams can trust support and internal assistants
            in production.
          </p>
          <p>
            When chat must change state — order lookups, tickets, CRM updates — connect your
            APIs via REST/OpenAPI or the Backend SDK. Credentials are encrypted; outbound calls
            use HTTPS with SSRF protections; execution logs support review and QA.
          </p>
          <h2>Why teams choose Qefro for this use case</h2>
          <p>
            You should not rebuild RAG infrastructure, hosting, or channel adapters for every
            project. Qefro gives organizations a multi-tenant AI Workspace Platform: isolated
            knowledge per workspace, RBAC for owners/admins/members, PII scrubbing on model
            calls, and a 14-day free trial with full premium access so you can prove value
            before buying.
          </p>
          <p>
            Compare plans on the <a href="/pricing">pricing page</a>, review
            <a href="/security">security controls</a>, and read the
            <a href="/benchmark">benchmark methodology</a> for how we evaluate grounding and
            refusal behavior. Product docs live at
            <a href="{DOCS}">docs.qefro.com</a>.
          </p>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:2.5rem">
          <h2>What you get with Qefro</h2>
          <p>Practical capabilities for {escape(landing.h1.lower())} — not a demo chatbot.</p>
        </div>
        <ul class="uc-list reveal" style="max-width:40rem">
{bullets}
        </ul>
        <div class="cap-grid reveal" style="margin-top:2rem">
          <div class="cap-card"><div class="cap-icon">{ICONS["shield"]}</div><span>Tenant &amp; workspace isolation</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>Source citations</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["zap"]}</div><span>Secure business actions</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>Web · WhatsApp · Internal Portal</span></div>
        </div>
{related}
{faqs}
        <p class="integrations-note reveal" style="margin-top:2rem">
          <a href="/features">All features</a> ·
          <a href="/use-cases">Solutions</a> ·
          <a href="/pricing">Pricing</a> ·
          <a href="/security">Security</a> ·
          <a href="{DOCS}">Docs</a>
        </p>"""


def register_seo_landings() -> None:
    """Generate topic, industry, feature, and vertical landing pages into PAGES."""
    vertical_pills = "\n".join(
        f'          <a class="workspace-pill" href="/{slug}">{escape(label)}</a>'
        for slug, label in vertical_link_grid()
    )
    # Dedicated hub so verticals are never orphaned from a crawl path.
    hub_path = "ai-customer-support-by-industry.html"
    PAGES[hub_path] = page(
        title="AI Customer Support by Industry | Qefro",
        description=(
            "Explore AI customer support pages by industry — clinics, hotels, universities, "
            "logistics, retail, and more — built on Qefro’s AI Workspace Platform."
        ),
        path=hub_path,
        active="use-cases",
        jsonld=[
            webpage_json(
                "AI Customer Support by Industry | Qefro",
                "Explore AI customer support pages by industry on Qefro.",
                hub_path,
            ),
            breadcrumb_json(
                [
                    ("Home", "/"),
                    ("AI customer support", "ai-customer-support"),
                    ("By industry", "ai-customer-support-by-industry"),
                ]
            ),
        ],
        body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), ("AI customer support", "/ai-customer-support"), ("By industry", "")])}
        <div class="page-hero-inner">
          <span class="badge badge-indigo">{ICONS["building"]} Industries</span>
          <h1>AI Customer Support by Industry</h1>
          <div class="direct-answer" style="text-align:left">
            <p>Choose your vertical to see how Qefro deploys grounded Customer AI, optional WhatsApp, secure API actions, and staff Internal Portals — without building RAG from scratch.</p>
          </div>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
        <div class="prose">
          <p>Each page targets a specific “AI customer support for …” search intent with scenarios, integrations, and FAQs for that niche. Start a free trial from any page when you are ready.</p>
        </div>
        <div class="workspace-pills" style="justify-content:flex-start;margin-top:1.5rem" aria-label="Industry support pages">
{vertical_pills}
        </div>
        <p class="integrations-note" style="margin-top:2rem">
          <a href="/ai-customer-support">AI customer support overview</a> ·
          <a href="/use-cases">Solutions</a> ·
          <a href="/features">Features</a> ·
          <a href="/pricing">Pricing</a>
        </p>
      </div>
    </section>
""",
    )

    for landing in all_landings():
        path = f"{landing.slug}.html"
        if landing.kind == "feature":
            crumb_nav = [("Home", "/"), ("Features", "/features"), (landing.h1, "")]
            crumb_json = [("Home", "/"), ("Features", "features"), (landing.h1, landing.slug)]
            active = "features"
            badge = f'{ICONS["sparkles"]} Feature'
        elif landing.kind == "industry":
            crumb_nav = [("Home", "/"), ("Solutions", "/use-cases"), (landing.h1, "")]
            crumb_json = [("Home", "/"), ("Solutions", "use-cases"), (landing.h1, landing.slug)]
            active = "use-cases"
            badge = f'{ICONS["building"]} Industry'
        elif landing.kind == "vertical":
            crumb_nav = [
                ("Home", "/"),
                ("AI customer support", "/ai-customer-support"),
                ("By industry", "/ai-customer-support-by-industry"),
                (landing.h1, ""),
            ]
            crumb_json = [
                ("Home", "/"),
                ("AI customer support", "ai-customer-support"),
                ("By industry", "ai-customer-support-by-industry"),
                (landing.h1, landing.slug),
            ]
            active = "use-cases"
            badge = f'{ICONS["headphones"]} Vertical'
        else:
            crumb_nav = [("Home", "/"), (landing.h1, "")]
            crumb_json = [("Home", "/"), (landing.h1, landing.slug)]
            active = None
            badge = f'{ICONS["zap"]} Topic'

        extra_hub = ""
        if landing.slug == "ai-customer-support":
            extra_hub = f"""
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>By industry</h2>
          <p>See niche pages for clinics, hotels, universities, logistics, retail, and more.</p>
          <p><a class="btn btn-ghost" href="/ai-customer-support-by-industry">Browse all industries</a></p>
        </div>
        <div class="workspace-pills reveal" style="justify-content:flex-start;margin-top:1rem" aria-label="Popular verticals">
{vertical_pills}
        </div>"""

        PAGES[path] = page(
            title=landing.title,
            description=landing.description,
            path=path,
            active=active,
            jsonld=[
                webpage_json(landing.title, landing.description, path),
                breadcrumb_json(crumb_json),
            ],
            body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs(crumb_nav)}
        <div class="page-hero-inner">
          <span class="badge badge-indigo">{badge}</span>
          <h1>{escape(landing.h1)}</h1>
          <div class="direct-answer" style="text-align:left">{landing.answer}</div>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
{seo_landing_content(landing)}
{extra_hub}
      </div>
    </section>
    <section class="cta-final">
      <div class="cta-final-glow" aria-hidden="true"></div>
      <div class="wrap-narrow reveal">
        <span class="badge badge-indigo">{ICONS["sparkles"]} Get started today</span>
        <h2>Try {escape(landing.h1)} with Qefro.</h2>
        <p>Start a 14-day free trial — Customer AI, Employee AI, and Admin Console. No credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start 14-Day Free Trial {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/ai-customer-support-by-industry">Browse industries</a>
        </div>
        <p class="integrations-note" style="margin-top:1.25rem"><a href="/contact">Talk to Sales</a> · <a href="{DOCS}">Documentation</a> · <a href="/security">Security</a></p>
      </div>
    </section>
""",
        )


# Hub must be in sitemap too.
SITEMAP_ENTRIES.append(("ai-customer-support-by-industry", []))

register_seo_landings()


def ensure_logo() -> None:
    logo = ROOT / "assets" / "images" / "qefro-logo.png"
    if logo.is_file():
        return
    portal_logo = ROOT.parent / "ai-customer-support-portal" / "src" / "assets" / "qefro-logo.png"
    if portal_logo.is_file():
        logo.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(portal_logo, logo)
        print("copied", logo.relative_to(ROOT))
        return
    print("warning: qefro-logo.png missing — add assets/images/qefro-logo.png for Organization schema")


def write_robots_txt() -> None:
    # https://developers.google.com/search/docs/crawling-indexing/robots/intro
    # Allow full crawl of HTML + CSS/JS/images so Google can render pages correctly.
    # Do not use robots.txt to hide pages — use noindex (see 404.html) instead.
    content = f"""# Qefro marketing site — https://qefro.com
# App hosts (app.qefro.com, api.qefro.com) are separate and not governed here.

User-agent: *
Allow: /

# Explicitly allow rendering resources (Google recommends not blocking these).
Allow: /assets/

# Custom 404 is not for indexing (also noindex in HTML + true HTTP 404 from nginx).
Disallow: /404
Disallow: /404.html

Sitemap: {SITE}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(content, encoding="utf-8")
    print("wrote robots.txt")


def write_sitemap_xml() -> None:
    # Canonical HTTPS URLs only. lastmod helps freshness; Google largely ignores
    # changefreq/priority so we omit them.
    # Image extension: https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps
    entries = list(SITEMAP_ENTRIES)
    # Attach product screenshots to the homepage when the full set is present
    image_dir = ROOT / "assets" / "images" / "product"
    if all((image_dir / filename).is_file() for filename, _, _ in PRODUCT_SCREENSHOTS):
        home_path, home_images = entries[0]
        product_images = [
            (
                f"{SITE}/assets/images/product/{filename}",
                f"Qefro {title}: {description}",
            )
            for filename, title, description in PRODUCT_SCREENSHOTS
        ]
        entries[0] = (home_path, list(home_images) + product_images)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for path, images in entries:
        loc = site_url(path if path else "index.html")
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        lines.append(f"    <lastmod>{BUILD_DATE}</lastmod>")
        for img_loc, img_title in images:
            lines.append("    <image:image>")
            lines.append(f"      <image:loc>{escape(img_loc)}</image:loc>")
            lines.append(f"      <image:title>{escape(img_title)}</image:title>")
            lines.append("    </image:image>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote sitemap.xml")


def build_og_image() -> None:
    svg = ROOT / "assets" / "images" / "og-cover.svg"
    png = ROOT / "assets" / "images" / "og-cover.png"
    converter = shutil.which("rsvg-convert")
    if not converter:
        if png.exists():
            print("rsvg-convert not found; keeping existing", png.name)
            return
        raise SystemExit("rsvg-convert is required to build og-cover.png from og-cover.svg")
    subprocess.run(
        [converter, "-w", "1200", "-h", "630", str(svg), "-o", str(png)],
        check=True,
    )
    print("wrote", png.relative_to(ROOT))


def write_all() -> None:
    ensure_logo()
    build_og_image()
    write_robots_txt()
    write_sitemap_xml()
    for name, html in PAGES.items():
        (ROOT / name).write_text(html, encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    write_all()
