#!/usr/bin/env python3
"""Generate Qefro static pages — portal-inspired dark design + SEO/AEO markup."""

from __future__ import annotations

import json
import re
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
ASSET_VERSION = "61"
OG_IMAGE = f"{SITE}/assets/images/og-cover.png"
OG_IMAGE_ALT = (
    "Qefro is AI-native business software for CRM, Billing, Restaurant, Real Estate, and more."
)
POSITIONING = (
    "Your business, powered by AI."
)
POSITIONING_ALT = (
    "Run your business through conversations, workflows, and automation."
)
CTA_TRIAL = "Start free"
CTA_TRIAL_SHORT = "Start free"
CTA_SEE_HOW = "Explore products"
CTA_MARKETPLACE = "Explore products"
CTA_MICRO = "AI-native business software for real-world operations."
DEMO_WIDGET_TOKEN = "wgt_729850c3-43ef-4a53-a604-870c8ded6f15"
BUILD_DATE = date.today().isoformat()
WIDGET_WELCOME = "Hello! How can I help?"
WIDGET_PRIMARY_COLOR = "#7c3aed"
WIDGET_WORKSPACE_ID = "ef7afd02-2db8-4453-a894-1ed44f3f42cd"
# Matches the default (light) page theme so first load doesn't re-theme/re-mount the widget.
WIDGET_THEME = "light"
# Used only for schema.org "keywords" in JSON-LD — the <meta name="keywords"> tag
# is deliberately not emitted (Google has ignored it since 2009).
META_KEYWORDS = (
    "AI Business Platform, AI business automation, AI business apps, "
    "AI agents for business operations, WhatsApp business AI, "
    "customer conversations, workflows, Qefro"
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
    "utensils": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 002-2V2M7 2v20M21 15V2c-2.5 0-5 2-5 5v6c0 1.1.9 2 2 2h3zm0 0v7"/></svg>',
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>',
    "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>',
    "kanban": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18M15 3v10"/></svg>',
    "shopping": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>',
    "target": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
}

for _name, _svg in list(ICONS.items()):
    ICONS[_name] = _svg.replace(
        "<svg ",
        '<svg class="icon" width="20" height="20" aria-hidden="true" ',
        1,
    )

NAV = [
    ("how-it-works", "How It Works"),
    ("business-apps", "Apps"),
    ("pricing", "Pricing"),
    ("faq", "FAQ"),
]

# Canonical indexable URLs for sitemap (extensionless; nginx 301s .html → these).
# Images listed here are included via the image sitemap extension.
SITEMAP_ENTRIES: list[tuple[str, list[tuple[str, str]]]] = [
    ("", [
        (f"{SITE}/assets/images/og-cover.png", "Qefro — AI Business Platform that turns conversations into outcomes"),
    ]),
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
    ("business-flows", []),
    ("business-tools", []),
    ("workflow-engine", []),
    ("sdk", []),
    ("openapi", []),
    ("enterprise", []),
    ("partners", []),
    ("whatsapp", []),
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
    og_type: str = "website",
) -> str:
    url = site_url(path)
    # Absolute HTTPS canonicals only — Google prefers absolute URLs for rel=canonical
    canonical = f'  <link rel="canonical" href="{url}" />\n' if include_canonical else ""
    page_og_alt = escape(OG_IMAGE_ALT if path in {"", "index.html"} else f"Qefro — {title}")
    return f"""  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}" />
  <meta name="robots" content="{robots}" />
  <meta name="googlebot" content="{robots}" />
  <meta name="author" content="Qefro" />
  <meta name="format-detection" content="telephone=no" />
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#080a12" media="(prefers-color-scheme: dark)" />
  <meta name="theme-color" content="#ffffff" id="theme-color-meta" />
  <script>
    (function () {{
      try {{
        var saved = localStorage.getItem("theme");
        if (saved === "dark") document.documentElement.setAttribute("data-theme", "dark");
      }} catch (e) {{ /* storage blocked (privacy mode) — default theme */ }}
    }})();
  </script>
{canonical}  <link rel="alternate" type="text/plain" href="{SITE}/llms.txt" title="LLM-readable summary" />
  <link rel="alternate" type="text/plain" href="{SITE}/llms-full.txt" title="Full LLM documentation digest" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="Qefro" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(description)}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{OG_IMAGE}" />
  <meta property="og:image:secure_url" content="{OG_IMAGE}" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{page_og_alt}" />
  <meta property="og:locale" content="en_US" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:site" content="@qefro" />
  <meta name="twitter:title" content="{escape(title)}" />
  <meta name="twitter:description" content="{escape(description)}" />
  <meta name="twitter:image" content="{OG_IMAGE}" />
  <meta name="twitter:image:alt" content="{page_og_alt}" />
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
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@500;600&family=Source+Serif+4:opsz,wght@8..60,600;8..60,700&display=swap" rel="stylesheet" />
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
        <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro logo" width="40" height="40" decoding="async" fetchpriority="high" />
        <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" decoding="async" />
      </a>
      <nav class="nav-links" aria-label="Primary">
{chr(10).join(links)}
        <a href="{DOCS}" rel="noopener noreferrer">Docs</a>
      </nav>
      <div class="nav-cta">
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to dark mode">
          <span class="icon-moon" aria-hidden="true">{ICONS["moon"]}</span>
          <span class="icon-sun" aria-hidden="true">{ICONS["sun"]}</span>
        </button>
        <a class="btn-link" href="{PORTAL_LOGIN}">Sign In</a>
        <a class="btn btn-primary" href="{PORTAL_SIGNUP}">{CTA_TRIAL_SHORT} {ICONS["arrow"]}</a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav-panel">{ICONS["menu"]}</button>
      </div>
    </div>
    <div class="mobile-panel wrap" id="mobile-nav-panel">
{mobile}
      <a href="{DOCS}" rel="noopener noreferrer">Docs</a>
      <a href="{PORTAL_LOGIN}">Sign In</a>
      <a class="btn btn-primary" href="{PORTAL_SIGNUP}">{CTA_TRIAL_SHORT} {ICONS["arrow"]}</a>
    </div>
  </header>"""


def widget_embed(theme: str | None = None) -> str:
    theme = theme or WIDGET_THEME
    return f"""  <script id="qefro-widget-script"
    src="{WIDGET_CDN}"
    defer
    data-token="{DEMO_WIDGET_TOKEN}"
    data-endpoint="{API}"
    data-theme="{theme}"
    data-position="bottom-right"
    data-primary-color="{WIDGET_PRIMARY_COLOR}"
    data-welcome-message="{WIDGET_WELCOME}"
    data-workspace-id="{WIDGET_WORKSPACE_ID}"></script>"""


def page_scripts(extra: str = "") -> str:
    return f"""{widget_embed()}
  <script src="/assets/js/main.js?v={ASSET_VERSION}" defer></script>
  <script src="/assets/js/qefro-ref.js?v={ASSET_VERSION}" defer></script>
  <script type="module" src="/assets/js/qefro-motion.js?v={ASSET_VERSION}"></script>{extra}"""


