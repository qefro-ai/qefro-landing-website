#!/usr/bin/env python3
"""Generate Qefro static pages — portal-inspired dark design + SEO/AEO markup."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
SITE = "https://qefro.com"
PORTAL = "https://app.qefro.com"
API = "https://api.qefro.com"
WIDGET_CDN = "https://cdn.qefro.com/widget.js"
PORTAL_LOGIN = f"{PORTAL}/login"
PORTAL_SIGNUP = f"{PORTAL}/login?mode=signup"
ASSET_VERSION = "33"
OG_IMAGE = f"{SITE}/assets/images/og-cover.png"
OG_IMAGE_ALT = (
    "Qefro — AI that knows your business and gets work done. Configure once in "
    "the Admin Console, deploy Customer AI and Employee AI everywhere."
)
DEMO_WIDGET_TOKEN = "demo-qefro-widget-token"
BUILD_DATE = date.today().isoformat()
WIDGET_WELCOME = (
    "Hi! I'm the Qefro assistant. Ask how Qefro deploys AI for customers and "
    "employees, or about workspaces, business actions, pricing, and security."
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

# Indexable pages for sitemap (extensionless paths; nginx serves matching .html)
SITEMAP_ENTRIES: list[tuple[str, str, str]] = [
    ("", "weekly", "1.0"),
    ("features", "monthly", "0.9"),
    ("how-it-works", "monthly", "0.8"),
    ("use-cases", "monthly", "0.8"),
    ("security", "monthly", "0.8"),
    ("pricing", "weekly", "0.9"),
    ("faq", "weekly", "0.9"),
    ("contact", "monthly", "0.7"),
    ("what-is-qefro", "monthly", "0.85"),
    ("qefro-pricing", "monthly", "0.85"),
    ("benchmark", "monthly", "0.6"),
]


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
    robots: str = "index, follow, max-image-preview:large, max-snippet:-1",
    include_canonical: bool = True,
) -> str:
    url = site_url(path)
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
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/css/styles.css?v={ASSET_VERSION}" />"""


