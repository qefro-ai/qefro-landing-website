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
ASSET_VERSION = "47"
OG_IMAGE = f"{SITE}/assets/images/og-cover.png"
OG_IMAGE_ALT = (
    "Qefro — AI Business Application Platform. Connect your systems, "
    "build intelligent applications, and automate your organization."
)
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
    "AI business application platform, AI business applications, "
    "business automation platform, AI workflow automation, AI SDK, "
    "enterprise AI integrations, AI application platform, "
    "external SDK connection, managed marketplace apps, organization workflows"
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
    ("sdk", "Developers"),
    ("use-cases", "Applications"),
    ("security", "Security"),
    ("pricing", "Pricing"),
]

# Canonical indexable URLs for sitemap (extensionless; nginx 301s .html → these).
# Images listed here are included via the image sitemap extension.
SITEMAP_ENTRIES: list[tuple[str, list[tuple[str, str]]]] = [
    ("", [(f"{SITE}/assets/images/og-cover.png", "Qefro AI Business Application Platform")]),
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
    page_og_alt = escape(f"Qefro AI Platform — {title}")
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
        <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI Business Application Platform logo" width="40" height="40" decoding="async" fetchpriority="high" />
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
        <a class="btn btn-primary" href="{PORTAL_SIGNUP}">Build with Qefro {ICONS["arrow"]}</a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-nav-panel">{ICONS["menu"]}</button>
      </div>
    </div>
    <div class="mobile-panel wrap" id="mobile-nav-panel">
{mobile}
      <a href="/faq">FAQ</a>
      <a href="{DOCS}" rel="noopener noreferrer">Docs</a>
      <a class="btn btn-primary" href="{PORTAL_SIGNUP}" style="justify-content:center;margin-top:0.5rem">Build with Qefro</a>
      <a href="{PORTAL_LOGIN}">Sign In</a>
      <div class="mobile-panel-tools">
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to dark mode">
          <span class="icon-moon" aria-hidden="true">{ICONS["moon"]}</span>
          <span class="icon-sun" aria-hidden="true">{ICONS["sun"]}</span>
        </button>
      </div>
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
            <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI Business Application Platform logo" width="40" height="40" decoding="async" />
            <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" decoding="async" />
          </a>
          <p class="footer-tagline">AI Business Application Platform</p>
        </div>
        <nav class="footer-col" aria-label="Platform">
          <h3>Platform</h3>
          <a href="/how-it-works">How it works</a>
          <a href="/features">Capabilities</a>
          <a href="/#customer-hub">Customer Hub</a>
          <a href="/workflow-engine">Organization Workflows</a>
          <a href="/#channels">Channels</a>
          <a href="/security">Security</a>
        </nav>
        <nav class="footer-col" aria-label="Developers">
          <h3>Developers</h3>
          <a href="/sdk">SDK</a>
          <a href="/sdk">External Connections</a>
          <a href="/integrations">Integrations</a>
          <a href="{DOCS}">Documentation</a>
          <a href="/api">API</a>
        </nav>
        <nav class="footer-col" aria-label="Applications">
          <h3>Applications</h3>
          <a href="/use-cases">All applications</a>
          <a href="/ai-customer-support-for-restaurants">Restaurant</a>
          <a href="/ai-customer-support-for-clinics">Healthcare</a>
          <a href="/enterprise">Enterprise</a>
          <a href="/sdk">Build a custom app</a>
        </nav>
        <nav class="footer-col" aria-label="Company">
          <h3>Company</h3>
          <a href="/what-is-qefro">About</a>
          <a href="/contact">Contact</a>
          <a href="/pricing">Pricing</a>
          <a href="/partners">Partners</a>
          <a href="/privacy">Privacy</a>
          <a href="/terms">Terms</a>
          <a href="/llms.txt">llms.txt</a>
        </nav>
      </div>
      <div class="footer-bottom">
        <p>© <span data-year></span> Qefro. All rights reserved.</p>
        <p>Connect your systems. Build intelligent applications. Automate your organization.</p>
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
            "Qefro is the AI Business Application Platform. "
            "Connect existing business systems, build AI-powered applications, "
            "and automate workflows across your organization with External SDK Connections, "
            "Managed Marketplace Apps, Customer Hub, and Organization Workflows."
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
            "AI business application platform",
            "External SDK connections",
            "Managed marketplace applications",
            "Organization workflow automation",
            "Customer Hub identity",
            "Enterprise system integration",
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
            "Qefro is the AI Business Application Platform. "
            "Connect your systems, build intelligent applications, and automate your organization."
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
            "Qefro is the AI Business Application Platform. "
            "Connect ERP/CRM systems via External SDK Connections, deploy Managed Marketplace Apps, "
            "and automate organization workflows — with Customer Hub, channels, and RBAC."
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
            "External SDK Connections (/qefro protocol)",
            "Managed Marketplace Applications",
            "Organization Workflows, approvals, and tasks",
            "Customer Hub identity layer",
            "AI tool execution against your backends",
            "Website, WhatsApp, Internal Portal, and API channels",
            "Workspace model with RBAC and teams",
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
            "AI Business Application Platform with External SDK Connections, "
            "Managed Marketplace Apps, Customer Hub, workflows, and channels."
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
                "name": "Pro",
                "price": 49,
                "priceCurrency": "USD",
                "description": "Billed annually ($59/month if billed monthly)",
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

ENTERPRISE_FAIR_USE_NOTE = (
    '<p class="price-desc price-fair-use">'
    "Enterprise is a custom capacity contract — seats, messages, documents, storage, and tools are quoted to your requirements. "
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
    return f"""          <article class="price-card{cta}">
            <h3>Trial (14 Days)</h3>
            <p class="price-best">Best for evaluating the platform</p>
            <div class="price-amount">$0</div>
            <p class="price-desc">14-day free trial — no credit card</p>
            <ul class="price-feats">
              {price_feat("Full premium access for 14 days")}
              {price_feat("Applications, channels &amp; workflows")}
              {price_feat("Knowledge base, crawler &amp; uploads")}
              {price_feat("Team management &amp; analytics")}
              {price_feat("SDK connections &amp; business tools")}
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
              {price_feat("10,000 AI Messages / month")}
              {price_feat("Knowledge for one team", "50 documents")}
              {price_feat("Connect up to 5 business systems")}
              {price_feat("Widget + WhatsApp")}
              {price_feat("Custom branding")}
              {price_feat("Email support")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>Get Started</a>
          </article>
          <article class="price-card is-popular{cta}">
            <div class="price-pop">{ICONS["star"]} Most Popular</div>
            <h3>Pro</h3>
            <p class="price-best">Best for scaling teams</p>
            <div class="price-amount" data-price-annual="$49" data-price-monthly="$59">$49 <span>/month</span></div>
            <p class="price-billed">billed annually · or $59/mo monthly</p>
            <p class="price-desc">For teams past startup volume</p>
            <ul class="price-feats">
              {price_feat("30,000 AI Messages / month")}
              {price_feat("Knowledge for growing teams", "200 documents")}
              {price_feat("10 team members")}
              {price_feat("Connect up to 25 business systems")}
              {price_feat("Widget + WhatsApp + voice")}
              {price_feat("Analytics &amp; agent handoff")}
              {price_feat("Email support")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>Get Pro</a>
          </article>
          <article class="price-card{cta}">
            <h3>Growth</h3>
            <p class="price-best">Best for growing companies</p>
            <div class="price-amount" data-price-annual="$99" data-price-monthly="$119">$99 <span>/month</span></div>
            <p class="price-billed">billed annually · or $119/mo monthly</p>
            <p class="price-desc">For teams deploying across channels</p>
            <ul class="price-feats">
              {price_feat("60,000 AI Messages / month")}
              {price_feat("Knowledge across teams", "500 documents")}
              {price_feat("20 team members")}
              {price_feat("Widget + WhatsApp + voice")}
              {price_feat("Unlimited business system connections")}
              {price_feat("Analytics &amp; agent handoff")}
              {price_feat("Priority support")}
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_get_started")}>Get Started</a>
          </article>
          <article class="price-card{cta}">
            <h3>Enterprise</h3>
            <p class="price-best">Best for regulated organizations</p>
            <div class="price-amount">Custom</div>
            <p class="price-desc">Pay for the capacity you need</p>
            <ul class="price-feats">
              {price_feat("Custom AI Messages")}
              {price_feat("Custom documents &amp; seats")}
              {price_feat("Custom Business Tools &amp; storage")}
              {price_feat("WhatsApp + Voice AI")}
              {price_feat("Private deployment")}
              {price_feat("Dedicated CSM")}
              {price_feat("Custom SLA")}
              {price_feat("SSO &amp; SAML (roadmap)")}
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
        "Qefro is the AI Business Application Platform. Connect existing business systems through External "
        "SDK Connections, build Managed Marketplace Apps, and automate Organization Workflows — with "
        "Customer Hub, channels (Website, WhatsApp, Portal, API), workspaces, and RBAC on one platform. "
        "Customer support chat is one use case, not the definition of Qefro.",
    ),
    ("How much does Qefro cost?", "Every new organization gets a 14-day free trial with full premium access. No credit card required. Starter is $29/month billed annually ($39 monthly, connect up to 5 business systems). Pro is $49/month billed annually ($59 monthly, up to 25 business systems). Growth is $99/month billed annually ($119 monthly, unlimited business system connections). Enterprise is custom capacity priced to your requirements."),
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
        "Yes. Connect existing APIs as Business Tools (REST/OpenAPI) or run an External SDK Connection in your backend. AI applications can search products, create quotations, open tickets, and more — with encrypted credentials or end-user identity you forward via identify().",
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
    ("Do you offer enterprise pricing?", "Yes. Enterprise is a custom capacity contract — seats, messages, documents, storage, crawls, and business tools are quoted to your needs — plus private deployment, dedicated support, and custom SLAs. SSO/SAML is on the roadmap — talk to sales about your timeline."),
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
def home_faq_preview(n: int = 8) -> str:
    return "".join(
        faq_item_html(q, a, "home-faq", i) for i, (q, a) in enumerate(FAQ_ITEMS[:n])
    )


def home_body() -> str:
    return f"""    <section class="hero hero-platform" aria-label="Hero" data-motion="hero">
      <div class="hero-grid" aria-hidden="true"></div>
      <div class="wrap-5xl hero-platform-grid">
        <div class="hero-copy">
          <span class="eyebrow" data-motion="hero-badge">{ICONS["sparkles"]} AI BUSINESS APPLICATION PLATFORM</span>
          <h1 data-motion="hero-title">
            <span class="hero-line">Connect Your Systems.</span>
            <span class="hero-line">Build Intelligent Applications.</span>
            <span class="hero-line">Automate Your Organization.</span>
          </h1>
          <p class="hero-sub" data-motion="hero-sub">Connect your existing business systems, build AI-powered applications, and automate work across teams&mdash;all on one platform.</p>
          <div class="hero-actions" data-motion="hero-actions">
            <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_build_qefro">Build with Qefro {ICONS["arrow"]}</a>
            <a class="btn btn-ghost btn-lg" href="/contact" data-clarity-event="cta_talk_sales">Talk to Sales</a>
            <a class="btn btn-link btn-lg" href="/sdk" data-clarity-event="cta_explore_sdk">Explore the SDK</a>
          </div>
          <div class="hero-checks" data-motion="hero-checks">
            <span>{ICONS["check"]} External SDK Connections</span>
            <span>{ICONS["check"]} Managed Marketplace Apps</span>
            <span>{ICONS["check"]} Organization Workflows</span>
            <span>{ICONS["check"]} Customer Hub</span>
          </div>
        </div>
        <div class="hero-arch reveal" data-pillars aria-label="Qefro platform pillars">
          <div class="pillar-hub">QEFRO<span>AI Business Application Platform</span></div>
          <div class="pillar-tabs" role="tablist" aria-label="Platform pillars">
            <button type="button" class="pillar-tab is-active" role="tab" aria-selected="true" data-pillar="connect">Connect</button>
            <button type="button" class="pillar-tab" role="tab" aria-selected="false" data-pillar="build">Build</button>
            <button type="button" class="pillar-tab" role="tab" aria-selected="false" data-pillar="automate">Automate</button>
          </div>
          <div class="pillar-panels">
            <div class="pillar-panel is-active" data-pillar-panel="connect" role="tabpanel">
              <ul class="pillar-list">
                <li>ERP / CRM</li>
                <li>APIs &amp; Databases</li>
                <li>SDK Connectors</li>
                <li>On-premise systems</li>
              </ul>
            </div>
            <div class="pillar-panel" data-pillar-panel="build" role="tabpanel" hidden>
              <ul class="pillar-list">
                <li>Restaurant Pro</li>
                <li>Clinic Pro</li>
                <li>Finance &amp; Sales</li>
                <li>Custom Marketplace Apps</li>
              </ul>
            </div>
            <div class="pillar-panel" data-pillar-panel="automate" role="tabpanel" hidden>
              <ul class="pillar-list">
                <li>Events &amp; Actions</li>
                <li>Approvals &amp; Tasks</li>
                <li>Organization Workflows</li>
                <li>Teams &amp; RBAC</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="pillars" aria-labelledby="three-ways-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Platform</span>
          <h2 id="three-ways-heading">One platform. Three ways to transform your business.</h2>
          <p>Qefro connects AI to your existing business systems, powers specialized business applications, and automates workflows across your organization.</p>
        </div>
        <div class="three-way-grid reveal">
          <article class="three-way-card">
            <h3>Connect</h3>
            <p class="three-way-lead">Bring your existing systems</p>
            <p>Connect ERP, CRM, inventory, pricing, databases and internal APIs through Qefro APIs or External SDK Connections.</p>
            <div class="mini-flow" aria-hidden="true"><span>Your Systems</span><span>{ICONS["arrow"]}</span><span>External SDK</span><span>{ICONS["arrow"]}</span><span>Qefro</span></div>
            <a class="btn btn-ghost" href="/integrations">Explore Integrations {ICONS["arrow"]}</a>
          </article>
          <article class="three-way-card">
            <h3>Build</h3>
            <p class="three-way-lead">Create AI-powered business applications</p>
            <p>Build specialized applications using the Qefro SDK or deploy applications through the Qefro Marketplace.</p>
            <div class="mini-chips" aria-label="Example applications"><span>Restaurant Pro</span><span>Clinic Pro</span><span>Finance</span><span>Sales</span><span>Operations</span></div>
            <a class="btn btn-ghost" href="/use-cases">Explore Applications {ICONS["arrow"]}</a>
          </article>
          <article class="three-way-card">
            <h3>Automate</h3>
            <p class="three-way-lead">Orchestrate work across your organization</p>
            <p>Connect business events, AI actions, approvals, tasks and teams through Organization Workflows.</p>
            <div class="mini-flow" aria-hidden="true"><span>Event</span><span>{ICONS["arrow"]}</span><span>Workflow</span><span>{ICONS["arrow"]}</span><span>Approval</span><span>{ICONS["arrow"]}</span><span>Action</span></div>
            <a class="btn btn-ghost" href="/workflow-engine">Explore Workflows {ICONS["arrow"]}</a>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="architecture" aria-labelledby="architecture-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["server"]} Architecture</span>
          <h2 id="architecture-heading">Your systems remain yours. Qefro makes them intelligent.</h2>
          <p>Keep your ERP, CRM, inventory and internal systems exactly where they belong. Qefro connects to them through secure SDK connections and APIs, while providing the AI and orchestration layer on top.</p>
        </div>
        <div class="arch-board reveal" aria-label="Qefro architecture">
          <div class="arch-row arch-top">
            <div class="arch-box arch-box-accent">QEFRO<span>AI + Applications</span></div>
          </div>
          <div class="arch-row">
            <div class="arch-box">Channels</div>
            <div class="arch-box">Workflows</div>
            <div class="arch-box">Applications</div>
          </div>
          <div class="arch-row">
            <div class="arch-box arch-box-wide">Qefro Runtime</div>
          </div>
          <div class="arch-row">
            <div class="arch-box arch-box-wide">Connector Layer</div>
          </div>
          <div class="arch-row">
            <div class="arch-box">External SDK<br/><small>Customer systems</small></div>
            <div class="arch-box">Managed Apps<br/><small>Qefro Marketplace</small></div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="build-your-way" aria-labelledby="build-way-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-green">{ICONS["file"]} Developers</span>
          <h2 id="build-way-heading">Build your way</h2>
          <p>Same application contract. Different deployment model.</p>
        </div>
        <div class="two-model-grid reveal">
          <article class="model-card">
            <h3>External SDK Connections</h3>
            <p>Run your application on your own infrastructure and connect it to Qefro.</p>
            <div class="mini-flow"><span>Your Infrastructure</span><span>{ICONS["arrow"]}</span><span>Your SDK App</span><span>{ICONS["arrow"]}</span><span>/qefro</span><span>{ICONS["arrow"]}</span><span>Qefro</span></div>
            <p class="model-best"><strong>Best for:</strong> ERP/CRM integrations, on-premise systems, enterprise infrastructure, sensitive backends.</p>
            <a class="btn btn-primary" href="/sdk">Build an SDK Connection {ICONS["arrow"]}</a>
          </article>
          <article class="model-card">
            <h3>Managed Marketplace Apps</h3>
            <p>Build applications that Qefro can host, distribute and manage.</p>
            <div class="mini-flow"><span>SDK Application</span><span>{ICONS["arrow"]}</span><span>Marketplace</span><span>{ICONS["arrow"]}</span><span>Workspace</span><span>{ICONS["arrow"]}</span><span>Managed Runtime</span></div>
            <p class="model-best"><strong>Best for:</strong> SaaS and vertical apps, reusable solutions, third-party developers, marketplace distribution.</p>
            <a class="btn btn-primary" href="/sdk">Build a Qefro App {ICONS["arrow"]}</a>
          </article>
        </div>
        <div class="compare-table-wrap reveal">
          <table class="compare-table">
            <caption class="sr-only">External SDK vs Managed App</caption>
            <thead><tr><th></th><th>External SDK</th><th>Managed App</th></tr></thead>
            <tbody>
              <tr><th scope="row">Runtime</th><td>Your infrastructure</td><td>Qefro</td></tr>
              <tr><th scope="row">Deployment</th><td>You</td><td>Qefro</td></tr>
              <tr><th scope="row">Marketplace</th><td>No</td><td>Yes</td></tr>
              <tr><th scope="row">Existing ERP</th><td>Excellent</td><td>Optional</td></tr>
              <tr><th scope="row">On-premise</th><td>Yes</td><td>No</td></tr>
              <tr><th scope="row">Scaling</th><td>You</td><td>Qefro</td></tr>
              <tr><th scope="row">Updates</th><td>You</td><td>Marketplace</td></tr>
              <tr><th scope="row">SDK</th><td>Same</td><td>Same</td></tr>
              <tr><th scope="row">/qefro protocol</th><td>Same</td><td>Same</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="erp-example" aria-labelledby="erp-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["building"]} Example</span>
          <h2 id="erp-heading">Turn an existing ERP into an AI sales assistant</h2>
          <p>Qefro doesn&rsquo;t replace your existing business systems. Connect them.</p>
        </div>
        <div class="flow-stack reveal" aria-label="ERP to AI sales flow">
          <div class="flow-step"><strong>Customer</strong><span>&ldquo;I need flooring for a 1,200 sq.ft house.&rdquo;</span></div>
          <div class="flow-step"><strong>Qefro AI</strong><span>Understands intent and calls business tools</span></div>
          <div class="flow-step"><strong>External SDK Connector</strong><span>Signed /qefro to your backend</span></div>
          <div class="flow-step"><strong>Product System</strong><span>Live product + pricing + inventory</span></div>
          <div class="flow-step"><strong>Quotation</strong><span>Calculated from your pricing rules</span></div>
          <div class="flow-step"><strong>Approval Workflow</strong><span>Sales manager when over threshold</span></div>
          <div class="flow-step flow-step-accent"><strong>Customer</strong><span>Confirmed quote &amp; next steps</span></div>
        </div>
        <div class="tool-strip reveal">
          <div class="tool-chip">Customer {ICONS["arrow"]} AI {ICONS["arrow"]} <code>abm.searchProducts</code> {ICONS["arrow"]} External SDK {ICONS["arrow"]} ERP</div>
          <div class="tool-chip">AI {ICONS["arrow"]} <code>abm.calculateQuotation</code> {ICONS["arrow"]} Pricing System {ICONS["arrow"]} Quotation</div>
          <p>AI doesn&rsquo;t need direct access to your databases. Your SDK application exposes controlled business capabilities as tools.</p>
        </div>
        <p class="integrations-note" style="text-align:center;margin-top:1.5rem"><a class="btn btn-primary" href="/how-it-works">See how it works {ICONS["arrow"]}</a></p>
      </div>
    </section>

    <section class="section" id="org-workflows" aria-labelledby="org-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["zap"]} Organization</span>
          <h2 id="org-heading">AI that works across teams</h2>
          <p>Applications stay independent. Qefro orchestrates the work between them.</p>
        </div>
        <div class="pipeline pipeline-flow reveal" aria-label="Cross-team workflow">
          <span class="pipeline-node"><span class="pipeline-v">Sales</span><span class="pipeline-d">Quote requested</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node"><span class="pipeline-v">Workflow</span><span class="pipeline-d">Qefro</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node"><span class="pipeline-v">Finance</span><span class="pipeline-d">Approval</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node"><span class="pipeline-v">Operations</span><span class="pipeline-d">Action</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node pipeline-node-accent"><span class="pipeline-v">Customer</span><span class="pipeline-d">Complete</span></span>
        </div>
        <div class="cap-pills reveal">{ICONS["check"]} Events · Actions · Tasks · Approvals · Teams · Workflows</div>
        <p class="integrations-note" style="text-align:center;margin-top:1.25rem"><a href="/workflow-engine">Explore Organization Workflows {ICONS["arrow"]}</a></p>
      </div>
    </section>

    <section class="section section-alt" id="customer-hub" aria-labelledby="hub-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-green">{ICONS["globe"]} Customer Hub</span>
          <h2 id="hub-heading">One customer identity across your applications</h2>
          <p>Customer Hub owns people and identity. Applications own their domain relationships.</p>
        </div>
        <div class="hub-diagram reveal">
          <div class="hub-center">Customer Hub<span>Identity · Timeline · Consent · Memberships · Attributes</span></div>
          <div class="hub-apps"><span>Sales</span><span>Restaurant</span><span>Support</span></div>
        </div>
      </div>
    </section>

    <section class="section" id="applications" aria-labelledby="apps-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["sparkles"]} Applications</span>
          <h2 id="apps-heading">Business applications, not generic AI wrappers</h2>
          <p>Every application gets the same platform foundation&mdash;AI, Customer Hub, Workflows, Storage, Channels, and RBAC.</p>
        </div>
        <div class="app-card-grid reveal">
          <article class="app-card"><h3>Restaurant Pro</h3><p>Reservations · Menu · Kitchen · Marketing</p></article>
          <article class="app-card"><h3>Clinic Pro</h3><p>Doctors · Appointments · Availability</p></article>
          <article class="app-card"><h3>Finance</h3><p>Invoices · Approvals · Finance workflows</p></article>
          <article class="app-card"><h3>Custom Applications</h3><p>Build your own with the Qefro SDK</p></article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="channels" aria-labelledby="channels-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["msg"]} Channels</span>
          <h2 id="channels-heading">Meet customers where they already are</h2>
          <p>Website, WhatsApp and internal tools are interaction channels&mdash;not separate systems.</p>
        </div>
        <div class="channel-row reveal">
          <span class="channel-pill">Website</span>
          <span class="channel-pill">WhatsApp</span>
          <span class="channel-pill">Internal Portal</span>
          <span class="channel-pill">API</span>
          <span class="channel-arrow">{ICONS["arrow"]}</span>
          <span class="channel-pill channel-pill-accent">Qefro Applications</span>
        </div>
      </div>
    </section>

    <section class="section" id="developers" aria-labelledby="dev-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-green">{ICONS["file"]} SDK</span>
          <h2 id="dev-heading">Build on Qefro</h2>
          <p>Connect an existing backend or build a complete business application using the Qefro SDK.</p>
        </div>
        <div class="dev-grid reveal">
          <div>
            <div class="lang-row"><span>JavaScript</span><span>Rust</span><span>Python</span></div>
            <div class="mini-flow" style="margin:1rem 0"><span>SDK</span><span>{ICONS["arrow"]}</span><span>Tools</span><span>{ICONS["arrow"]}</span><span>Capabilities</span><span>{ICONS["arrow"]}</span><span>Runtime</span></div>
            <div class="hero-actions">
              <a class="btn btn-primary" href="{DOCS}">Read the Documentation {ICONS["arrow"]}</a>
              <a class="btn btn-ghost" href="/sdk">Build an SDK Connection</a>
            </div>
          </div>
          <pre class="code-panel" tabindex="0"><code>import {{ Qefro }} from '@qefro-ai/backend'

const app = new Qefro({{ signingSecret: process.env.QEFRO_SIGNING_SECRET }})

app.tool(
  {{
    name: 'abm.searchProducts',
    description: 'Search catalog by query, category, or brand',
    auth: 'none',
    input_schema: {{
      type: 'object',
      properties: {{
        query: {{ type: 'string' }},
        category: {{ type: 'string' }},
      }},
    }},
  }},
  async (ctx) =&gt; {{
    // Your ERP / product system — controlled capability
    return {{ products: await search(ctx.parameters) }}
  }},
)</code></pre>
        </div>
        <p class="integrations-note reveal" style="margin-top:1rem">AI {ICONS["arrow"]} Tool {ICONS["arrow"]} Your Backend {ICONS["arrow"]} Your System</p>
      </div>
    </section>

    <section class="section section-alt" id="security" aria-labelledby="sec-home-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["shield"]} Security</span>
          <h2 id="sec-home-heading">Enterprise systems stay under your control</h2>
          <p>Qefro connects to your systems without requiring you to hand over your core business infrastructure.</p>
        </div>
        <div class="sec-grid reveal">
          <article><h3>Tenant isolation</h3><p>Organization boundaries enforced end to end.</p></article>
          <article><h3>Workspace isolation</h3><p>Apps, teams, and channels scoped per workspace.</p></article>
          <article><h3>RBAC</h3><p>Role-based access for teams and staff portals.</p></article>
          <article><h3>Signed SDK connections</h3><p>Authenticated /qefro protocol to your backends.</p></article>
          <article><h3>Controlled tool access</h3><p>Only the capabilities you expose as tools.</p></article>
          <article><h3>On-premise option</h3><p>External SDK keeps sensitive systems on your infra.</p></article>
        </div>
        <p class="integrations-note" style="text-align:center;margin-top:1.25rem"><a href="/security">Security details {ICONS["arrow"]}</a></p>
      </div>
    </section>

    <section class="section" id="use-cases-home" aria-labelledby="uc-home-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["building"]} Use cases</span>
          <h2 id="uc-home-heading">Built for the way businesses actually work</h2>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card"><h3>Sales</h3><ul><li>Product discovery</li><li>Quotation</li><li>Approval</li></ul></article>
          <article class="outcome-card"><h3>Customer Operations</h3><ul><li>Website / WhatsApp</li><li>Customer identity</li><li>Action</li></ul></article>
          <article class="outcome-card"><h3>Healthcare</h3><ul><li>Appointment</li><li>Availability</li><li>Staff workflow</li></ul></article>
          <article class="outcome-card"><h3>Restaurants</h3><ul><li>Booking</li><li>Kitchen</li><li>Customer</li></ul></article>
          <article class="outcome-card"><h3>Finance</h3><ul><li>Request</li><li>Approval</li><li>Execution</li></ul></article>
          <article class="outcome-card"><h3>Enterprise Integrations</h3><ul><li>ERP / CRM</li><li>SDK</li><li>AI + workflows</li></ul></article>
        </div>
        <p class="integrations-note" style="text-align:center;margin-top:1.25rem"><a href="/use-cases">Explore Applications {ICONS["arrow"]}</a></p>
      </div>
    </section>

    <section class="section section-alt" id="marketplace" aria-labelledby="mkt-heading">
      <div class="wrap-5xl">
        <div class="two-band reveal">
          <div>
            <span class="badge badge-green">{ICONS["sparkles"]} Marketplace</span>
            <h2 id="mkt-heading">A platform for business applications</h2>
            <p>Developers can build specialized applications on Qefro and distribute them through the Marketplace.</p>
            <div class="mini-flow"><span>Developer</span><span>{ICONS["arrow"]}</span><span>SDK</span><span>{ICONS["arrow"]}</span><span>App</span><span>{ICONS["arrow"]}</span><span>Marketplace</span><span>{ICONS["arrow"]}</span><span>Workspace</span></div>
            <a class="btn btn-primary" href="/sdk">Build an App {ICONS["arrow"]}</a>
          </div>
          <div>
            <span class="badge badge-indigo">{ICONS["server"]} External SDK</span>
            <h2>Connect your existing backend in hours</h2>
            <p>Your infrastructure stays yours. Expose only the capabilities Qefro needs.</p>
            <div class="mini-flow"><span>Your API / ERP</span><span>{ICONS["arrow"]}</span><span>Qefro SDK</span><span>{ICONS["arrow"]}</span><span>/qefro</span><span>{ICONS["arrow"]}</span><span>Qefro</span></div>
            <a class="btn btn-ghost" href="/sdk">Explore External SDK Connections {ICONS["arrow"]}</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="capabilities" aria-labelledby="caps-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <h2 id="caps-heading">Platform capabilities</h2>
        </div>
        <div class="cap-grid reveal">
          <article><h3>AI</h3><p>Grounded answers and tool calling across channels.</p></article>
          <article><h3>Applications</h3><p>Managed and custom business apps on one runtime.</p></article>
          <article><h3>SDK</h3><p>External connections with the /qefro protocol.</p></article>
          <article><h3>Customer Hub</h3><p>Identity layer shared across applications.</p></article>
          <article><h3>Workflows</h3><p>Events, approvals, tasks, and team handoffs.</p></article>
          <article><h3>Marketing</h3><p>Campaign capabilities for installed apps.</p></article>
          <article><h3>Storage</h3><p>App-scoped storage for managed solutions.</p></article>
          <article><h3>Channels</h3><p>Website, WhatsApp, portal, and API.</p></article>
          <article><h3>RBAC</h3><p>Roles and permissions for organizations.</p></article>
          <article><h3>Marketplace</h3><p>Distribute and install vertical applications.</p></article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="pricing" aria-labelledby="pricing-heading">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["chart"]} Pricing</span>
          <h2 id="pricing-heading">Platform plans for teams that build</h2>
          <p>Platform access, applications, and usage that scale with your organization.</p>
        </div>
{price_cards_html(interactive=True)}
        <p class="integrations-note reveal" style="text-align:center;margin-top:1.5rem"><a href="/pricing">Compare plans in detail {ICONS["arrow"]}</a></p>
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
        <span class="badge badge-indigo">{ICONS["sparkles"]} Build with Qefro</span>
        <h2 id="cta-heading">Build the AI layer for your business.</h2>
        <p>Connect your systems. Build intelligent applications. Automate the work between them.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_build_qefro">Build with Qefro {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact" data-clarity-event="cta_talk_sales">Talk to Sales</a>
          <a class="btn btn-link btn-lg" href="{DOCS}" data-clarity-event="cta_read_docs">Explore the SDK</a>
        </div>
      </div>
    </section>
"""


PAGES["index.html"] = page(
    title="Qefro — AI Business Application Platform",
    description=(
        "Connect your systems. Build intelligent applications. Automate your organization. "
        "Qefro is the AI Business Application Platform for External SDK Connections, "
        "Managed Marketplace Apps, Customer Hub, and Organization Workflows."
    ),
    path="",
    jsonld=[
        ORG_JSON,
        WEBSITE_JSON,
        SOFTWARE_JSON,
        webpage_json(
            "Qefro — AI Business Application Platform",
            "Connect your systems. Build intelligent applications. Automate your organization.",
            "",
        ),
    ],
    body=home_body(),
    extra_scripts='',
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
          <article class="workspace-card"><h3>Connect</h3><p>External SDK Connections and REST/OpenAPI tools against systems you already run.</p></article>
          <article class="workspace-card"><h3>Build</h3><p>Managed Marketplace Apps or your own SDK applications in a workspace.</p></article>
          <article class="workspace-card"><h3>Automate</h3><p>Organization Workflows for events, approvals, tasks, and handoffs.</p></article>
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
          <article class="three-way-card"><h3>1. Connect</h3><p>Register an External SDK Connection or REST/OpenAPI tools against your ERP, CRM, or APIs.</p></article>
          <article class="three-way-card"><h3>2. Build</h3><p>Install a Managed Marketplace App or ship your own SDK application into a workspace.</p></article>
          <article class="three-way-card"><h3>3. Automate</h3><p>Wire Organization Workflows for events, approvals, tasks, and team handoffs.</p></article>
        </div>
        <div class="pipeline pipeline-flow reveal" aria-label="Platform flow">
          <span class="pipeline-node"><span class="pipeline-v">Your systems</span><span class="pipeline-d">ERP / CRM / APIs</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node"><span class="pipeline-v">SDK /qefro</span><span class="pipeline-d">Signed tools</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node"><span class="pipeline-v">Qefro runtime</span><span class="pipeline-d">AI + workflows</span></span>
          <div class="pipeline-arrow" aria-hidden="true">{ICONS["arrow"]}</div>
          <span class="pipeline-node pipeline-node-accent"><span class="pipeline-v">Channels</span><span class="pipeline-d">Web · WhatsApp · Portal · API</span></span>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3rem">
          <h2>Configure once. Deploy across channels.</h2>
          <p>Workspaces bound applications, teams, channels, and customers. The Admin Console is where you connect systems, install apps, and govern access.</p>
        </div>
        <div class="steps-grid reveal">
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">01</div></div><h3>Create organization &amp; workspace</h3><p>Set the operational boundary for apps, teams, and channels.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">02</div></div><h3>Connect systems or install apps</h3><p>External SDK Connection or Managed Marketplace App — same /qefro contract.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">03</div></div><h3>Enable channels</h3><p>Website widget, WhatsApp, Internal Portal, and API — all to the same applications.</p></article>
          <article class="step tilt-3d"><div class="step-num-wrap"><div class="step-num-inner">04</div></div><h3>Automate across teams</h3><p>Organization Workflows for events, approvals, and tasks between applications.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>What we handle for you</h2>
          <p>Retrieval, model hosting, PII scrubbing, rate limits, and tool orchestration — you focus on systems, apps, and permissions.</p>
        </div>
"""

def use_cases_page_content() -> str:
    return f"""        <div class="uc-grid reveal">
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["chart"]}</div><h3>Sales</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Product search and quotations</li><li>{ICONS["chevr"]} CRM lookups via SDK tools</li><li>{ICONS["chevr"]} Lead capture across channels</li><li>{ICONS["chevr"]} Approval workflows for quotes</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["zap"]}</div><h3>Operations</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Order and shipment actions</li><li>{ICONS["chevr"]} Ticketing and escalations</li><li>{ICONS["chevr"]} Cross-team task handoffs</li><li>{ICONS["chevr"]} Audit-ready execution logs</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["shield"]}</div><h3>Healthcare</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Clinic Pro application</li><li>{ICONS["chevr"]} Policy and protocol lookup</li><li>{ICONS["chevr"]} Staff Internal Portal</li><li>{ICONS["chevr"]} PII scrubbing on model calls</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["building"]}</div><h3>Restaurants</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Restaurant Pro application</li><li>{ICONS["chevr"]} Menu and location knowledge</li><li>{ICONS["chevr"]} Reservations and FAQs</li><li>{ICONS["chevr"]} WhatsApp + website channels</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["file"]}</div><h3>Finance</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Policy and procedure answers</li><li>{ICONS["chevr"]} Approval-gated actions</li><li>{ICONS["chevr"]} Workspace-scoped secrets</li><li>{ICONS["chevr"]} Tenant isolation by design</li></ul></article>
          <article class="uc-card tilt-3d"><div class="uc-head"><div class="uc-icon">{ICONS["server"]}</div><h3>Enterprise integrations</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} ERP / CRM External SDK Connections</li><li>{ICONS["chevr"]} On-prem capable backends</li><li>{ICONS["chevr"]} Organization Workflows</li><li>{ICONS["chevr"]} RBAC across teams and apps</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["zap"]} Platform in action</span>
          <h2>Applications on a shared foundation</h2>
          <p>Customer support chat is one application pattern. Sales assistants, Clinic Pro, Restaurant Pro, and custom SDK apps all share AI, Customer Hub, workflows, and channels.</p>
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
    return f"""        <div class="direct-answer reveal">
          <p>Every new organization gets a <strong>14-day free trial</strong> with full premium access (no credit card), then <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Pro from $49/month billed annually</strong> ($59 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly, unlimited business system connections), and <strong>Enterprise</strong> custom capacity contracts.</p>
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
            Qefro provides an AI Business Application Platform for organizations — External SDK Connections, Managed Marketplace Apps, Customer Hub, Organization Workflows, and channels. Contact: <a href="mailto:support@qefro.com">support@qefro.com</a>.
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
            Qefro is an AI Business Application Platform. You configure organizations, workspaces, applications, tools,
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
        <span class="badge badge-indigo">{ICONS["sparkles"]} Build with Qefro</span>
        <h2>Build the AI layer for your business.</h2>
        <p>Connect your systems, ship applications, and automate organization workflows — start a 14-day free trial, no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Build with Qefro {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Talk to Sales</a>
          <a class="btn btn-link btn-lg" href="{DOCS}">Explore the SDK</a>
        </div>
        <p class="integrations-note" style="margin-top:1.25rem"><a href="/contact">Talk to Sales</a> for Enterprise · <a href="{DOCS}">Documentation</a> · <a href="/security">Security overview</a></p>
      </div>
    </section>
""",
    )


PAGES["features.html"] = inner(
    "Features | Qefro AI Business Application Platform",
    "Platform capabilities",
    "AI, Applications, SDK, Customer Hub, Workflows, Marketing, Storage, Channels, RBAC, and Marketplace — the shared foundation for every Qefro app.",
    "features.html",
    "features",
    "<p>Qefro is an <strong>AI Business Application Platform</strong>. Every application — managed or custom — shares AI, Customer Hub, Organization Workflows, Storage, Channels, and RBAC.</p>",
    features_page_content(),
    badge=f'{ICONS["sparkles"]} Features',
)

PAGES["how-it-works.html"] = inner(
    "Platform | Qefro AI Business Application Platform",
    "How Qefro works",
    "Connect existing systems via External SDK Connections, build Managed Marketplace Apps, and automate Organization Workflows — without replacing your ERP or CRM.",
    "how-it-works.html",
    "how-it-works",
    "<p><strong>Connect. Build. Automate.</strong> Keep your systems of record. Qefro adds the AI application and orchestration layer on top through the /qefro protocol, Marketplace apps, and Organization Workflows.</p>",
    how_it_works_page_content(),
    extra_jsonld=[howto_json("how-it-works.html")],
    badge=f'{ICONS["zap"]} Platform overview',
)

PAGES["use-cases.html"] = inner(
    "Applications &amp; solutions | Qefro",
    "Applications &amp; solutions",
    "Sales, customer operations, healthcare, restaurants, finance, and enterprise integrations — built as applications on the Qefro platform.",
    "use-cases.html",
    "use-cases",
    "<p>Business applications — not generic AI wrappers. Restaurant Pro, Clinic Pro, finance workflows, sales assistants, and custom SDK apps all share the same platform foundation.</p>",
    use_cases_page_content(),
    badge=f'{ICONS["building"]} Applications',
)

PAGES["security.html"] = inner(
    "Security | Qefro AI Business Application Platform",
    "Security",
    "Tenant and workspace isolation, RBAC, signed SDK connections, controlled tool access, and optional on-premise External SDK deployment.",
    "security.html",
    "security",
    "<p>Enterprise systems stay under your control. Qefro connects through signed SDK connections and controlled tools — your core infrastructure does not need to move. SOC 2 is on our roadmap — contact Sales for the current timeline.</p>",
    security_page_content(),
    badge=f'{ICONS["shield"]} Security',
)

PAGES["pricing.html"] = inner(
    "Pricing | Qefro AI Business Application Platform",
    "Pricing",
    "Platform plans for teams that connect systems and build applications. 14-day free trial. Starter from $29/mo, Pro from $49/mo, Growth from $99/mo.",
    "pricing.html",
    "pricing",
    "<p>Platform access for AI applications, SDK connections, channels, and workflows. Start a 14-day free trial, then scale with Starter, Pro, Growth, or Enterprise.</p>",
    pricing_page_content(),
    # No FAQPage here — Google asks to mark up each FAQ only once (on /faq).
    extra_jsonld=[PRICING_OFFERS_JSON],
    badge=f'{ICONS["zap"]} Pricing',
)

faq_html = "".join(
    faq_item_html(q, a, "faq", i) for i, (q, a) in enumerate(FAQ_ITEMS)
)

PAGES["faq.html"] = page(
    title="FAQ | Qefro AI Business Application Platform",
    description="FAQ about the Qefro AI Business Application Platform: pricing, security, SDK connections, workflows, channels, and setup.",
    path="faq.html",
    active="faq",
    jsonld=[
        webpage_json(
            "FAQ | Qefro AI Business Application Platform",
            "FAQ about the Qefro AI Business Application Platform: pricing, security, SDK connections, workflows, channels, and setup.",
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
        "What is Qefro? | AI Business Application Platform",
        "What is Qefro?",
        "Qefro is the AI Business Application Platform. Connect existing business systems through External SDK Connections, build Managed Marketplace Apps, and automate Organization Workflows — with Customer Hub, channels (Website, WhatsApp, Portal, API), workspaces, and RBAC. Customer support chat is one use case, not the definition of Qefro.",
        "<p>Keep your ERP, CRM, and databases. Qefro adds the AI application layer: Connect systems, Build apps, Automate workflows. Deploy through Website, WhatsApp, Internal Portal, or API — same applications, tools, and permissions underneath.</p>",
    ),
    (
        "qefro-pricing.html",
        "How much does Qefro cost? | Pricing overview",
        "How much does Qefro cost?",
        "Every new organization gets a 14-day free trial with full premium access. No credit card required. Starter from $29/month billed annually (connect up to 5 business systems). Pro from $49/month billed annually (up to 25 business systems). Growth from $99/month billed annually (unlimited business system connections). Enterprise is custom capacity priced to your requirements.",
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
          <p><a class="btn btn-primary" href="{PORTAL_LOGIN}">Start 14-day free trial</a></p>
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
        <span class="badge badge-indigo">{ICONS["sparkles"]} Build with Qefro</span>
        <h2>Try {escape(landing.h1)} on the Qefro platform.</h2>
        <p>Customer support is one application on Qefro. Start a 14-day free trial — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Build with Qefro {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Talk to Sales</a>
          <a class="btn btn-link btn-lg" href="/ai-customer-support-by-industry">Browse industries</a>
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