def footer() -> str:
    return f"""  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div class="footer-brand">
          <a class="brand" href="/" aria-label="Qefro home">
            <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro logo" width="40" height="40" decoding="async" />
            <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" decoding="async" />
          </a>
          <p class="footer-tagline">Your business, powered by AI.</p>
        </div>
        <nav class="footer-col" aria-label="Applications">
          <h3>Apps</h3>
          <a href="/business-apps">Marketplace</a>
          <a href="/business-apps">Real Estate Pro</a>
          <a href="/business-apps">Restaurant Pro</a>
          <a href="/business-apps">Clinic Pro</a>
          <a href="/sdk">SDK</a>
        </nav>
        <nav class="footer-col" aria-label="Platform">
          <h3>Platform</h3>
          <a href="/#outcomes">Outcomes</a>
          <a href="/#act">AI that acts</a>
          <a href="/#channels">Channels</a>
          <a href="/whatsapp">WhatsApp</a>
          <a href="/#control">Control</a>
        </nav>
        <nav class="footer-col" aria-label="Resources">
          <h3>Resources</h3>
          <a href="/how-it-works">How It Works</a>
          <a href="/pricing">Pricing</a>
          <a href="/faq">FAQ</a>
          <a href="/security">Security</a>
          <a href="{DOCS}">Docs</a>
          <a href="/contact">Contact</a>
        </nav>
        <nav class="footer-col" aria-label="Company">
          <h3>Company</h3>
          <a href="/contact">About</a>
          <a href="/privacy">Privacy</a>
          <a href="/terms">Terms</a>
          <a href="/llms.txt">llms.txt</a>
        </nav>
      </div>
      <div class="footer-bottom">
        <p>&copy; <span data-year></span> Qefro. All rights reserved.</p>
        <p>{escape(POSITIONING)}</p>
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
    og_type: str = "website",
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
{meta_block(title, description, path, robots=robots, include_canonical=include_canonical, og_type=og_type)}
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


def speakable_json(path: str) -> str:
    """SpeakableSpecification for AEO / voice / AI answer extraction."""
    url = site_url(path)
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".quick-answer-card", ".direct-answer", ".hero-sub", "h1"],
            },
        },
        indent=2,
    )


def howto_json(path: str = "how-it-works.html") -> str:
    """HowTo schema for platform setup and deployment steps."""
    url = site_url(path)
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "How to Connect, Build, and Automate with Qefro",
            "description": "Step-by-step guide to connecting systems, installing apps, enabling channels, and automating Organization Workflows.",
            "url": url,
            "step": [
                {
                    "@type": "HowToStep",
                    "position": 1,
                    "name": "Connect systems or install apps",
                    "text": "Register an External SDK Connection, import REST/OpenAPI tools, or install a Managed Marketplace App into a workspace.",
                    "url": f"{url}#step-1",
                },
                {
                    "@type": "HowToStep",
                    "position": 2,
                    "name": "Configure workspaces, teams, and RBAC",
                    "text": "Set organization and workspace boundaries for apps, knowledge, tools, teams, and role-based access.",
                    "url": f"{url}#step-2",
                },
                {
                    "@type": "HowToStep",
                    "position": 3,
                    "name": "Enable channels and Organization Workflows",
                    "text": "Deploy Website, WhatsApp, Internal Portal, and API channels — then automate events, approvals, and tasks across teams.",
                    "url": f"{url}#step-3",
                },
            ],
        },
        indent=2,
    )


def tech_article_json(title: str, description: str, path: str) -> str:
    """TechArticle schema for deep technical overview and benchmark pages."""
    url = site_url(path)
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "@id": f"{url}#article",
            "headline": title,
            "description": description,
            "url": url,
            "inLanguage": "en-US",
            "datePublished": "2024-01-01",
            "dateModified": BUILD_DATE,
            "author": {"@id": f"{SITE}/#organization"},
            "publisher": {"@id": f"{SITE}/#organization"},
            "mainEntityOfPage": url,
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
            "Qefro is AI-native business software. Businesses run CRM, Billing, "
            "Restaurant, Real Estate, Clinic, HR and more through conversations, "
            "workflows, and automation."
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
            "AI Business Platform",
            "AI business automation",
            "AI business apps",
            "AI agents for business operations",
            "WhatsApp business AI",
            "Customer conversations to completed work",
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
            "Qefro is AI-native business software. Run your business through "
            "conversations, workflows, and automation."
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
            "Qefro is AI-native business software for CRM, Billing, Restaurant, "
            "Real Estate, Clinic, HR and more. Run your business through conversations, "
            "workflows, and automation."
        ),
        "keywords": META_KEYWORDS,
        "author": {"@id": f"{SITE}/#organization"},
        "publisher": {"@id": f"{SITE}/#organization"},
        "offers": {
            "@type": "Offer",
            "price": 0,
            "priceCurrency": "INR",
            "availability": "https://schema.org/InStock",
            "url": f"{SITE}/pricing",
            "description": "14-day free trial, then Starter, Pro, or Growth",
        },
        "featureList": [
            "AI-native business software for CRM, Billing, Restaurant, Real Estate, Clinic, HR and more",
            "Run your business through conversations, workflows, and automation",
            "Business applications with AI built into every workflow",
            "WhatsApp, Instagram, website, and portal channels",
            "Automated follow-ups, invoicing, and business events",
            "Permissions, approvals, and people in the loop",
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
            "Connect workspaces, conversations, integrations, and automation "
            "on Qefro — AI business software built for your industry."
        ),
        "brand": {"@type": "Brand", "name": "Qefro"},
        "offers": [
            {
                "@type": "Offer",
                "name": "Trial (14 Days)",
                "price": 0,
                "priceCurrency": "INR",
                "description": "Full access for 14 days. Then choose Starter, Pro, or Growth.",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
            {
                "@type": "Offer",
                "name": "Starter",
                "price": 699,
                "priceCurrency": "INR",
                "description": "1 user, 500 CRM customers. Upgrade to Pro for more users.",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
            {
                "@type": "Offer",
                "name": "Pro",
                "price": 1499,
                "priceCurrency": "INR",
                "description": "Up to 5 users, 2,500 CRM customers.",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
            {
                "@type": "Offer",
                "name": "Growth",
                "price": 2999,
                "priceCurrency": "INR",
                "description": "Up to 15 users, 10,000 CRM customers, unlimited integrations.",
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
    "AI usage is included with rate limits for abuse protection. "
    "Marketplace apps are billed separately."
    "</p>"
)

ENTERPRISE_FAIR_USE_NOTE = (
    '<p class="price-desc price-fair-use">'
    "Enterprise is a custom contract — users, CRM customers, documents, storage, SSO, and private deploy. "
    'Contact <a href="/contact">Sales</a> for a quotation.'
    "</p>"
)


def price_feat(text: str, meta: str | None = None) -> str:
    """Feature row with check icon; keep text in a body so the icon never orphans on wrap."""
    body = text if meta is None else f'{text} <span class="price-meta">{meta}</span>'
    return f'<li>{ICONS["check"]}<span class="price-feat-body">{body}</span></li>'


def price_cards_html(*, interactive: bool = False) -> str:
    """Shared Trial / Starter / Pro / Growth / Enterprise cards for homepage + /pricing."""
    cta = ' data-price-cta' if interactive else ""
    clarity = (
        lambda event: f' data-clarity-event="{event}"' if interactive else ""
    )
    return f"""          <article class="price-card{cta}" data-plan-slug="trial">
            <h3>Trial (14 Days)</h3>
            <p class="price-best">Best for evaluating the platform</p>
            <div class="price-amount">₹0</div>
            <p class="price-desc">14 days free. Explore Qefro with your business.</p>
            <ul class="price-feats">
              {price_feat("Full premium access for 14 days")}
              {price_feat("Users, CRM, WhatsApp &amp; Voice AI")}
              {price_feat("Knowledge base, crawler &amp; uploads")}
              {price_feat("Marketplace apps billed separately")}
              {price_feat("Then choose a paid plan")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_start_free")}>{CTA_TRIAL}</a>
          </article>
          <article class="price-card{cta}" data-plan-slug="starter">
            <h3>Starter</h3>
            <p class="price-best">Best for a first operator</p>
            <div class="price-amount" data-price-annual="₹582" data-price-monthly="₹699" data-quote-amount>₹699 <span>/month</span></div>
            <p class="price-billed">billed annually · or ₹699/mo monthly</p>
            <p class="price-desc">1 user · 500 CRM customers</p>
            <ul class="price-feats">
              {price_feat("1 user")}
              {price_feat("500 CRM customers")}
              {price_feat("50 documents")}
              {price_feat("5 integrations")}
              {price_feat("Widget + WhatsApp + CRM")}
              {price_feat("Marketplace billed separately")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>{CTA_TRIAL}</a>
          </article>
          <article class="price-card is-popular{cta}" data-plan-slug="pro">
            <div class="price-pop">{ICONS["star"]} Most Popular</div>
            <h3>Pro</h3>
            <p class="price-best">Best for a working team</p>
            <div class="price-amount" data-price-annual="₹1,249" data-price-monthly="₹1,499" data-quote-amount>₹1,499 <span>/month</span></div>
            <p class="price-billed">billed annually · or ₹1,499/mo monthly</p>
            <p class="price-desc">Up to 5 users · 2,500 CRM customers</p>
            <ul class="price-feats">
              {price_feat("Up to 5 users")}
              {price_feat("2,500 CRM customers")}
              {price_feat("200 documents")}
              {price_feat("25 integrations")}
              {price_feat("Voice AI, analytics &amp; handoff")}
              {price_feat("API, webhooks &amp; permissions")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>{CTA_TRIAL}</a>
          </article>
          <article class="price-card{cta}" data-plan-slug="growth">
            <h3>Growth</h3>
            <p class="price-best">Best for growing companies</p>
            <div class="price-amount" data-price-annual="₹2,499" data-price-monthly="₹2,999" data-quote-amount>₹2,999 <span>/month</span></div>
            <p class="price-billed">billed annually · or ₹2,999/mo monthly</p>
            <p class="price-desc">Up to 15 users · 10,000 CRM customers</p>
            <ul class="price-feats">
              {price_feat("Up to 15 users")}
              {price_feat("10,000 CRM customers")}
              {price_feat("Customer 360 &amp; reporting")}
              {price_feat("Unlimited integrations")}
              {price_feat("Multiple teams")}
              {price_feat("Priority support")}
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>{CTA_TRIAL}</a>
          </article>
          <article class="price-card{cta}" data-plan-slug="enterprise">
            <h3>Enterprise</h3>
            <p class="price-best">Best for regulated organizations</p>
            <div class="price-amount">Custom</div>
            <p class="price-desc">Users, customers, SSO, private deploy</p>
            <ul class="price-feats">
              {price_feat("Custom users &amp; CRM customers")}
              {price_feat("Custom documents &amp; storage")}
              {price_feat("SSO &amp; private deployment")}
              {price_feat("Dedicated CSM")}
              {price_feat("Custom SLA")}
              {price_feat("Marketplace billed separately")}
            </ul>
            {ENTERPRISE_FAIR_USE_NOTE}
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
          <p>Inbox, website chat, knowledge, and workspace controls — the surfaces your team actually uses.</p>
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
        "Qefro is an AI Business Platform. Businesses run customer-facing work and "
        "operations through AI using actual business data, apps, workflows, automations, "
        "and people — so customers get answers and work actually gets done.",
    ),
    ("How much does Qefro cost?", "Every new organization starts with a 14-day free trial. After the trial, choose a paid plan: Starter ₹699/month for 1 user, Pro ₹1,499/month for 5 users, or Growth ₹2,999/month for 15 users. Marketplace apps are billed separately. Enterprise is custom."),
    ("What types of content can I upload?", "PDFs, Word documents, Markdown, plain text — or crawl entire websites automatically. Every workspace has its own isolated knowledge base with source citations when answering."),
    ("How accurate are the answers?", FAQ_ACCURACY_ANSWER_HTML),
    (
        "Is my data secure?",
        "Qefro provides tenant isolation and workspace isolation, encryption at rest and in transit, "
        "end-user identity forwarding for tool authorization, "
        "audit and execution logs, and encrypted storage for API secrets. End-user passwords are never stored, "
        "and your data is never used to train AI models. Private deployment is available for Enterprise. "
        "SOC 2 compliance is on our roadmap. Contact Sales for our current timeline.",
    ),
    (
        "Can Qefro take action in my systems?",
        "Yes. Qefro can look up live business information and take authorized actions — "
        "book a viewing, start a collection, confirm an appointment — then follow up until the work is complete. "
        "People stay in the loop for approvals when you want them.",
    ),
    (
        "How long does setup take?",
        "Most teams embed the website widget in under 5 minutes. Connecting business systems and "
        "rolling out the Internal Portal depends on your APIs and knowledge prep — "
        "typically a day or less for straightforward integrations.",
    ),
    (
        "Can I use this for employees as well as customers?",
        "Yes. Customer-facing channels (website and WhatsApp) and employee Internal Portal share the same applications, tools, and workspace permissions — Customer Hub keeps context available to your teams.",
    ),
    ("Do you offer enterprise pricing?", "Yes. Enterprise is a custom contract — users, CRM customers, documents, storage, SSO, and private deployment are quoted to your needs — plus dedicated support and SLAs. Talk to sales about your timeline."),
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
        "Configure once, deploy everywhere: website widget (voice on Pro+), public chat pages, "
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


def faq_item_html(q: str, a: str, prefix: str, index: int, *, raw: bool = True) -> str:
    """Accordion item with button↔panel ARIA pairing. raw=False escapes plain-text q/a."""
    q_html = q if raw else escape(q)
    a_html = a if raw else escape(a)
    return f"""          <div class="faq-item">
            <button type="button" id="{prefix}-q{index}" aria-expanded="false" aria-controls="{prefix}-a{index}"><span>{q_html}</span><span class="faq-chevron">{ICONS["chevron"]}</span></button>
            <div class="faq-a" id="{prefix}-a{index}" role="region" aria-labelledby="{prefix}-q{index}"><p>{a_html}</p></div>
          </div>
"""


def pill_cloud(items, label: str, *, ul_class: str = "") -> str:
    """Pill cloud with real list semantics; wrapped in a labelled nav when items are links.

    items: iterable of (href, text) — pass href="" for a static (non-link) pill.
    """
    items_html = "\n".join(
        (
            f'          <li><a class="workspace-pill" href="{href}">{escape(text)}</a></li>'
            if href
            else f'          <li class="workspace-pill">{escape(text)}</li>'
        )
        for href, text in items
    )
    ul = f'<ul class="workspace-pills{ul_class}">\n{items_html}\n        </ul>'
    if any(href for href, _ in items):
        return f'<nav aria-label="{escape(label)}">\n        {ul}\n      </nav>'
    return f'{ul}<!-- static pill list: {escape(label)} -->'


# ── Home ────────────────────────────────────────────────────────────
_ILLUST_DIR = ROOT / "assets" / "images" / "illustrations"
_ILLUST_CACHE: dict[str, str] = {}


def illustration(name: str, *, alt: str = "", figure_class: str = "illust") -> str:
    """Inline an enterprise-diagram SVG so CSS can theme light/dark."""
    if name not in _ILLUST_CACHE:
        path = _ILLUST_DIR / f"{name}.svg"
        if not path.is_file():
            raise FileNotFoundError(f"Missing illustration: {path}")
        _ILLUST_CACHE[name] = path.read_text(encoding="utf-8").strip()
    svg = _ILLUST_CACHE[name]
    label = f' aria-label="{escape(alt)}"' if alt else ' aria-hidden="true"'
    return f'<figure class="{figure_class}" role="img"{label}>\n{svg}\n        </figure>'


def hero_visual() -> str:
    return f"""        <figure class="hero-demo" data-motion="hero-visual" aria-label="Product demo: customer searches for a 2BHK apartment, Qefro returns results with a property card, and books a viewing.">
          <div class="hero-demo-chrome">
            <span class="hero-demo-dots" aria-hidden="true"></span>
            <span class="hero-demo-title">Qefro · Real Estate</span>
            <span class="hero-demo-meta">Live demo</span>
          </div>
          <div class="hero-demo-body">
            <div class="hero-demo-convo">
              <div class="demo-msg demo-customer" data-hero-msg>
                <span class="demo-avatar demo-avatar-customer" aria-hidden="true">C</span>
                <div class="demo-bubble demo-bubble-in">
                  <p>Do you have 2BHK apartments in Ramanathapuram under &#x20B9;40L?</p>
                </div>
              </div>
              <div class="demo-msg demo-qefro" data-hero-msg>
                <span class="demo-avatar demo-avatar-qefro" aria-hidden="true">Q</span>
                <div class="demo-bubble demo-bubble-out">
                  <p>I found 6 properties matching your criteria.</p>
                  <div class="demo-property-card">
                    <div class="demo-property-img" aria-hidden="true"></div>
                    <div class="demo-property-info">
                      <strong>2BHK Apartment</strong>
                      <span class="demo-property-price">&#x20B9;36.5L</span>
                      <span class="demo-property-meta">Ramanathapuram &middot; 1,240 sq.ft</span>
                    </div>
                    <div class="demo-property-actions">
                      <button class="demo-btn demo-btn-ghost" type="button">View property</button>
                      <button class="demo-btn demo-btn-primary" type="button">Book viewing</button>
                    </div>
                  </div>
                </div>
              </div>
              <div class="demo-msg demo-customer" data-hero-msg>
                <span class="demo-avatar demo-avatar-customer" aria-hidden="true">C</span>
                <div class="demo-bubble demo-bubble-in">
                  <p>Book tomorrow at 4 PM.</p>
                </div>
              </div>
              <div class="demo-msg demo-qefro" data-hero-msg>
                <span class="demo-avatar demo-avatar-qefro" aria-hidden="true">Q</span>
                <div class="demo-bubble demo-bubble-out">
                  <p>Done. Your viewing is scheduled for tomorrow at 4:00 PM.</p>
                  <div class="demo-confirmation">
                    {ICONS["check"]} Viewing confirmed &middot; Tomorrow 4:00 PM
                  </div>
                </div>
              </div>
            </div>
          </div>
        </figure>"""


def architecture_visual(*, label: str = "Qefro connects business software to customers") -> str:
    apps = "".join(
        f"<span>{name}</span>"
        for name in ("ERP", "CRM", "Restaurant", "Hospital", "Custom App")
    )
    return f"""        <div class="qefro-arch" role="img" aria-label="{escape(label)}">
          <p class="qefro-arch-kicker">Your business software</p>
          <div class="qefro-arch-apps">{apps}</div>
          <div class="qefro-arch-down" aria-hidden="true"></div>
          <div class="qefro-arch-hub"><strong>QEFRO</strong><span>AI business software</span></div>
          <div class="qefro-arch-down" aria-hidden="true"></div>
          <div class="qefro-arch-layers">
            <span>AI Chat</span>
            <span>CRM</span>
            <span>Automation</span>
          </div>
          <div class="qefro-arch-down" aria-hidden="true"></div>
          <div class="qefro-arch-customers">
            <strong>Your customers</strong>
            <span>WhatsApp · Chat · Voice</span>
          </div>
        </div>"""


def convo_example(customer: str, qefro: str) -> str:
    return f"""          <article class="convo-card">
            <p class="convo-who">Customer</p>
            <p class="convo-bubble convo-in">{customer}</p>
            <p class="convo-who">Qefro</p>
            <p class="convo-bubble convo-out">{qefro}</p>
          </article>"""


def home_body() -> str:
    return f"""    <!-- 1. HERO -->
    <section class="hero hero-platform" aria-label="Hero" data-motion="hero">
      <div class="hero-grid" aria-hidden="true"></div>
      <div class="wrap-hero hero-platform-grid">
        <div class="hero-copy">
          <span class="eyebrow" data-motion="hero-badge">{ICONS["sparkles"]} AI-native business software</span>
          <h1 data-motion="hero-title">
            <span class="hero-line">Your business,</span>
            <span class="hero-line hero-accent">powered by AI.</span>
          </h1>
          <p class="hero-sub" data-motion="hero-sub">Run your business through conversations, workflows, and automation.</p>
          <p class="hero-sub-extra">Qefro gives businesses focused software for CRM, Billing, Restaurant, Real Estate, Clinic, HR and more&mdash;with AI built into the work, not bolted onto it.</p>
          <div class="hero-actions" data-motion="hero-actions">
            <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_start_free">Start free {ICONS["arrow"]}</a>
            <a class="btn btn-ghost btn-lg" href="#products" data-clarity-event="cta_explore_products">Explore products</a>
          </div>
          <p class="hero-micro" data-motion="hero-checks">AI-native business software for real-world operations.</p>
        </div>
{hero_visual()}
      </div>
    </section>

    <!-- 3. NOT ANOTHER CHATBOT -->
    <section class="section" id="not-chatbot" aria-labelledby="not-chatbot-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="not-chatbot-heading">AI that actually gets business done.</h2>
          <p>Most AI tools answer questions. Qefro can understand a request, use business capabilities, execute the operation, and keep the workflow moving.</p>
        </div>
        <ol class="act-chain reveal">
          <li>Ask</li>
          <li>Understand</li>
          <li>Execute</li>
          <li>Update business</li>
          <li>Trigger automation</li>
          <li>Follow through</li>
        </ol>
        <div class="not-chatbot-examples reveal">
          <article class="ncc-card">
            <p class="ncc-label">Restaurant</p>
            <p class="ncc-ask">&ldquo;Book a table for 4 tomorrow at 7.&rdquo;</p>
            <p class="ncc-result">{ICONS["check"]} Table reserved. Confirmation sent.</p>
          </article>
          <article class="ncc-card">
            <p class="ncc-label">Billing</p>
            <p class="ncc-ask">&ldquo;Show me unpaid invoices.&rdquo;</p>
            <p class="ncc-result">{ICONS["check"]} 14 outstanding &middot; &#x20B9;2.1L. Follow-ups ready.</p>
          </article>
          <article class="ncc-card">
            <p class="ncc-label">Real Estate</p>
            <p class="ncc-ask">&ldquo;Schedule a viewing for this property tomorrow.&rdquo;</p>
            <p class="ncc-result">{ICONS["check"]} Viewing scheduled. Owner notified.</p>
          </article>
        </div>
      </div>
    </section>

    <!-- 4. ONE PLATFORM. MANY BUSINESSES. -->
    <section class="section section-alt" id="products" aria-labelledby="products-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="products-heading">One platform. Many businesses.</h2>
          <p>Choose the business software you need. Every Qefro product is built on the same AI-native foundation.</p>
        </div>
        <div class="products-grid reveal">
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["building"]}</span>
            <h3>Qefro CRM</h3>
            <p>Leads, customers, deals and follow-ups.</p>
          </a>
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["file"]}</span>
            <h3>Qefro Billing</h3>
            <p>Invoices, payments and automated follow-ups.</p>
          </a>
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["utensils"]}</span>
            <h3>Qefro Restaurant</h3>
            <p>Menu, orders, tables and POS.</p>
          </a>
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["home"]}</span>
            <h3>Qefro Real Estate</h3>
            <p>Properties, leads, viewings and agents.</p>
          </a>
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["heart"]}</span>
            <h3>Qefro Clinic</h3>
            <p>Patients, appointments and prescriptions.</p>
          </a>
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["users"]}</span>
            <h3>Qefro HR</h3>
            <p>Employees, attendance, leave and payroll.</p>
          </a>
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["kanban"]}</span>
            <h3>Qefro Project</h3>
            <p>Projects, tasks, sprints and time.</p>
          </a>
          <a class="product-card" href="/business-apps">
            <span class="product-card-icon" aria-hidden="true">{ICONS["shopping"]}</span>
            <h3>Qefro E-commerce</h3>
            <p>Products, orders and customers.</p>
          </a>
        </div>
      </div>
    </section>

    <!-- 5. BUSINESS COMMAND CHAT -->
    <section class="section" id="command-chat" aria-labelledby="command-chat-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="command-chat-heading">Ask your business anything.</h2>
          <p>Your business data is only a conversation away.</p>
        </div>
        <div class="command-chat-demo reveal">
          <div class="cc-thread">
            <div class="cc-msg cc-user">
              <span class="cc-avatar" aria-hidden="true">You</span>
              <div class="cc-bubble cc-in">What were our sales this month?</div>
            </div>
            <div class="cc-msg cc-qefro">
              <span class="cc-avatar cc-avatar-q" aria-hidden="true">Q</span>
              <div class="cc-bubble cc-out">
                <div class="cc-stat-card">
                  <strong class="cc-stat-value">&#x20B9;8,42,600</strong>
                  <span class="cc-stat-delta">&#x2191; 18.4% vs last month</span>
                  <div class="cc-stat-list">
                    <span>Top products:</span>
                    <ol>
                      <li>Product A</li>
                      <li>Product B</li>
                      <li>Product C</li>
                    </ol>
                  </div>
                </div>
              </div>
            </div>
            <div class="cc-msg cc-user">
              <span class="cc-avatar" aria-hidden="true">You</span>
              <div class="cc-bubble cc-in">Which customers haven&rsquo;t paid?</div>
            </div>
            <div class="cc-msg cc-qefro">
              <span class="cc-avatar cc-avatar-q" aria-hidden="true">Q</span>
              <div class="cc-bubble cc-out">
                <p>I found 14 outstanding invoices.</p>
                <div class="cc-actions">
                  <button class="demo-btn demo-btn-primary" type="button">View invoices</button>
                  <button class="demo-btn demo-btn-ghost" type="button">Start follow-ups</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 6. AUTOMATION -->
    <section class="section section-alt" id="automation" aria-labelledby="automation-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="automation-heading">Set it once. Let Qefro follow through.</h2>
        </div>
        <div class="automation-flow reveal">
          <div class="auto-step"><span class="auto-icon">{ICONS["file"]}</span><p>Invoice becomes overdue</p></div>
          <span class="auto-arrow" aria-hidden="true">{ICONS["chevron"]}</span>
          <div class="auto-step"><span class="auto-icon">{ICONS["sparkles"]}</span><p>Qefro detects it</p></div>
          <span class="auto-arrow" aria-hidden="true">{ICONS["chevron"]}</span>
          <div class="auto-step"><span class="auto-icon">{ICONS["msg"]}</span><p>Follow-up created</p></div>
          <span class="auto-arrow" aria-hidden="true">{ICONS["chevron"]}</span>
          <div class="auto-step"><span class="auto-icon">{ICONS["zap"]}</span><p>WhatsApp reminder</p></div>
          <span class="auto-arrow" aria-hidden="true">{ICONS["chevron"]}</span>
          <div class="auto-step auto-step-done"><span class="auto-icon">{ICONS["check"]}</span><p>Customer pays</p></div>
          <span class="auto-arrow" aria-hidden="true">{ICONS["chevron"]}</span>
          <div class="auto-step auto-step-done"><span class="auto-icon">{ICONS["check"]}</span><p>Invoice marked paid</p></div>
        </div>
        <p class="automation-note reveal">Qefro doesn&rsquo;t stop when the conversation ends. Business events can trigger workflows, automations and follow-up actions automatically.</p>
      </div>
    </section>

    <!-- 7. CHANNELS -->
    <section class="section" id="channels" aria-labelledby="channels-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="channels-heading">Meet customers where they already are.</h2>
        </div>
        <div class="channels-visual reveal">
          <div class="channels-sources">
            <span class="channel-pill channel-whatsapp">WhatsApp</span>
            <span class="channel-pill channel-instagram">Instagram</span>
            <span class="channel-pill channel-web">Website</span>
            <span class="channel-pill channel-portal">Portal</span>
          </div>
          <div class="channels-arrow" aria-hidden="true">{ICONS["chevron"]}</div>
          <div class="channels-hub">
            <strong>Qefro</strong>
            <span>Same business capabilities</span>
          </div>
        </div>
        <p class="channels-note reveal">Customers can start conversations from different channels while your business runs on the same underlying Qefro runtime.</p>
      </div>
    </section>

    <!-- 8. FROM A MESSAGE TO A BUSINESS ACTION -->
    <section class="section section-alt" id="architecture" aria-labelledby="arch-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="arch-heading">From a message to a business action.</h2>
        </div>
        <div class="arch-flow reveal">
          <div class="arch-step"><span class="arch-num">1</span><p>Customer request</p></div>
          <span class="arch-connector" aria-hidden="true"></span>
          <div class="arch-step"><span class="arch-num">2</span><p>Qefro AI</p></div>
          <span class="arch-connector" aria-hidden="true"></span>
          <div class="arch-step"><span class="arch-num">3</span><p>Business capability</p></div>
          <span class="arch-connector" aria-hidden="true"></span>
          <div class="arch-step"><span class="arch-num">4</span><p>FlowRunner</p></div>
          <span class="arch-connector" aria-hidden="true"></span>
          <div class="arch-step"><span class="arch-num">5</span><p>Business data</p></div>
          <span class="arch-connector" aria-hidden="true"></span>
          <div class="arch-step"><span class="arch-num">6</span><p>Business event</p></div>
          <span class="arch-connector" aria-hidden="true"></span>
          <div class="arch-step"><span class="arch-num">7</span><p>Automation / Goal</p></div>
          <span class="arch-connector" aria-hidden="true"></span>
          <div class="arch-step arch-step-outcome"><span class="arch-num">8</span><p>Customer outcome</p></div>
        </div>
      </div>
    </section>

    <!-- 9. WHY QEFRO -->
    <section class="section" id="why-qefro" aria-labelledby="why-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="why-heading">Built for real business software.</h2>
        </div>
        <div class="why-grid reveal">
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["sparkles"]}</span>
            <h3>AI-native</h3>
            <p>AI is built into the business workflow&mdash;not added as a chatbot layer.</p>
          </article>
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["chart"]}</span>
            <h3>Business data</h3>
            <p>Customers, orders, invoices, appointments, properties and more.</p>
          </article>
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["zap"]}</span>
            <h3>Workflows</h3>
            <p>Turn repeatable business procedures into executable flows.</p>
          </article>
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["msg"]}</span>
            <h3>Business events</h3>
            <p>React to what actually happened in your business.</p>
          </article>
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["server"]}</span>
            <h3>Automation</h3>
            <p>Keep routine work moving automatically.</p>
          </article>
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["target"]}</span>
            <h3>Goals</h3>
            <p>Keep pursuing outcomes after the conversation ends.</p>
          </article>
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["globe"]}</span>
            <h3>Integrations</h3>
            <p>Connect external systems through Qefro&rsquo;s integration layer.</p>
          </article>
          <article class="why-card">
            <span class="why-icon" aria-hidden="true">{ICONS["headphones"]}</span>
            <h3>Multi-channel</h3>
            <p>Bring conversations from WhatsApp, Instagram, web and more into the same business context.</p>
          </article>
        </div>
      </div>
    </section>

    <!-- 10. TECHNICAL FOUNDATION -->
    <section class="section section-alt" id="foundation" aria-labelledby="foundation-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="foundation-heading">One foundation. Every business capability.</h2>
          <p>Qefro provides a reusable business runtime so each product can focus on its domain instead of rebuilding infrastructure from scratch.</p>
        </div>
        <div class="foundation-stack reveal">
          <div class="foundation-layer">Marketplace Apps</div>
          <div class="foundation-layer">Business Metadata</div>
          <div class="foundation-layer">Capabilities</div>
          <div class="foundation-layer">FlowRunner</div>
          <div class="foundation-layer">Business Entities</div>
          <div class="foundation-layer">Business Events</div>
          <div class="foundation-layer">Automation + Goals</div>
          <div class="foundation-layer foundation-layer-base">AI Agents</div>
        </div>
      </div>
    </section>

    <!-- 11. PRODUCT LANDING LINKS -->
    <section class="section" id="product-links" aria-labelledby="product-links-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="product-links-heading">Business software, ready to go.</h2>
          <p>Each product is purpose-built for its domain on the Qefro platform.</p>
        </div>
        <div class="product-landing-grid reveal">
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["utensils"]}</div>
            <h3>Qefro Restaurant</h3>
            <p>Run restaurant operations with AI.</p>
          </a>
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["file"]}</div>
            <h3>Qefro Billing</h3>
            <p>Create invoices. Track payments. Follow up automatically.</p>
          </a>
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["home"]}</div>
            <h3>Qefro Real Estate</h3>
            <p>Turn property enquiries into scheduled viewings.</p>
          </a>
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["users"]}</div>
            <h3>Qefro CRM</h3>
            <p>Manage customers, deals and follow-ups.</p>
          </a>
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["heart"]}</div>
            <h3>Qefro Clinic</h3>
            <p>Manage patients and appointments.</p>
          </a>
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["users"]}</div>
            <h3>Qefro HR</h3>
            <p>Manage employees and everyday HR operations.</p>
          </a>
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["kanban"]}</div>
            <h3>Qefro Project</h3>
            <p>Keep projects, tasks and teams moving.</p>
          </a>
          <a class="pl-card" href="/business-apps">
            <div class="pl-card-icon">{ICONS["shopping"]}</div>
            <h3>Qefro E-commerce</h3>
            <p>Run products, orders and customer operations.</p>
          </a>
        </div>
        <div class="section-cta reveal">
          <a class="btn btn-ghost" href="/business-apps">Explore all products {ICONS["arrow"]}</a>
        </div>
      </div>
    </section>

    <!-- 12. TRY QEFRO -->
    <section class="section section-alt" id="try-qefro" aria-labelledby="try-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="try-heading">Try Qefro</h2>
          <p>See what Qefro can do.</p>
        </div>
        <div class="try-choices reveal">
          <button class="try-chip" type="button" data-try-scenario="table">Book a table</button>
          <button class="try-chip" type="button" data-try-scenario="invoice">Create an invoice</button>
          <button class="try-chip" type="button" data-try-scenario="property">Find a property</button>
          <button class="try-chip" type="button" data-try-scenario="sales">Check sales</button>
          <button class="try-chip" type="button" data-try-scenario="customer">Find a customer</button>
        </div>
        <div class="try-demo-area reveal" id="try-demo-area" aria-live="polite">
          <p class="try-placeholder">Choose a scenario above to see Qefro in action.</p>
        </div>
      </div>
    </section>

    <!-- 13. PRICING -->
    <section class="section" id="pricing" aria-labelledby="pricing-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="pricing-heading">Simple pricing.</h2>
          <p>Start free. Upgrade when you&rsquo;re ready.</p>
        </div>
        <div class="price-scroll reveal">
{price_cards_html(interactive=True)}
        </div>
        <p class="pricing-note reveal">All plans include a 14-day free trial. No credit card required.</p>
      </div>
    </section>

    <!-- 14. FAQ -->
    <section class="section section-alt" id="faq" aria-labelledby="faq-heading">
      <div class="wrap-narrow">
        <div class="section-head reveal">
          <h2 id="faq-heading">Frequently asked questions.</h2>
        </div>
        <div class="faq-list reveal">
          <details class="faq-item" open>
            <summary>What is Qefro?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Qefro is AI-native business software. It gives you focused applications for CRM, Billing, Restaurant, Real Estate, Clinic, HR and more&mdash;with AI built into every workflow.</p>
          </details>
          <details class="faq-item">
            <summary>Is Qefro a CRM or ERP?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Qefro is neither a traditional CRM nor an ERP. It is a platform that runs focused business applications&mdash;each one purpose-built for its domain, with AI at the core.</p>
          </details>
          <details class="faq-item">
            <summary>What business products does Qefro offer?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Qefro CRM, Billing, Restaurant, Real Estate, Clinic, HR, Project and E-commerce. Each product is a standalone business application built on the same AI-native foundation.</p>
          </details>
          <details class="faq-item">
            <summary>Can I use Qefro on WhatsApp?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Yes. Customers and team members can interact with Qefro through WhatsApp, Instagram, your website widget, and the internal portal&mdash;all connected to the same business data.</p>
          </details>
          <details class="faq-item">
            <summary>Can Qefro actually perform business actions?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Yes. Qefro doesn&rsquo;t just answer questions&mdash;it books tables, creates invoices, schedules viewings, sends follow-ups, and completes real business operations.</p>
          </details>
          <details class="faq-item">
            <summary>Can I automate follow-ups?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Yes. Business events like overdue invoices or missed appointments can automatically trigger follow-up workflows through WhatsApp, email, or internal tasks.</p>
          </details>
          <details class="faq-item">
            <summary>Can I connect my existing business system?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Yes. Qefro supports integrations through its SDK and integration layer, so you can connect existing tools and data sources.</p>
          </details>
          <details class="faq-item">
            <summary>Does Qefro use AI agents?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Yes. Qefro uses AI agents that understand business context, invoke capabilities, and execute workflows&mdash;all within the boundaries you define.</p>
          </details>
          <details class="faq-item">
            <summary>Can I start with one business application?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Absolutely. Each workspace runs one primary business application. Start with the one you need, and add more as your business grows.</p>
          </details>
          <details class="faq-item">
            <summary>Can I try Qefro for free?<span class="faq-chevron" aria-hidden="true">{ICONS["chevron"]}</span></summary>
            <p>Yes. Every plan starts with a 14-day free trial. No credit card required.</p>
          </details>
        </div>
      </div>
    </section>

    <!-- 15. FINAL CTA -->
    <section class="cta-final" aria-labelledby="cta-heading">
      <div class="cta-final-glow" aria-hidden="true"></div>
      <div class="wrap-narrow reveal">
        <h2 id="cta-heading">Ready to run your business with AI?</h2>
        <p>Start with the business software you need. Let Qefro handle the work behind it.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_start_free">Start free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="#products" data-clarity-event="cta_explore_products">Explore products</a>
        </div>
        <p class="hero-micro">Define the business. Let Qefro execute it.</p>
      </div>
    </section>
"""


HOME_HOWTO_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "How to run your business with Qefro",
        "description": (
            "Start free, choose your business application, and let Qefro "
            "handle conversations, workflows, and automation."
        ),
        "url": f"{SITE}/",
        "step": [
            {
                "@type": "HowToStep",
                "position": 1,
                "name": "Start free",
                "text": "Create your workspace with a 14-day free trial.",
                "url": f"{SITE}/#products",
            },
            {
                "@type": "HowToStep",
                "position": 2,
                "name": "Choose your business software",
                "text": "Pick the Qefro product that matches your business: CRM, Billing, Restaurant, Real Estate, Clinic, HR, Project, or E-commerce.",
                "url": f"{SITE}/#products",
            },
            {
                "@type": "HowToStep",
                "position": 3,
                "name": "Let Qefro run it",
                "text": "Ask in chat, WhatsApp, or Command Chat. Qefro executes the work automatically.",
                "url": f"{SITE}/#command-chat",
            },
        ],
    },
    indent=2,
)