def header(active: str | None = None) -> str:
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if active == href else ""
        links.append(f'        <a href="{href}"{cur}>{label}</a>')
    mobile = "\n".join(
        f'      <a href="{href}"{" aria-current=\"page\"" if active == href else ""}>{label}</a>'
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
        <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI Workspace Platform logo" width="40" height="40" />
        <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" />
      </a>
      <nav class="nav-links" aria-label="Primary">
{chr(10).join(links)}
        <a href="/faq"{' aria-current="page"' if active == "faq" else ""}>FAQ</a>
      </nav>
      <div class="nav-cta">
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch to dark mode">
          <span class="icon-moon" aria-hidden="true">{ICONS["moon"]}</span>
          <span class="icon-sun" aria-hidden="true">{ICONS["sun"]}</span>
        </button>
        <a class="btn-link" href="{PORTAL_LOGIN}">Sign In</a>
        <a class="btn btn-primary" href="{PORTAL_SIGNUP}">Start Free {ICONS["arrow"]}</a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false">{ICONS["menu"]}</button>
      </div>
    </div>
    <div class="mobile-panel wrap">
{mobile}
      <a href="/faq">FAQ</a>
      <a class="btn btn-primary" href="{PORTAL_SIGNUP}" style="justify-content:center;margin-top:0.5rem">Start Free</a>
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


def page_scripts() -> str:
    return f"""{widget_embed()}
  <script src="/assets/js/main.js?v={ASSET_VERSION}" defer></script>
  <script type="module" src="/assets/js/qefro-motion.js?v={ASSET_VERSION}"></script>"""


def footer() -> str:
    return f"""  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-top">
        <a class="brand" href="/" aria-label="Qefro home">
          <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI Workspace Platform logo" width="40" height="40" />
          <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" />
        </a>
        <nav class="footer-links" aria-label="Footer">
          <a href="/how-it-works">Platform</a>
          <a href="/features">Features</a>
          <a href="/use-cases">Solutions</a>
          <a href="/pricing">Pricing</a>
          <a href="/security">Security</a>
          <a href="/benchmark">Benchmark</a>
          <a href="/faq">FAQ</a>
          <a href="/contact">Contact</a>
          <a href="/llms.txt">llms.txt</a>
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
    robots: str = "index, follow, max-image-preview:large, max-snippet:-1",
    include_canonical: bool = True,
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
{page_scripts()}
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
        item = site_url(href) if href else site_url("")
        elements.append({"@type": "ListItem", "position": i, "name": name, "item": item})
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}, indent=2)


ORG_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": f"{SITE}/#organization",
        "name": "Qefro",
        "url": SITE,
        "logo": f"{SITE}/assets/images/qefro-logo.png",
        "email": "support@qefro.com",
        "sameAs": ["https://github.com/qefro-ai"],
    },
    indent=2,
)

WEBSITE_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "@id": f"{SITE}/#website",
        "name": "Qefro",
        "url": SITE,
        "description": "AI Workspace Platform for organizations — configure once in the Admin Console, deploy Customer AI and Employee AI everywhere.",
        "publisher": {"@id": f"{SITE}/#organization"},
        "inLanguage": "en-US",
    },
    indent=2,
)

SOFTWARE_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Qefro",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "url": SITE,
        "image": OG_IMAGE,
        "description": (
            "AI Workspace Platform for organizations: configure once in the Admin Console, "
            "then deploy Customer AI on website and WhatsApp and Employee AI via a branded "
            "Internal Portal — with knowledge, business actions, and permissions."
        ),
        "keywords": META_KEYWORDS,
        "offers": {
            "@type": "AggregateOffer",
            "lowPrice": "0",
            "highPrice": "119",
            "priceCurrency": "USD",
            "offerCount": "4",
            "availability": "https://schema.org/InStock",
            "url": f"{SITE}/pricing",
        },
    },
    indent=2,
)

# Use SoftwareApplication — not Product — so Google does not evaluate /pricing as a Merchant listing
# (shipping/return fields are for physical goods). SaaS belongs in software-app rich results.
PRICING_OFFERS_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Qefro",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
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
                "name": "Free",
                "price": "0",
                "priceCurrency": "USD",
                "description": "Forever free plan — no credit card required",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
            {
                "@type": "Offer",
                "name": "Starter",
                "price": "29",
                "priceCurrency": "USD",
                "description": "Billed annually ($39/month if billed monthly)",
                "url": f"{SITE}/pricing",
                "availability": "https://schema.org/InStock",
                "priceValidUntil": "2027-12-31",
            },
            {
                "@type": "Offer",
                "name": "Growth",
                "price": "99",
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
    """Shared Free / Starter / Growth / Enterprise cards for homepage + /pricing."""
    cta = ' data-price-cta' if interactive else ""
    clarity = (
        lambda event: f' data-clarity-event="{event}"' if interactive else ""
    )
    return f"""          <article class="price-card{cta}">
            <h3>Free</h3>
            <p class="price-best">Best for evaluating the platform</p>
            <div class="price-amount">$0</div>
            <p class="price-desc">Forever free — no credit card</p>
            <ul class="price-feats">
              {price_feat("100 conversations/month")}
              {price_feat("Knowledge for getting started", "2 documents")}
              {price_feat("Connect 1 business system")}
              {price_feat("2 team members")}
              {price_feat("Website widget + voice")}
              {price_feat("Multilingual RAG")}
              {price_feat("Community support")}
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}"{clarity("cta_start_free")}>Start Free</a>
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
              {price_feat("Website widget + voice")}
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
            <img src="/assets/images/product/{filename}" alt="Qefro {title}: {description}" loading="lazy" width="1440" height="900" />
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
        "Qefro is an AI Workspace Platform for organizations. Configure once in the Admin Console, "
        "deploy Customer AI on your website and WhatsApp, and give employees a branded Internal Portal — "
        "sharing one knowledge platform, one permission system, and one set of business actions.",
    ),
    ("How much does Qefro cost?", "Qefro is freemium — start Free forever (100 conversations/month, knowledge for getting started, connect 1 business system). Starter is $29/month billed annually ($39 monthly, connect up to 5 business systems). Growth is $99/month billed annually ($119 monthly, unlimited business system connections). Enterprise is custom. No credit card required."),
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
        "Yes. Connect REST APIs or import OpenAPI specs as Business Tools so AI can perform "
        "defined business actions — retrieve live data, create tickets, look up orders — using "
        "encrypted credentials or end-user identity you forward via the widget identify() API.",
    ),
    (
        "How long does setup take?",
        "Typical setup takes {{REAL_SETUP_TIME}} depending on your documentation and integrations. "
        "Most teams embed the website widget in under 5 minutes; connecting business systems and "
        "rolling out the Internal Portal depends on your APIs and knowledge prep.",
    ),
    ("How long does integration take?", "Most teams embed the website widget in under 5 minutes. Identify authenticated users with a few lines of JavaScript. WhatsApp, Internal Portal, and API access are available for deeper rollouts."),
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
        "branded Internal Portal for employees, WhatsApp on Growth+, and direct API/WebSocket access for custom UIs.",
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
        <span class="eyebrow" data-motion="hero-badge">{ICONS["sparkles"]} AI Workspace Platform</span>
        <h1 data-motion="hero-title">
          <span class="hero-line">AI That Knows Your Business</span>
          <span class="hero-accent">and Gets Work Done</span>
        </h1>
        <p class="hero-sub" data-motion="hero-sub">Deploy AI across customer support and internal teams. Answer questions, search company knowledge, and securely perform business actions from one centralized AI platform.</p>
        <div class="hero-actions" data-motion="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_start_free">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="#demo" data-open-demo data-clarity-event="cta_try_live_demo">Try Live Demo</a>
        </div>
        <div class="hero-checks" data-motion="hero-checks">
          <span>{ICONS["check"]} Configure once · deploy everywhere</span>
          <span>{ICONS["check"]} Free forever · no credit card</span>
          <span>{ICONS["check"]} Customers &amp; employees</span>
          <span>{ICONS["check"]} Your auth stays yours</span>
        </div>
        <p class="hero-diff" data-motion="hero-diff">Most AI platforms answer questions. Qefro answers questions and securely performs business actions using your organization&rsquo;s knowledge, APIs, and permissions.</p>
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
              <a class="btn btn-ghost" href="{PORTAL_SIGNUP}" style="margin-left:0.5rem" data-clarity-event="cta_start_free">Start Free</a>
            </p>
          </div>
          <button type="button" class="demo-chat" data-open-demo data-clarity-event="cta_chat_mock" aria-label="Open live chat demo">
            <div class="chat-mock" data-motion="hero-float">
              <div class="chat-mock-head">
                <div class="chat-mock-avatar">{ICONS["bot"]}</div>
                <div><strong>Qefro Assistant</strong><span>AI Workspace Platform</span></div>
              </div>
              <div class="chat-mock-body" data-demo-script>
                <div class="chat-bubble ai">Hi! I can explain how Qefro deploys AI for customers and employees from one platform.</div>
                <div class="chat-bubble user">What makes Qefro different?</div>
                <div class="chat-bubble ai">Most AI platforms answer questions. Qefro also performs business actions using your knowledge, APIs, and permissions — configure once, deploy everywhere.</div>
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
          <span class="badge badge-indigo">{ICONS["zap"]} Platform overview</span>
          <h2 id="platform-heading">Configure knowledge once. Deploy it everywhere.</h2>
          <p>Set up workspaces, knowledge, business actions, and permissions in the Admin Console — then deploy Customer AI and Employee AI across every channel. <a href="/how-it-works">See how the platform works</a>.</p>
        </div>
        <div class="arch-diagram arch-diagram-flow reveal" role="img" aria-label="Admin Console configures once, then deploys Customer AI and Employee AI" data-motion="architecture">
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
        <div class="exp-grid reveal" style="margin-top:2.5rem">
          <article class="exp-card">
            <div class="exp-icon">{ICONS["headphones"]}</div>
            <h3>Customer AI</h3>
            <p>Website widget and WhatsApp with knowledge answers, business actions, lead capture, and human handoff.</p>
          </article>
          <article class="exp-card exp-card-featured">
            <div class="exp-icon">{ICONS["building"]}</div>
            <h3>Employee AI</h3>
            <p>Branded Internal Portal with workspace selector, conversations, documents, and source citations.</p>
          </article>
          <article class="exp-card">
            <div class="exp-icon">{ICONS["server"]}</div>
            <h3>Admin Console</h3>
            <p>One place to configure knowledge, actions, teams, branding, channels, analytics, and inbox.</p>
          </article>
        </div>
        <div class="product-mock-grid reveal" style="margin-top:2.5rem">
          <figure class="product-mock">
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
          <figure class="product-mock">
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
          <p>Grounded answers from your content, secure actions via your APIs, and deployment where your people already work. <a href="/features">Explore all features</a>.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card">
            <h3>Business Actions</h3>
            <ul>
              <li>Powered by Business Tools</li>
              <li>REST &amp; OpenAPI import</li>
              <li>Encrypted credentials</li>
              <li>Identity forwarding</li>
              <li>Execution logs</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Knowledge Platform</h3>
            <ul>
              <li>PDF, DOCX, Markdown, TXT</li>
              <li>Website crawling &amp; OCR</li>
              <li>Multilingual retrieval</li>
              <li>Source citations</li>
              <li>Workspace-isolated bases</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Channels</h3>
            <ul>
              <li>Website widget &amp; voice</li>
              <li>Internal Portal</li>
              <li>WhatsApp (Growth+)</li>
              <li>Human handoff</li>
              <li>Lead capture</li>
            </ul>
          </article>
          <article class="outcome-card">
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
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Where is my order?</p>
            <div class="scenario-flow"><span>AI calls your Order API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Live tracking returned</span></div>
          </article>
          <article class="scenario-card">
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
          <p>Freemium — Free forever. Save ~26% with yearly billing — Starter from $29/mo, Growth from $99/mo. <a href="/pricing">Full pricing details</a>.</p>
        </div>
        <div class="direct-answer reveal">
          <p>Qefro has a <strong>Free plan</strong> (100 conversations/month, knowledge for getting started, connect 1 business system), then <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly), and custom Enterprise plans.</p>
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
        <h2 id="cta-heading">Deploy your company&rsquo;s AI workspace.</h2>
        <p>Start free for Customer AI, Employee AI, and the Admin Console — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}" data-clarity-event="cta_start_free">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="#demo" data-open-demo data-clarity-event="cta_try_live_demo">Try Live Demo</a>
        </div>
        <p class="integrations-note" style="margin-top:1.25rem"><a href="/contact">Talk to Sales</a> for Enterprise · <a href="/benchmark">Benchmark methodology</a> · <a href="/security">Security</a></p>
      </div>
    </section>