HOME_FAQ_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "What is Qefro?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Qefro is AI-native business software. It gives you focused applications for CRM, Billing, Restaurant, Real Estate, Clinic, HR and more — with AI built into every workflow.",
                },
            },
            {
                "@type": "Question",
                "name": "Is Qefro a CRM or ERP?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Qefro is neither a traditional CRM nor an ERP. It is a platform that runs focused business applications — each one purpose-built for its domain, with AI at the core.",
                },
            },
            {
                "@type": "Question",
                "name": "Can I use Qefro on WhatsApp?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. Customers and team members can interact with Qefro through WhatsApp, Instagram, your website widget, and the internal portal — all connected to the same business data.",
                },
            },
            {
                "@type": "Question",
                "name": "Can Qefro actually perform business actions?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. Qefro doesn't just answer questions — it books tables, creates invoices, schedules viewings, sends follow-ups, and completes real business operations.",
                },
            },
            {
                "@type": "Question",
                "name": "Can I try Qefro for free?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Yes. Every plan starts with a 14-day free trial. No credit card required.",
                },
            },
        ],
    },
    indent=2,
)


PAGES["index.html"] = page(
    title="Qefro — Your Business, Powered by AI",
    description=(
        "Qefro is AI-native business software for CRM, Billing, Restaurant, "
        "Real Estate, Clinic, HR and more. Run your business through conversations, "
        "workflows, and automation. Start free."
    ),
    path="",
    jsonld=[
        ORG_JSON,
        WEBSITE_JSON,
        SOFTWARE_JSON,
        HOME_HOWTO_JSON,
        HOME_FAQ_JSON,
        webpage_json(
            "Qefro — Your Business, Powered by AI",
            "AI-native business software for CRM, Billing, Restaurant, Real Estate, Clinic, HR and more. Start free.",
            "",
        ),
    ],
    body=home_body(),
    extra_scripts="",
)


# Inner pages — detailed content for menu-linked pages
def features_page_content() -> str:
    return f"""        <div class="outcome-grid reveal">
          <article class="outcome-card tilt-3d"><h3>AI</h3><ul><li>Grounded retrieval with citations</li><li>Multilingual knowledge indexing</li><li>Tool calling against your backends</li><li>Workspace-scoped instructions</li><li>Streaming replies across channels</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Applications</h3><ul><li>Managed Marketplace Apps</li><li>Custom SDK applications</li><li>Restaurant Pro &amp; Clinic Pro</li><li>Shared platform services</li><li>Per-workspace install &amp; config</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Customer Hub</h3><ul><li>Unified customer identity</li><li>Conversation and activity context</li><li>Cross-channel continuity</li><li>Team visibility with RBAC</li><li>Handoff-ready history</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Organization Workflows</h3><ul><li>Events, approvals, and tasks</li><li>Multi-step business processes</li><li>Human-in-the-loop steps</li><li>State until completion</li><li>Cross-team handoffs</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Channels</h3><ul><li>Website widget</li><li>WhatsApp Business</li><li>Internal Portal</li><li>API / WebSocket</li><li>Configure once, deploy everywhere</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>SDK &amp; Marketplace</h3><ul><li>External SDK Connections</li><li>Signed /qefro protocol</li><li>REST &amp; OpenAPI tools</li><li>Managed Marketplace installs</li><li>On-prem capable backends</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Storage &amp; Marketing</h3><ul><li>Document &amp; site knowledge stores</li><li>OCR for scans and images</li><li>Lead capture in-channel</li><li>Campaign-ready customer context</li><li>Execution and conversation logs</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>RBAC &amp; Workspaces</h3><ul><li>Owner / Admin / Member roles</li><li>Tenant and workspace isolation</li><li>Scoped tools and secrets</li><li>Team boundaries per app</li><li>Billing restricted to owners</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-blue">{ICONS["building"]} Shared foundation</span>
          <h2>One platform under every application</h2>
          <p>Every managed or custom app shares AI, Customer Hub, workflows, storage, channels, and RBAC — so you do not rebuild the stack for each use case.</p>
        </div>
        <div class="workspace-grid reveal">
          <article class="workspace-card"><h3>Connect</h3><p>SDK, Marketplace apps, and webhooks against systems you already run.</p></article>
          <article class="workspace-card"><h3>Engage</h3><p>AI chat, WhatsApp, and voice with live business data from connected capabilities.</p></article>
          <article class="workspace-card"><h3>Automate</h3><p>Business events trigger WhatsApp, tags, assignment, follow-ups, and tasks.</p></article>
          <article class="workspace-card"><h3>Govern</h3><p>Workspaces, teams, secrets, and role-based access in one Admin Console.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["msg"]} Channels</span>
          <h2>Channels are delivery surfaces — not the product</h2>
          <p>Website, WhatsApp, Internal Portal, and API all reach the same applications, tools, and permissions.</p>
        </div>
        <div class="table-wrap reveal" style="margin-top:1.5rem">
          <table class="compare-table" aria-label="Qefro channel matrix">
            <thead>
              <tr>
                <th>Surface</th>
                <th>Audience</th>
                <th>Auth</th>
                <th>What it reaches</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Website widget</td>
                <td>Customers &amp; visitors</td>
                <td>Widget JWT / identify()</td>
                <td>Apps, tools, Customer Hub</td>
              </tr>
              <tr>
                <td>WhatsApp</td>
                <td>Customers on messaging</td>
                <td>Channel + identity mapping</td>
                <td>Same apps and workflows</td>
              </tr>
              <tr>
                <td>Internal Portal</td>
                <td>Employees &amp; teams</td>
                <td>Email OTP + workspace session</td>
                <td>Team knowledge and internal tools</td>
              </tr>
              <tr>
                <td>API / WebSocket</td>
                <td>Your products &amp; UIs</td>
                <td>API credentials</td>
                <td>Programmatic access to the platform</td>
              </tr>
            </tbody>
          </table>
        </div>
"""