"""


PAGES["index.html"] = page(
    title="Qefro — AI That Knows Your Business and Gets Work Done",
    description=(
        "Qefro deploys AI across support and internal teams — "
        "grounded answers plus secure business actions. Start free."
    ),
    path="",
    jsonld=[ORG_JSON, WEBSITE_JSON, SOFTWARE_JSON],
    body=home_body(),
)

# Inner pages — detailed content for menu-linked pages
def features_page_content() -> str:
    return f"""        <div class="outcome-grid">
          <article class="outcome-card"><h3>AI Workspaces</h3><ul><li>Per-team AI contexts</li><li>Isolated knowledge bases</li><li>Scoped business actions</li><li>Public &amp; private workspaces</li><li>Owner / Admin / Member RBAC</li><li>Separate conversations &amp; permissions</li></ul></article>
          <article class="outcome-card"><h3>Knowledge Platform</h3><ul><li>PDF, DOCX, Markdown, TXT</li><li>Website crawler</li><li>OCR for scans &amp; images</li><li>Multilingual (EN, AR, TA, HI+)</li><li>Hybrid BM25 + vector search</li><li>Source citations &amp; refusal when unsure</li></ul></article>
          <article class="outcome-card"><h3>Business Actions</h3><ul><li>Powered by Business Tools</li><li>REST &amp; OpenAPI import</li><li>Encrypted API credentials</li><li>End-user identity via identify()</li><li>SSRF &amp; DNS-pinned webhooks</li><li>Execution logs &amp; schema validation</li></ul></article>
          <article class="outcome-card"><h3>AI Experiences</h3><ul><li>Website widget (JWT auth)</li><li>Internal Portal for employees</li><li>WhatsApp (Growth+)</li><li>Voice STT/TTS in widget</li><li>WebSocket streaming</li><li>Handoff to human agents</li></ul></article>
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
          <p>Powered by Business Tools. Import OpenAPI or configure REST endpoints for order lookup, booking, ticketing, CRM queries, or ERP reads. Credentials are encrypted; outbound calls use HTTPS with SSRF protections.</p>
        </div>
        <div class="scenario-grid reveal">
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Where is my order #4821?</p>
            <div class="scenario-flow"><span>AI calls Order API with user JWT</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Live tracking returned</span></div>
          </article>
          <article class="scenario-card">
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
    return f"""        <div class="steps-grid">
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">01</div></div><h3>Configure once</h3><p>In the Admin Console, create AI Workspaces, upload knowledge, set instructions, define business actions, invite teams, and set Owner / Admin / Member permissions.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">02</div></div><h3>Connect business systems</h3><p>Import OpenAPI or configure REST endpoints as Business Tools. Store encrypted credentials or forward end-user JWTs via identify(). Scope actions per workspace.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">03</div></div><h3>Deploy everywhere</h3><p>Launch Customer AI on website and WhatsApp, and Employee AI on a branded Internal Portal — same knowledge, actions, and permissions underneath.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">04</div></div><h3>Monitor &amp; improve</h3><p>Review conversations, analytics, and action logs. Hand off to humans when needed. Reindex documents as policies change.</p></article>
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
            <li>REST API for documents, Business Tools, conversations, and billing</li>
            <li>WebSocket chat with streaming tokens and tool-call events</li>
            <li>Widget SDK with identify(), lazy voice, and theme customization</li>
            <li>Internal Portal at yourcompany.qefro.com for employees</li>
          </ul>
        </div>"""