def how_it_works_page_content() -> str:
    return f"""        <div class="three-way-grid reveal" style="margin-bottom:2.5rem">
          <article class="three-way-card"><h3>1. Connect</h3><p>Connect your ERP, CRM, business application, or custom system through the SDK, Marketplace, or webhooks.</p></article>
          <article class="three-way-card"><h3>2. Configure</h3><p>Choose customer-facing capabilities, CRM, and automation. Capabilities are what Qefro can invoke. Business events are what happened.</p></article>
          <article class="three-way-card"><h3>3. Engage</h3><p>Customers interact through AI chat, WhatsApp, and other channels — with live data from the systems you already run.</p></article>
        </div>
        <div class="pipeline pipeline-flow reveal" aria-label="How Qefro works">
          <span class="pipeline-node"><span class="pipeline-v">Your software</span><span class="pipeline-d">ERP / CRM / apps</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node"><span class="pipeline-v">Qefro</span><span class="pipeline-d">AI + CRM + automation</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node pipeline-node-accent"><span class="pipeline-v">Customers</span><span class="pipeline-d">Chat · WhatsApp · Voice</span></span>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3rem">
          <h2>Keep your systems of record</h2>
          <p>Workspaces bound connections, teams, channels, and customers. The Admin Console is where you connect software, choose capabilities, and govern access.</p>
        </div>
        <div class="steps-grid reveal">
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">01</div></div><h3>Create organization &amp; workspace</h3><p>Set the operational boundary for connections, teams, and channels.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">02</div></div><h3>Connect systems</h3><p>SDK connection, Marketplace app, or webhook — your software stays yours.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">03</div></div><h3>Enable channels</h3><p>Website chat, WhatsApp, and voice — all to the same customer layer.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">04</div></div><h3>Automate from events</h3><p>When the connected app emits a business event, Qefro can follow up, tag, or assign.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>What we handle for you</h2>
          <p>Conversations, CRM around the relationship, automation, and channel delivery — you keep ERP, industry software, and ledgers as the source of truth.</p>
        </div>
"""

def use_cases_page_content() -> str:
    return f"""        <div class="uc-grid reveal">
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["chart"]}</div><h3>Sales</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Product search and quotations</li><li>{ICONS["chevr"]} CRM lookups via SDK tools</li><li>{ICONS["chevr"]} Lead capture across channels</li><li>{ICONS["chevr"]} Approval workflows for quotes</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["zap"]}</div><h3>Operations</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Order and shipment actions</li><li>{ICONS["chevr"]} Ticketing and escalations</li><li>{ICONS["chevr"]} Cross-team task handoffs</li><li>{ICONS["chevr"]} Audit-ready execution logs</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["shield"]}</div><h3>Healthcare</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Connected hospital or clinic software</li><li>{ICONS["chevr"]} Appointment lookups via capabilities</li><li>{ICONS["chevr"]} Staff context in Customer 360</li><li>{ICONS["chevr"]} WhatsApp and website channels</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["building"]}</div><h3>Restaurants</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Connected restaurant software</li><li>{ICONS["chevr"]} Reservation and menu questions</li><li>{ICONS["chevr"]} Confirmations from business events</li><li>{ICONS["chevr"]} WhatsApp + website channels</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["file"]}</div><h3>Finance</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Policy and procedure answers</li><li>{ICONS["chevr"]} Approval-gated actions</li><li>{ICONS["chevr"]} Workspace-scoped secrets</li><li>{ICONS["chevr"]} Tenant isolation by design</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["server"]}</div><h3>Enterprise integrations</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} ERP / CRM External SDK Connections</li><li>{ICONS["chevr"]} On-prem capable backends</li><li>{ICONS["chevr"]} Organization Workflows</li><li>{ICONS["chevr"]} RBAC across teams and apps</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["zap"]} Platform in action</span>
          <h2>Applications on a shared foundation</h2>
          <p>Customer support chat is one channel. Sales assistants, connected clinic or restaurant software, and custom SDK apps all use the same Qefro customer layer — conversations, CRM, and automation.</p>
        </div>
        <div class="scenario-grid reveal">
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Sales</span> Find SKU and quote</p>
            <div class="scenario-flow"><span>SDK tool searchProducts</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Quotation drafted in your ERP</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Ops</span> Cancel order #4821</p>
            <div class="scenario-flow"><span>Workflow + Business Tool</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Approval then system update</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Clinic</span> What is our triage policy?</p>
            <div class="scenario-flow"><span>Workspace knowledge</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Cited answer for staff</span></div>
          </article>
          <article class="scenario-card tilt-3d">
            <p class="scenario-ask"><span>Customer</span> I need a human</p>
            <div class="scenario-flow"><span>Handoff triggered</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Agent sees full thread in hub</span></div>
          </article>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Industries</h2>
          <p>Teams in SaaS, healthcare, hospitality, manufacturing, retail, and internal operations use Qefro to ship AI business applications without rebuilding the platform layer.</p>
        </div>
        {pill_cloud([(f"/{s}", l) for s, l in industry_link_grid()], "Industry landing pages", ul_class=" reveal mt-1")}
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Topic pages</h2>
          <p>Explore common search intents — support, RAG, WhatsApp agents, and more — as applications on the Qefro platform.</p>
        </div>
        {pill_cloud([(f"/{s}", l) for s, l in topic_link_grid()], "Topic landing pages", ul_class=" reveal mt-1")}
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>AI customer support by industry</h2>
          <p>Programmatic pages for niche support intent — one application surface on the same platform.</p>
        </div>
        {pill_cloud([(f"/{s}", l) for s, l in vertical_link_grid()], "Vertical landing pages", ul_class=" reveal mt-1")}"""



def business_apps_page_content() -> str:
    re_chat = convo_example(
        "I need a 2-bedroom apartment near downtown, budget under $1,500/month.",
        "I found 3 matching listings. The top match is a 2BR on Maple Ave — $1,400/mo, available next week. Want to schedule a viewing?",
    )
    rest_chat = convo_example(
        "Do you have a table for 4 tonight?",
        "Yes — we have openings at 7:00 and 8:30 PM. Shall I reserve one? I can also share tonight's specials.",
    )
    clinic_chat = convo_example(
        "I need to reschedule my appointment on Thursday.",
        "I see your appointment with Dr. Patel at 2:00 PM. The nearest available slot is Friday at 10:00 AM. Want me to switch it?",
    )
    return f"""        <div class="section-head reveal" style="text-align:left">
          <span class="badge badge-indigo">{ICONS["sparkles"]} Flagship app</span>
          <h2>Real Estate Pro</h2>
          <p>AI-powered property inquiries — from first question to scheduled viewing. Connects to your listing database, handles follow-ups, and keeps your team in the loop.</p>
        </div>
        <div class="convo-grid reveal">
          {re_chat}
          <div style="display:flex;flex-direction:column;gap:1rem;justify-content:center">
            <div class="check-list">
              <span>{ICONS["check"]} Live property search</span>
              <span>{ICONS["check"]} Viewing scheduling</span>
              <span>{ICONS["check"]} Quotation generation</span>
              <span>{ICONS["check"]} WhatsApp follow-up</span>
              <span>{ICONS["check"]} CRM context &amp; history</span>
              <span>{ICONS["check"]} Human handoff when needed</span>
            </div>
          </div>
        </div>

        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>Industry applications</h2>
          <p>Pre-built AI apps for the most common business workflows. Each one connects to your existing systems and deploys across chat, WhatsApp, and web.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card tilt-3d">
            <h3>Restaurant Pro</h3>
            <p>Reservations, menu queries, order tracking, and customer follow-up — all handled by AI across WhatsApp and web chat.</p>
            <ul><li>Table reservations</li><li>Menu &amp; specials lookup</li><li>Order status tracking</li><li>Automated follow-ups</li></ul>
          </article>
          <article class="outcome-card tilt-3d">
            <h3>Clinic Pro</h3>
            <p>Appointment scheduling, patient context, reminders, and rescheduling — reducing front-desk workload while keeping care personal.</p>
            <ul><li>Appointment management</li><li>Patient history context</li><li>Automated reminders</li><li>Rescheduling &amp; cancellations</li></ul>
          </article>
          <article class="outcome-card tilt-3d">
            <h3>E-commerce</h3>
            <p>Order status, product search, returns, and proactive shipping updates — the customer service layer on top of your store.</p>
            <ul><li>Order tracking</li><li>Product search &amp; recommendations</li><li>Return initiation</li><li>Shipping notifications</li></ul>
          </article>
          <article class="outcome-card tilt-3d">
            <h3>ERP + Sales</h3>
            <p>Quotations, order management, and CRM workflows — bring your ERP data into customer conversations without manual lookup.</p>
            <ul><li>Quote generation</li><li>Order management</li><li>Customer assignment</li><li>Approval workflows</li></ul>
          </article>
        </div>

        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>See them in action</h2>
          <p>Each app handles real customer conversations with live data from your connected systems.</p>
        </div>
        <div class="convo-grid reveal">
          {rest_chat}
          {clinic_chat}
        </div>

        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["zap"]} Build your own</span>
          <h2>Custom applications</h2>
          <p>When pre-built apps don't cover your workflow, build on the Qefro SDK. Same platform, same AI, same channels — your business logic.</p>
        </div>
        <div class="cap-grid reveal">
          <div class="cap-card"><div class="cap-icon">{ICONS["zap"]}</div><span>OpenAPI tool definitions</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>External SDK Connections</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["lock"]}</div><span>Signed /qefro protocol</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>AI planning &amp; tool calling</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["shield"]}</div><span>Workspace-scoped permissions</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Execution logs &amp; audit trail</span></div>
        </div>

        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>How apps connect to your business</h2>
          <p>Every Qefro app follows the same pattern: connect your existing systems, configure the AI behavior, and deploy across channels. No data migration, no rip-and-replace — Qefro adds the intelligence layer on top of what you already run.</p>
        </div>
        <div class="steps-grid steps-grid-3 reveal">
          <div class="step-card">
            <span class="step-num">1</span>
            <h3>Connect</h3>
            <p>Link your ERP, CRM, listing database, or any system with an API. Signed SDK connections keep credentials in your backend.</p>
          </div>
          <div class="step-card">
            <span class="step-num">2</span>
            <h3>Configure</h3>
            <p>Set AI instructions, tool permissions, approval gates, and workspace boundaries. Control what the AI can do autonomously vs. what needs human approval.</p>
          </div>
          <div class="step-card">
            <span class="step-num">3</span>
            <h3>Deploy</h3>
            <p>Go live across website chat, WhatsApp, and API. Customers get instant answers. Your team gets CRM context, automation, and full visibility.</p>
          </div>
        </div>"""


def security_page_content() -> str:
    return f"""        <div class="trust-grid reveal">
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["building"]}</div><h3>Tenant &amp; workspace isolation</h3><p>Multi-tenant by design at the database and vector store level. Workspaces control which knowledge, apps, and tools each experience can use.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["lock"]}</div><h3>Signed SDK connections</h3><p>External SDK Connections use a signed /qefro protocol. Credentials stay in your backend; Qefro orchestrates tool calls.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["bot"]}</div><h3>End-user identity forwarding</h3><p>Forward signed-in identity via <code>identify()</code> so tools run as the real user — passwords never touch Qefro.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["file"]}</div><h3>Audit &amp; execution logs</h3><p>Conversation history and tool runs stay attached for accountability and review.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["shield"]}</div><h3>RBAC &amp; controlled tools</h3><p>Owner / Admin / Member roles, workspace-scoped secrets, and per-tool allowlists for public channels.</p></article>
          <article class="trust-card tilt-3d"><div class="trust-icon">{ICONS["server"]}</div><h3>On-prem capable External SDK</h3><p>Run sensitive connectors in your infrastructure. HTTPS-only outbound calls with SSRF protections and DNS-pinned webhooks.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>Enterprise platform controls</h2>
          <p>Your systems remain yours. Qefro adds the AI application layer with governance — not a black-box takeover of your ERP or CRM.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card tilt-3d"><h3>Access control</h3><ul><li>Owner / Admin / Member RBAC</li><li>Email OTP — no password storage</li><li>Billing actions restricted to owners</li><li>Workspace-scoped documents &amp; tools</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Data handling</h3><ul><li>PII scrubbing on outbound LLM calls</li><li>Never used to train AI models</li><li>Encrypted at rest &amp; in transit</li><li>Conversation isolation</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Tool execution</h3><ul><li>OpenAPI schema validation</li><li>SSRF &amp; DNS pinning for webhooks</li><li>Per-tool public-chat allow toggles</li><li>Execution logs for accountability</li></ul></article>
          <article class="outcome-card tilt-3d"><h3>Enterprise roadmap</h3><ul><li>SSO / SAML (roadmap)</li><li>Platform admin audit trail (roadmap)</li><li>Private deployment available today</li><li>SOC 2 program in progress</li></ul></article>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Compliance &amp; deployment</h2>
          <p>Enterprise customers can run Qefro in a private environment with dedicated support. Contact Sales for the current compliance roadmap and data processing terms — we do not invent certifications we have not completed.</p>
        </div>"""



def pricing_page_content() -> str:
    return f"""        <div class="pricing-ledger" data-pricing-root data-pricing-api="{API}">
          <div class="direct-answer reveal">
            <p>Every new organization starts with a <strong>14-day free trial</strong>. Choose apps, connect your business, and experience the outcome — then pick a paid plan: Starter ₹699/mo (1 user), Pro ₹1,499/mo (5 users), or Growth ₹2,999/mo (15 users). Marketplace apps are billed separately.</p>
          </div>
          <div class="headcount-tape reveal" aria-label="Team size by plan">
            <p class="tape-kicker">Team size</p>
            <p class="tape-lead">Each plan includes a fixed number of users. Need more people? Upgrade to the next plan.</p>
            <p class="tape-break">Starter 1 user · Pro up to 5 · Growth up to 15</p>
            <div class="currency-toggle" role="group" aria-label="Currency">
              <button type="button" data-currency="INR" class="is-active" aria-pressed="true">INR</button>
              <button type="button" data-currency="USD" aria-pressed="false">USD</button>
            </div>
          </div>
          <div class="billing-toggle reveal" role="group" aria-label="Billing period">
            <button type="button" data-billing="monthly" aria-pressed="false">Monthly</button>
            <button type="button" data-billing="annual" class="is-active" aria-pressed="true">Yearly <span>2 months free</span></button>
          </div>
          <div class="price-grid reveal">
{price_cards_html(interactive=False)}
          </div>
          <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
            <h2>Compare plans</h2>
            <p>Users, customers, documents, and integrations — not AI message quotas.</p>
          </div>
          <div class="compare-wrap reveal">
            <table class="compare-table pricing-compare">
              <thead>
                <tr><th>Capability</th><th>Starter</th><th>Pro</th><th>Growth</th><th>Enterprise</th></tr>
              </thead>
              <tbody>
                <tr><th>Users included</th><td>1</td><td>5</td><td>15</td><td>Custom</td></tr>
                <tr><th>CRM customers</th><td>500</td><td>2,500</td><td>10,000</td><td>Custom</td></tr>
                <tr><th>Documents</th><td>50</td><td>200</td><td>500</td><td>Custom</td></tr>
                <tr><th>Integrations</th><td>5</td><td>25</td><td>Unlimited</td><td>Custom</td></tr>
                <tr><th>CRM</th><td>✓</td><td>Advanced</td><td>Customer 360</td><td>Custom</td></tr>
                <tr><th>Automations</th><td>✓</td><td>Advanced</td><td>✓</td><td>Custom</td></tr>
                <tr><th>WhatsApp</th><td>✓</td><td>✓</td><td>✓</td><td>✓</td></tr>
                <tr><th>Voice</th><td>—</td><td>✓</td><td>✓</td><td>✓</td></tr>
                <tr><th>Analytics</th><td>—</td><td>✓</td><td>Reporting</td><td>Custom</td></tr>
                <tr><th>API</th><td>—</td><td>✓</td><td>✓</td><td>✓</td></tr>
                <tr><th>Marketplace</th><td>Separate</td><td>Separate</td><td>Separate</td><td>Separate</td></tr>
              </tbody>
            </table>
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
            <p>Billing is prepaid via Razorpay in the portal. Upgrade or change plans anytime; owners manage subscriptions and invoices from the billing page. Also see: <a href="/qefro-pricing">How much does Qefro cost?</a></p>
          </div>
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
            Qefro connects existing business software to AI-powered customer conversations, CRM, and automation. Contact: <a href="mailto:support@qefro.com">support@qefro.com</a>.
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
            Qefro connects existing business software to AI-powered customer conversations, CRM, and automation.
            You configure organizations, workspaces, connections, and channels. Features and plan limits are described on
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
        speakable_json(path),
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
          <aside class="quick-answer-card" aria-label="Quick Summary">
            <span class="quick-answer-badge">{ICONS["sparkles"]} Quick Answer</span>
            <div style="text-align:left">{answer}</div>
          </aside>
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
        <span class="badge badge-indigo">{ICONS["sparkles"]} AI Business Platform</span>
        <h2>Ready to put AI to work?</h2>
        <p>Start your 14-day free trial. Choose apps, connect your business, and experience the outcome — then pick a paid plan.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">{CTA_TRIAL} {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/business-apps">{CTA_MARKETPLACE}</a>
          <a class="btn btn-link btn-lg" href="/contact">Talk to Sales</a>
        </div>
        <p class="integrations-note" style="margin-top:1.25rem"><a href="/pricing">See plans</a> · <a href="{DOCS}">Documentation</a> · <a href="/security">Security</a></p>
      </div>
    </section>
""",
    )


PAGES["features.html"] = inner(
    "Features | Qefro",
    "Product capabilities",
    "AI customer conversations, CRM, Customer 360, automations, WhatsApp, SDK, and Marketplace — the customer layer on top of software you already use.",
    "features.html",
    "features",
    "<p>Qefro is the <strong>AI customer interaction and automation layer</strong> that connects existing business software to customers. It is not another ERP, CRM replacement, or generic chatbot.</p>",
    features_page_content(),
    badge=f'{ICONS["sparkles"]} Features',
)

PAGES["how-it-works.html"] = inner(
    "How it works | Qefro",
    "How Qefro works",
    "Connect existing systems, configure capabilities, CRM and automation, then engage customers through AI chat and WhatsApp — without replacing your ERP or CRM.",
    "how-it-works.html",
    "how-it-works",
    "<p><strong>Connect. Configure. Engage.</strong> Keep your systems of record. Qefro adds the AI business applications on top — conversations, CRM, and automation.</p>",
    how_it_works_page_content(),
    extra_jsonld=[howto_json("how-it-works.html")],
    badge=f'{ICONS["zap"]} How it works',
)

PAGES["business-apps.html"] = inner(
    "Business Apps | Qefro",
    "AI Business Applications",
    "Pre-built AI applications for real estate, restaurants, healthcare, e-commerce and more. Connect your existing systems, engage customers, and automate follow-ups.",
    "business-apps.html",
    "business-apps",
    "<p>Qefro offers <strong>pre-built AI applications</strong> for common business workflows — plus an SDK to build custom apps. Each one connects to your existing systems and deploys across chat, WhatsApp, and web.</p>",
    business_apps_page_content(),
    badge=f'{ICONS["sparkles"]} Business Apps',
)