def use_cases_page_content() -> str:
    return f"""        <div class="uc-grid">
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["building"]}</div><h3>Employee AI</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Branded Internal Portal</li><li>{ICONS["chevr"]} HR, IT, Finance, Sales workspaces</li><li>{ICONS["chevr"]} Policy &amp; compliance lookup</li><li>{ICONS["chevr"]} Role-based knowledge access</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["headphones"]}</div><h3>Customer Support</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Order &amp; shipment lookups via your APIs</li><li>{ICONS["chevr"]} Refund policy with citations</li><li>{ICONS["chevr"]} Ticket creation in your helpdesk</li><li>{ICONS["chevr"]} Handoff to agents from inbox</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["shield"]}</div><h3>Regulated Industries</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Protocol &amp; guideline search</li><li>{ICONS["chevr"]} PII scrubbing in conversations</li><li>{ICONS["chevr"]} Tenant-isolated knowledge</li><li>{ICONS["chevr"]} Audit-ready execution logs</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["server"]}</div><h3>Engineering &amp; Ops</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Runbook &amp; incident playbooks</li><li>{ICONS["chevr"]} API docs + OpenAPI actions</li><li>{ICONS["chevr"]} Multilingual wiki search</li><li>{ICONS["chevr"]} Internal self-service portal</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["zap"]} Real scenarios</span>
          <h2>Knowledge plus live business actions</h2>
          <p>Every solution combines grounded document answers with optional business actions through your existing systems — powered by Business Tools.</p>
        </div>
        <div class="scenario-grid reveal">
          <article class="scenario-card">
            <p class="scenario-ask"><span>Employee</span> What is our parental leave policy?</p>
            <div class="scenario-flow"><span>Retrieves HR handbook</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Cited answer in employee&rsquo;s language</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Cancel my subscription</p>
            <div class="scenario-flow"><span>AI calls Billing API with identify()</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Cancellation confirmed</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Engineer</span> How do I roll back deploy?</p>
            <div class="scenario-flow"><span>Retrieves runbook</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Step-by-step with doc link</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> I need a human</p>
            <div class="scenario-flow"><span>Handoff triggered</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Agent sees full thread in inbox</span></div>
          </article>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Industries</h2>
          <p>Teams in SaaS, healthcare, education, manufacturing, retail, professional services, government, and internal IT use Qefro to deploy organizational AI without building a platform from scratch.</p>
        </div>"""