PAGES["use-cases.html"] = inner(
    "Solutions | Qefro",
    "Solutions",
    "ERP, e-commerce, restaurants, healthcare, and custom business apps — Qefro is the customer conversation layer, not a vertical ERP.",
    "use-cases.html",
    "use-cases",
    "<p>Use Qefro with the software you already run. Vertical examples depend on the connected application&rsquo;s capabilities &mdash; Qefro does not replace those systems.</p>",
    use_cases_page_content(),
    badge=f'{ICONS["building"]} Applications',
)

PAGES["security.html"] = inner(
    "Security | Qefro",
    "Security",
    "Workspace isolation, capability-based access, signed events, and an existing business system that remains the source of truth.",
    "security.html",
    "security",
    "<p>Your business data stays under your control. Qefro connects through authorized capabilities and signed events — CRM does not duplicate entire business ledgers. SOC 2 is on our roadmap — contact Sales for the current timeline.</p>",
    security_page_content(),
    badge=f'{ICONS["shield"]} Security',
)

PAGES["pricing.html"] = inner(
    "Pricing | Qefro",
    "Simple pricing that grows with your business",
    "Fixed-price plans with a maximum team size. 14-day free trial. Starter ₹699/mo (1 user), Pro ₹1,499/mo (5 users), Growth ₹2,999/mo (15 users).",
    "pricing.html",
    "pricing",
    "<p>Start with one user on Starter. Pro includes up to 5 users, Growth up to 15. Marketplace apps stay on their own bill.</p>",
    pricing_page_content(),
    # No FAQPage here — Google asks to mark up each FAQ only once (on /faq).
    extra_jsonld=[PRICING_OFFERS_JSON],
    extra_sections=f'    <script type="module" src="/assets/js/pricing.js?v={ASSET_VERSION}"></script>\n',
    badge=f'{ICONS["zap"]} Pricing',
)

faq_html = "".join(
    faq_item_html(q, a, "faq", i) for i, (q, a) in enumerate(FAQ_ITEMS)
)

PAGES["faq.html"] = page(
    title="FAQ | Qefro",
    description="FAQ about Qefro: connecting existing business software to AI conversations, CRM, automation, pricing, security, and setup.",
    path="faq.html",
    active="faq",
    jsonld=[
        webpage_json(
            "FAQ | Qefro",
            "FAQ about Qefro: connecting existing business software to AI conversations, CRM, automation, pricing, security, and setup.",
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
    og_type="article",
    jsonld=[
        webpage_json(
            "Benchmark methodology | Qefro",
            "How Qefro measures answer accuracy: test set composition, evaluation methodology, results, and known limitations.",
            "benchmark",
        ),
        breadcrumb_json([("Home", "/"), ("Benchmark Methodology", "benchmark")]),
        tech_article_json(
            "Benchmark methodology | Qefro",
            "How Qefro measures answer accuracy: test set composition, evaluation methodology, results, and known limitations.",
            "benchmark",
        ),
        speakable_json("benchmark.html"),
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
          <p class="contact-alt">Prefer email? <a href="mailto:support@qefro.com?subject=Qefro%20demo%20request">support@qefro.com</a> · or <a href="{PORTAL_SIGNUP}">{CTA_TRIAL_SHORT}</a></p>
        </form>
        <div class="cap-grid" style="margin-top:2rem">
          <a class="cap-card" href="mailto:support@qefro.com"><div class="cap-icon">{ICONS["msg"]}</div><span>support@qefro.com</span></a>
          <a class="cap-card" href="{PORTAL_SIGNUP}"><div class="cap-icon">{ICONS["zap"]}</div><span>{CTA_TRIAL}</span></a>
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
    description="Terms governing use of the Qefro AI Business Application Platform, including accounts, billing, acceptable use, and liability.",
    path="terms.html",
    active=None,
    jsonld=[
        webpage_json(
            "Terms of Service | Qefro",
            "Terms governing use of the Qefro AI Business Application Platform, including accounts, billing, acceptable use, and liability.",
            "terms.html",
        ),
        breadcrumb_json([("Home", "/"), ("Terms of Service", "terms")]),
    ],
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), ("Terms of Service", "")])}
        <h1>Terms of Service</h1>
        <div class="direct-answer" style="text-align:left">
          <p>The agreement between you and Qefro for using the AI Business Application Platform and related websites.</p>
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
        "What is Qefro? | AI Business Platform",
        "What is Qefro?",
        "Qefro is an AI Business Platform. It turns customer conversations into business outcomes using your data, apps, workflows, automations, and people — not a chatbot bolted onto a form.",
        "<p>Start a 14-day free trial, install the apps your business needs, and let Qefro run the work across WhatsApp, website, mobile, and Command Chat.</p>",
    ),
    (
        "qefro-pricing.html",
        "How much does Qefro cost? | Pricing overview",
        "How much does Qefro cost?",
        "Every new organization starts with a 14-day free trial. After the trial, Starter is ₹699/month (1 user), Pro is ₹1,499/month (5 users), and Growth is ₹2,999/month (15 users). Marketplace apps billed separately. Enterprise is custom.",
        '<p>See the full comparison on the <a href="/pricing">pricing page</a>.</p>',
    ),
]:
    page_jsonld = [
        webpage_json(title, a, slug),
        breadcrumb_json([("Home", "/"), (q, slug.removesuffix(".html"))]),
        speakable_json(slug),
    ]
    if slug == "what-is-qefro.html":
        page_jsonld.append(tech_article_json(title, a, slug))
    PAGES[slug] = page(
        title=title,
        description=a,
        path=slug,
        og_type="article" if slug == "what-is-qefro.html" else "website",
        jsonld=page_jsonld,
        body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", "/"), (q, "")])}
        <h1>{q}</h1>
        <aside class="quick-answer-card" aria-label="Quick Summary">
          <span class="quick-answer-badge">{ICONS["sparkles"]} Quick Answer</span>
          <p>{a}</p>
        </aside>
        <div class="prose" style="margin-top:1.5rem">{extra}
          <p><a class="btn btn-primary" href="{PORTAL_SIGNUP}">{CTA_TRIAL}</a></p>
        </div>
      </div>
    </section>
""",
    )


def _landing_cards(cards: list[tuple[str, str, str]]) -> str:
    items = "\n".join(
        f"""          <div class="exp-card tilt-3d">
            <div class="exp-icon">{ICONS[icon]}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
          </div>"""
        for icon, title, desc in cards
    )
    return f"""        <div class="exp-grid reveal" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.25rem;margin-top:1.5rem">
{items}
        </div>"""


def _landing_flow(steps: list[str]) -> str:
    if not steps:
        return ""
    parts = []
    for i, label in enumerate(steps):
        if i:
            parts.append(f'          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>')
        accent = " pipeline-node-accent" if i == len(steps) - 1 else ""
        parts.append(f'          <span class="pipeline-node{accent}"><span class="pipeline-v">{label}</span></span>')
    body = "\n".join(parts)
    return f"""        <div class="pipeline pipeline-flow reveal" style="margin-top:2rem" aria-label="{escape(' then '.join(steps))}">
{body}
        </div>"""


def _landing_related(related: list[tuple[str, str]]) -> str:
    pills = "\n".join(
        f'          <a class="workspace-pill" href="{DOCS if slug == "docs" else "/" + slug}">{label}</a>'
        for slug, label in related
    )
    return f"""        <div class="prose reveal" style="margin-top:2.5rem">
          <p class="facts-label">Explore more</p>
          <div class="workspace-pills">
{pills}
          </div>
        </div>"""


def landing_body(intro: str, cards, steps, related) -> str:
    return f"""        <div class="prose"><p>{intro}</p></div>
{_landing_cards(cards)}
{_landing_flow(steps)}
{_landing_related(related)}"""


# Product & platform landing pages — AI Business Application Platform.
# (title, h1, slug, meta_desc, badge, quick_answer, intro, cards, flow_steps, related)
LANDING_PAGES = [
    (
        "Business Flows | Automate processes end to end | Qefro",
        "Automate organization processes from start to finish",
        "business-flows.html",
        "Business Flows orchestrate tools into multi-step processes — asking questions, calling systems, pausing for approval, and completing the work across your organization.",
        f'{ICONS["zap"]} Business Flows',
        "A Business Flow is a declarative description of how a request is completed: which questions to ask, which Business Tools to call, when to branch, and when to pause for human approval. The Qefro Runtime executes the flow and maintains state until the task is done.",
        "An answer isn&rsquo;t an outcome. Business Flows turn a customer request into a completed process — order changes, cancellations, refunds, onboarding, claims — executed step by step across your systems, with humans looped in only when a step requires approval.",
        [
            ("file", "Declarative flows", "Describe the process once; the Runtime executes it. Flows are metadata — nothing runs in your backend."),
            ("zap", "Multi-step orchestration", "Ask, call tools, branch on conditions, delay, and resume — all in one governed flow."),
            ("shield", "Human approval steps", "Insert approval and challenge/resume steps so a person signs off before sensitive actions execute."),
            ("check", "Versioned &amp; validated", "Flows are validated at sync time and versioned, with Accept/Reject prompts on change."),
        ],
        ["Understand", "Route", "Execute", "Complete"],
        [("workflow-engine", "Workflow Engine"), ("business-tools", "Business Tools"), ("sdk", "SDK"), ("features", "All features")],
    ),
    (
        "Business Tools | Controlled tool execution | Qefro",
        "Controlled tool execution against your existing systems",
        "business-tools.html",
        "Business Tools are controlled capabilities AI applications call in your ERP, CRM, HR, OMS, and billing systems — via REST/OpenAPI or External SDK Connections, with encrypted credentials and identity forwarding.",
        f'{ICONS["lock"]} Business Tools',
        "A Business Tool is a secure, scoped capability an AI application can call — search products, draft a quotation, open a ticket. Credentials are encrypted and scoped per workspace, and every call is logged.",
        "Qefro does not replace your systems of record. Applications call Business Tools — typed, permissioned capabilities you define — so automation stays secure, auditable, and under your control.",
        [
            ("globe", "REST / OpenAPI import", "Turn existing endpoints into tools by importing an OpenAPI spec or configuring REST calls."),
            ("lock", "Business Tool SDK", "Run auth and tool logic in your backend with the Rust, JavaScript, or Python SDK."),
            ("shield", "Encrypted credentials", "Secrets are encrypted at rest and scoped per workspace — never exposed to the model."),
            ("server", "Identity forwarding", "Forward the verified customer identity so tools act with the right permissions."),
        ],
        ["AI agent", "Business Tool", "ERP / CRM / Database", "Result"],
        [("sdk", "SDK"), ("openapi", "REST &amp; OpenAPI"), ("integrations", "Integrations"), ("business-flows", "Business Flows")],
    ),
    (
        "Organization Workflows | Events, approvals &amp; tasks | Qefro",
        "Orchestrate work across teams and applications",
        "workflow-engine.html",
        "Organization Workflows orchestrate events, approvals, tasks, and multi-step processes across teams and applications — with branching, delays, retries, and state until completion.",
        f'{ICONS["zap"]} Organization Workflows',
        "Organization Workflows execute Business Flows: events, tool calls, conditions, human approvals, and tasks between applications — with state maintained until the work is done.",
        "Automate across your organization — not just a single chat turn. Workflows track where a process is, resume after approval, retry transient failures, and finish only when the work is complete.",
        [
            ("zap", "Multi-step execution", "Sequence questions, tool calls, and decisions into one reliable process."),
            ("chart", "Conditions &amp; branching", "Route to the right path based on data returned from your systems."),
            ("server", "Delays, retries &amp; resume", "Wait, retry, and resume long-running processes without losing context."),
            ("check", "State until completion", "Workflow state is maintained until the task finishes — not just until the reply is sent."),
        ],
        ["Conversation", "Business Flow", "Business Tools", "Completed task"],
        [("business-flows", "Business Flows"), ("business-tools", "Business Tools"), ("sdk", "SDK"), ("how-it-works", "Platform")],
    ),
    (
        "SDK | External Connections &amp; Marketplace Apps | Qefro",
        "Build an External SDK Connection or a Managed Marketplace App",
        "sdk.html",
        "Build External SDK Connections or Managed Marketplace Apps with the Qefro SDK (Rust, JavaScript, Python) — signed /qefro protocol, tools in your backend, credentials that never leave your infrastructure.",
        f'{ICONS["lock"]} Qefro SDK',
        "Use the SDK two ways: External SDK Connections that keep systems on your side, or Managed Marketplace Apps you ship into workspaces. Declare tools in code; Qefro calls them over a signed protocol.",
        "When a tool needs your auth, session logic, or data that must never leave your infrastructure, run an External SDK Connection. Your backend stays the source of truth; Qefro orchestrates.",
        [
            ("server", "Rust SDK", "High-performance backend integration with typed tools and flows."),
            ("globe", "JavaScript SDK", "Node/TypeScript SDK for fast integration with existing services."),
            ("file", "Python SDK", "qefro-backend on PyPI — the same signed protocol, zero dependencies."),
            ("lock", "Signed webhook protocol", "Every callback is signed; identity is forwarded; credentials stay in your backend."),
        ],
        ["Runtime", "Signed webhook", "Your backend", "Your systems"],
        [("openapi", "REST &amp; OpenAPI"), ("business-tools", "Business Tools"), ("integrations", "Integrations"), ("docs", "Documentation")],
    ),
    (
        "REST &amp; OpenAPI | Turn your APIs into AI tools | Qefro",
        "Turn your existing APIs into AI Business Tools",
        "openapi.html",
        "Import an OpenAPI spec or configure REST endpoints to expose your existing APIs as Business Tools — encrypted credentials, per-workspace scoping, and no backend code required.",
        f'{ICONS["globe"]} REST &amp; OpenAPI',
        "The REST/OpenAPI path connects your existing APIs as Business Tools without writing backend code. Import a spec, map authentication, scope credentials per workspace, and the agent can call those endpoints inside Business Flows.",
        "Already have APIs? Point Qefro at them. Import an OpenAPI document and your endpoints become secure, callable tools — the fastest way to give an agent real capabilities.",
        [
            ("file", "Import OpenAPI spec", "Upload a spec and generate typed tools automatically."),
            ("globe", "REST endpoints", "Configure individual REST calls with headers, auth, and parameters."),
            ("shield", "Encrypted credentials", "API keys and tokens are encrypted and never shown to the model."),
            ("lock", "Scoped per workspace", "Each workspace gets its own credentials and permissions."),
        ],
        ["OpenAPI spec", "Business Tool", "Your API", "Result"],
        [("sdk", "SDK"), ("business-tools", "Business Tools"), ("integrations", "Integrations"), ("business-flows", "Business Flows")],
    ),
    (
        "Enterprise | AI Business Application Platform at scale | Qefro",
        "Keep your systems. Add the AI application layer.",
        "enterprise.html",
        "Deploy Qefro self-hosted or in the cloud with tenant isolation, RBAC, audit and execution logs, human approvals, and governed integrations to ERP, CRM, HR, and billing systems.",
        f'{ICONS["building"]} Enterprise',
        "Qefro Enterprise adds the AI application layer on systems you keep: External SDK Connections, managed apps, Organization Workflows, isolation, governance, auditability, and flexible deployment — self-hosted or cloud.",
        "Enterprise automation has to be trustworthy. Qefro keeps humans in control with approvals, records every tool call, isolates every tenant, and runs where your compliance requires — in your cloud or ours.",
        [
            ("server", "Self-hosted or cloud", "Run in your own infrastructure or on Qefro Cloud — same platform, your choice."),
            ("shield", "Tenant isolation &amp; RBAC", "Isolated data per tenant, role-based access, and per-workspace permissions."),
            ("file", "Audit &amp; execution logs", "Every conversation, decision, and tool call is recorded for review."),
            ("lock", "Governed automation", "Human approvals, challenge/resume, and encrypted secrets by default."),
        ],
        ["Conversation", "Governed AI", "Approved execution", "Business outcome"],
        [("security", "Security"), ("business-tools", "Business Tools"), ("partners", "Partners"), ("contact", "Talk to our team")],
    ),
    (
        "Partners | Build and deliver AI automation | Qefro",
        "Build and deliver AI automation with Qefro",
        "partners.html",
        "Partner with Qefro to deliver AI business applications — solution partners, technology integrations, referral, and co-selling programs for agencies, ISVs, and system integrators.",
        f'{ICONS["star"]} Partners',
        "The Qefro Partner Program supports agencies, system integrators, and technology vendors who build, deploy, and resell AI automation — with SDKs, documentation, and co-selling support.",
        "Qefro is built to be integrated. Partners extend it with new Business Tools, deliver automation to their customers, and grow with a platform designed for conversation-to-completion outcomes.",
        [
            ("building", "Solution partners", "Agencies and SIs that design and deploy Business Flows for customers."),
            ("server", "Technology partners", "ISVs that expose their product as Business Tools and integrations."),
            ("star", "Referral program", "Refer customers and earn on qualified opportunities."),
            ("chart", "Co-selling", "Joint go-to-market with enterprise sales support."),
        ],
        [],
        [("enterprise", "Enterprise"), ("sdk", "SDK"), ("docs", "Documentation"), ("contact", "Talk to our team")],
    ),
    (
        "WhatsApp | Complete business processes on WhatsApp | Qefro",
        "Complete business processes on WhatsApp",
        "whatsapp.html",
        "Run Qefro AI agents on WhatsApp Business — answer from your knowledge, execute Business Flows, call your systems securely, and pause for human approval, all in the chat your customers already use.",
        f'{ICONS["msg"]} WhatsApp',
        "Qefro on WhatsApp is the same automation platform on a channel your customers already use: grounded answers, multi-step Business Flows, secure tool calls, and human approvals — not just autoreplies.",
        "Most WhatsApp bots deflect. Qefro completes — a customer can change an order, track a shipment, or start a claim on WhatsApp and the process runs to completion across your systems.",
        [
            ("msg", "WhatsApp Business", "Official WhatsApp Business integration for customer conversations."),
            ("sparkles", "Knowledge answers", "Grounded, cited answers from your business knowledge."),
            ("zap", "Business Flows on WhatsApp", "Execute multi-step processes directly in the chat."),
            ("shield", "Human approval", "Pause for approval on sensitive steps before they run."),
        ],
        ["WhatsApp", "Qefro", "Business systems", "Completed task"],
        [("voice-ai", "Voice AI"), ("business-flows", "Business Flows"), ("integrations", "Integrations"), ("how-it-works", "Platform")],
    ),
]

for _t, _h1, _slug, _desc, _badge, _answer, _intro, _cards, _steps, _related in LANDING_PAGES:
    PAGES[_slug] = inner(
        _t,
        _h1,
        _desc,
        _slug,
        None,
        f"<p>{_answer}</p>",
        landing_body(_intro, _cards, _steps, _related),
        badge=_badge,
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
            faq_item_html(q, a, f"{landing.slug}-faq", i, raw=False)
            for i, (q, a) in enumerate(landing.faqs)
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
            Connect systems or install apps once in the Admin Console, then deploy across
            <strong>Website</strong>, <strong>WhatsApp</strong>, <strong>Internal Portal</strong>, and
            <strong>API</strong> channels — with the same retrieval, permissions, and tool layer underneath.
            Customer support chat is one application on that platform — not the whole product.
          </p>
          <p>
            Answers are grounded in your documents and crawled pages. Hybrid search combines
            keyword and vector retrieval, returns source citations, and is designed to decline
            when nothing relevant exists — so teams can trust support and internal assistants
            in production.
          </p>
          <p>
            When chat must change state — order lookups, tickets, CRM updates — connect your
            APIs via REST/OpenAPI or an External SDK Connection. Credentials are encrypted; outbound calls
            use HTTPS with SSRF protections; execution logs support review and QA.
          </p>
          <h2>Why teams choose Qefro for this use case</h2>
          <p>
            You should not rebuild RAG infrastructure, hosting, or channel adapters for every
            project. Qefro gives organizations a multi-tenant AI Business Application Platform: isolated
            knowledge per workspace, RBAC for owners/admins/members, PII scrubbing on model
            calls, and a 14-day free trial so you can prove value before choosing a paid plan.
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
            "logistics, retail, and more — built as applications on Qefro’s AI Business Application Platform."
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

        landing_jsonld = [
            webpage_json(landing.title, landing.description, path),
            breadcrumb_json(crumb_json),
            speakable_json(path),
        ]
        if landing.faqs:
            landing_jsonld.append(faq_schema(landing.faqs))

        PAGES[path] = page(
            title=landing.title,
            description=landing.description,
            path=path,
            active=active,
            jsonld=landing_jsonld,
            body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs(crumb_nav)}
        <div class="page-hero-inner">
          <span class="badge badge-indigo">{badge}</span>
          <h1>{escape(landing.h1)}</h1>
          <aside class="quick-answer-card" aria-label="Quick Summary">
            <span class="quick-answer-badge">{ICONS["sparkles"]} Quick Answer</span>
            <div style="text-align:left">{landing.answer}</div>
          </aside>
        </div>
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
        <span class="badge badge-indigo">{ICONS["sparkles"]} AI Business Platform</span>
        <h2>Try {escape(landing.h1)} with Qefro.</h2>
        <p>Start your 14-day free trial. Choose apps, connect your business, and experience the outcome.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">{CTA_TRIAL} {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Talk to Sales</a>
          <a class="btn btn-link btn-lg" href="/business-apps">{CTA_MARKETPLACE}</a>
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
Allow: /llms.txt
Allow: /llms-full.txt

# Explicitly allow rendering resources (Google recommends not blocking these).
Allow: /assets/

# Custom 404 is not for indexing (also noindex in HTML + true HTTP 404 from nginx).
Disallow: /404
Disallow: /404.html

Sitemap: {SITE}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(content, encoding="utf-8")
    print("wrote robots.txt")


def write_llms_full_txt() -> None:
    """Generate comprehensive llms-full.txt plain-text digest for LLM crawlers."""
    llms_path = ROOT / "llms.txt"
    base_llms = llms_path.read_text(encoding="utf-8") if llms_path.is_file() else ""

    sections = [base_llms.strip(), "\n\n# Expanded Landing Specifications & Direct Answers\n"]

    for landing in all_landings():
        url = site_url(landing.slug)
        sections.append(f"\n## {landing.h1} ({url})")
        sections.append(f"Kind: {landing.kind.capitalize()}")
        sections.append(f"Title: {landing.title}")
        sections.append(f"Description: {landing.description}")
        clean_answer = re.sub(r"<[^>]+>", "", landing.answer).strip()
        sections.append(f"Direct Answer: {clean_answer}")
        if landing.paragraphs:
            sections.append("Overview: " + " ".join(landing.paragraphs))
        if landing.bullets:
            sections.append("Key Capabilities:\n" + "\n".join(f"- {b}" for b in landing.bullets))
        if landing.faqs:
            sections.append("FAQs:")
            for q, a in landing.faqs:
                clean_a = re.sub(r"<[^>]+>", "", a).strip()
                sections.append(f"  Q: {q}\n  A: {clean_a}")

    content = "\n".join(sections) + "\n"
    (ROOT / "llms-full.txt").write_text(content, encoding="utf-8")
    print("wrote llms-full.txt")


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
    write_llms_full_txt()
    for name, html in PAGES.items():
        (ROOT / name).write_text(html, encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    write_all()