def security_page_content() -> str:
    return f"""        <div class="trust-grid">
          <article class="trust-card"><div class="trust-icon">{ICONS["bot"]}</div><h3>End-user identity forwarding</h3><p>Forward signed-in identity via <code>identify()</code> so business actions run as the real user — passwords never touch Qefro.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["lock"]}</div><h3>Zero-trust style authorization</h3><p>Business actions authorize with the end-user&rsquo;s identity by default — not a shared organization secret.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["file"]}</div><h3>Audit &amp; execution logs</h3><p>Conversation history and Business Tool runs stay attached for accountability and review.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["building"]}</div><h3>Tenant &amp; workspace isolation</h3><p>Multi-tenant by design at the database and vector store level. AI Workspaces control which knowledge and actions each experience can use.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["shield"]}</div><h3>Widget JWT auth</h3><p>Embeds load with short-lived widget tokens. Messages are bounded (8 KB), PII is scrubbed before model calls, and tenants cannot access each other&rsquo;s data.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["server"]}</div><h3>Encrypted secrets &amp; secure actions</h3><p>Business Tool credentials encrypted at rest. HTTPS-only outbound calls with SSRF protections and DNS-pinned webhooks.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>Enterprise platform controls</h2>
          <p>Built for organizational AI — not demo chat experiences.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card"><h3>Access control</h3><ul><li>Owner / Admin / Member RBAC</li><li>Email OTP — no password storage</li><li>Billing actions restricted to owners</li><li>Workspace-scoped documents &amp; actions</li></ul></article>
          <article class="outcome-card"><h3>Data handling</h3><ul><li>PII scrubbing on outbound LLM calls</li><li>Never used to train AI models</li><li>Encrypted at rest &amp; in transit</li><li>Conversation isolation</li></ul></article>
          <article class="outcome-card"><h3>Action execution</h3><ul><li>OpenAPI schema validation</li><li>SSRF &amp; DNS pinning for webhooks</li><li>Per-action allow-from-public-chat toggle</li><li>Execution logs for accountability</li></ul></article>
          <article class="outcome-card"><h3>Enterprise roadmap</h3><ul><li>SSO / SAML (roadmap)</li><li>Platform admin audit trail (roadmap)</li><li>Private deployment available today</li><li>SOC 2 program in progress</li></ul></article>
        </div>
        <div class="prose reveal" style="margin-top:2.5rem">
          <h2>Compliance &amp; deployment</h2>
          <p>Enterprise customers can run Qefro in a private environment with dedicated support and custom SLAs. Contact sales for the current compliance roadmap and data processing terms.</p>
        </div>"""


def pricing_page_content() -> str:
    return f"""        <div class="billing-toggle" role="group" aria-label="Billing period">
          <button type="button" data-billing="monthly">Monthly</button>
          <button type="button" data-billing="annual" class="is-active">Yearly <span>Save 26%</span></button>
        </div>
        <div class="price-grid">
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
          <p>Billing is prepaid via Razorpay in the portal. Upgrade or top up anytime; owners manage subscriptions and invoices from the billing page.</p>
        </div>"""


def inner(title, h1, desc, path, active, answer, content, extra_jsonld=None, extra_sections=""):
    jl = [breadcrumb_json([("Home", ""), (h1, path)])]
    if extra_jsonld:
        jl.extend(extra_jsonld)
    return page(
        title=title,
        description=desc,
        path=path,
        active=active,
        jsonld=jl,
        body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", ""), (h1, "")])}
        <h1>{h1}</h1>
        <div class="direct-answer" style="text-align:left">{answer}</div>
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
        <h2>Ready to deploy your company&rsquo;s AI workspace?</h2>
        <p>Start free — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Book Demo</a>
        </div>
      </div>
    </section>
""",
    )


PAGES["features.html"] = inner(
    "Qefro features — AI Workspace Platform",
    "Features",
    "Qefro AI Workspace Platform: AI Workspaces, knowledge RAG, business actions (REST/OpenAPI), Customer AI widget, Internal Portal, WhatsApp, voice, RBAC, and agent handoff.",
    "features.html",
    "features",
    "<p>Qefro combines <strong>AI Workspaces</strong>, a <strong>knowledge platform</strong>, <strong>business actions</strong>, and <strong>three AI experiences</strong> — Customer AI, Employee AI, and Admin Console — so organizations can answer questions, take secure actions, and govern access from one platform.</p>",
    features_page_content(),
)

PAGES["how-it-works.html"] = inner(
    "Qefro platform — configure once, deploy everywhere",
    "Platform",
    "How the Qefro platform works: configure AI Workspaces, knowledge, and business actions once in the Admin Console, then deploy Customer AI and Employee AI everywhere.",
    "how-it-works.html",
    "how-it-works",
    "<p><strong>Configure once. Deploy everywhere.</strong> Four steps from Admin Console setup to production organizational AI. We handle vectors, models, PII scrubbing, and action execution — you bring knowledge, APIs, and permissions.</p>",
    how_it_works_page_content(),
)

PAGES["use-cases.html"] = inner(
    "Qefro solutions — Customer AI, Employee AI, HR, IT, engineering",
    "Solutions",
    "Teams use Qefro for Customer AI with live API actions, Employee AI portals for HR/IT, regulated compliance lookup, and engineering runbooks — multilingual RAG included.",
    "use-cases.html",
    "use-cases",
    "<p>Same AI Workspace Platform for customer-facing experiences and internal operations — grounded answers from docs plus optional business actions through your existing APIs.</p>",
    use_cases_page_content(),
)

PAGES["security.html"] = inner(
    "Qefro security — enterprise AI Workspace Platform",
    "Security",
    "Enterprise security for organizational AI: end-user identity forwarding, zero-trust style authorization, audit logs, multi-tenant isolation, workspace RBAC, and encrypted secrets.",
    "security.html",
    "security",
    "<p>Authentication stays in your app. Qefro never stores passwords. Lead with the controls that matter: tenant isolation, encryption, identity forwarding, audit logs, and secure secret storage. SOC 2 compliance is on our roadmap — contact Sales for the current timeline.</p>",
    security_page_content(),
)

PAGES["pricing.html"] = inner(
    "Qefro pricing — Starter from $29/mo, Growth from $99/mo, Enterprise",
    "Pricing",
    "Qefro pricing: Free forever (100 conversations, multilingual RAG, widget + voice). Starter $29/mo annual, Growth $99/mo with WhatsApp and unlimited business system connections.",
    "pricing.html",
    "pricing",
    "<p>Start free with multilingual RAG, widget JWT auth, and voice. Scale to WhatsApp and unlimited business system connections on Growth. Enterprise adds private deployment and custom SLAs.</p>",
    pricing_page_content(),
    extra_jsonld=[
        PRICING_OFFERS_JSON,
        faq_schema([("How much does Qefro cost?", "Qefro is freemium: Free plan includes 100 conversations/month, knowledge for getting started, and connect 1 business system. Starter is $29/month billed annually ($39 monthly) with up to 5 business systems. Growth is $99/month billed annually ($119 monthly) with unlimited business system connections. Enterprise is custom. No credit card required to start Free.")]),
    ],
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
    title="Qefro FAQ — AI Workspace Platform, pricing, security, integrations",
    description="FAQ about the Qefro AI Workspace Platform: pricing, accuracy, security, business actions, Internal Portal, workspaces, and setup.",
    path="faq.html",
    active="faq",
    jsonld=[breadcrumb_json([("Home", ""), ("FAQ", "faq")]), faq_schema()],
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", ""), ("FAQ", "")])}
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
    title="Qefro benchmark methodology — accuracy evaluation",
    description="How Qefro measures answer accuracy: test set composition, evaluation methodology, results, and known limitations.",
    path="benchmark.html",
    jsonld=[breadcrumb_json([("Home", ""), ("Benchmark Methodology", "benchmark")])],
    body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", ""), ("Benchmark Methodology", "")])}
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
    "Contact Qefro — sales, support, and demos",
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
          <p class="contact-alt">Prefer email? <a href="mailto:support@qefro.com?subject=Qefro%20demo%20request">support@qefro.com</a> · or <a href="{PORTAL_SIGNUP}">start free</a></p>
        </form>
        <div class="cap-grid" style="margin-top:2rem">
          <a class="cap-card" href="mailto:support@qefro.com"><div class="cap-icon">{ICONS["msg"]}</div><span>support@qefro.com</span></a>
          <a class="cap-card" href="{PORTAL_SIGNUP}"><div class="cap-icon">{ICONS["zap"]}</div><span>Start free</span></a>
          <a class="cap-card" href="/pricing"><div class="cap-icon">{ICONS["chart"]}</div><span>View pricing</span></a>
        </div>""",
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
        "What is Qefro? — AI Workspace Platform for Organizations",
        "What is Qefro?",
        "Qefro is an AI Workspace Platform for organizations. Configure once in the Admin Console, deploy Customer AI on website and WhatsApp, and give employees a branded Internal Portal — sharing one knowledge platform, permission system, and set of business actions.",
        "<p>Most AI platforms answer questions. Qefro answers questions and securely performs business actions using your organization&rsquo;s knowledge, APIs, and permissions. Configure once in the Admin Console, then deploy Customer AI and Employee AI everywhere — with workspace-level isolation.</p>",
    ),
    (
        "qefro-pricing.html",
        "How much does Qefro cost?",
        "How much does Qefro cost?",
        "Qefro is freemium. Free forever: 100 conversations/month, knowledge for getting started, connect 1 business system. Starter from $29/month billed annually (connect up to 5 business systems). Growth from $99/month billed annually (unlimited business system connections). Enterprise is custom. No credit card required.",
        '<p>See the full comparison on the <a href="/pricing">pricing page</a>.</p>',
    ),
]:
    PAGES[slug] = page(
        title=title,
        description=a,
        path=slug,
        jsonld=[
            breadcrumb_json([("Home", ""), (q, slug.removesuffix(".html"))]),
            faq_schema([(q, a)]),
        ],
        body=f"""    <section class="page-hero">
      <div class="wrap-5xl">
        {crumbs([("Home", ""), (q, "")])}
        <h1>{q}</h1>
        <div class="direct-answer"><p>{a}</p></div>
        <div class="prose" style="margin-top:1.5rem">{extra}
          <p><a class="btn btn-primary" href="{PORTAL_LOGIN}">Start free</a></p>
        </div>
      </div>
    </section>
""",
    )


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
    content = f"""User-agent: *
Allow: /

# App and admin are separate hosts; marketing site only.
Sitemap: {SITE}/sitemap.xml
"""
    (ROOT / "robots.txt").write_text(content, encoding="utf-8")
    print("wrote robots.txt")


def write_sitemap_xml() -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, changefreq, priority in SITEMAP_ENTRIES:
        loc = site_url(path if path else "index.html")
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(loc)}</loc>")
        lines.append(f"    <lastmod>{BUILD_DATE}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
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
