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
ASSET_VERSION = "15"
OG_IMAGE = f"{SITE}/assets/images/og-cover.png"
OG_IMAGE_ALT = "Qefro — Turn business knowledge into instant answers. RAG assistant grounded in your content."
DEMO_WIDGET_TOKEN = "demo-qefro-widget-token"
BUILD_DATE = date.today().isoformat()
WIDGET_WELCOME = (
    "Hi! I'm the Qefro assistant. Ask me how Qefro helps businesses, pricing, security, or how to integrate."
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
    ("how-it-works", "How it Works"),
    ("use-cases", "Use Cases"),
    ("security", "Security"),
    ("pricing", "Pricing"),
    ("features", "Docs"),
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
  <link rel="icon" href="/assets/images/favicon.svg?v={ASSET_VERSION}" type="image/svg+xml" />
  <link rel="icon" href="/assets/images/favicon-32.png?v={ASSET_VERSION}" type="image/png" sizes="32x32" />
  <link rel="apple-touch-icon" href="/assets/images/apple-touch-icon.png?v={ASSET_VERSION}" sizes="180x180" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet" />
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
        <img src="/assets/images/qefro-logo.png" alt="Qefro AI customer support platform logo" width="40" height="40" />
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
        <a class="btn btn-primary" href="{PORTAL_LOGIN}">Get Started {ICONS["arrow"]}</a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false">{ICONS["menu"]}</button>
      </div>
    </div>
    <div class="mobile-panel wrap">
{mobile}
      <a href="/faq">FAQ</a>
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
  <script src="/assets/js/main.js?v={ASSET_VERSION}" defer></script>"""


def footer() -> str:
    return """  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-top">
        <a class="brand" href="/" aria-label="Qefro home">
          <img src="/assets/images/qefro-logo.png" alt="Qefro AI customer support platform logo" width="40" height="40" />
        </a>
        <nav class="footer-links" aria-label="Footer">
          <a href="/features">Features</a>
          <a href="/pricing">Pricing</a>
          <a href="/security">Security</a>
          <a href="/faq">FAQ</a>
          <a href="/contact">Contact</a>
          <a href="/llms.txt">llms.txt</a>
        </nav>
      </div>
      <div class="footer-bottom">
        <p>© <span data-year></span> qefro AI. All rights reserved.</p>
        <p>Built for teams who value their knowledge.</p>
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
    return f"""<!DOCTYPE html>
<html lang="en" data-api-url="{API}" data-widget-cdn="{WIDGET_CDN}">
<head>
{meta_block(title, description, path, robots=robots, include_canonical=include_canonical)}
{schemas}
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
        "description": "AI customer support grounded in your business knowledge.",
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
        "description": "AI customer support and knowledge assistant that answers only from your verified company content.",
        "offers": {
            "@type": "AggregateOffer",
            "lowPrice": "29",
            "highPrice": "119",
            "priceCurrency": "USD",
            "offerCount": "3",
        },
    },
    indent=2,
)

PRICING_OFFERS_JSON = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Qefro",
        "description": "AI customer support platform with RAG, website widget, and WhatsApp.",
        "brand": {"@type": "Brand", "name": "Qefro"},
        "offers": [
            {
                "@type": "Offer",
                "name": "Starter",
                "price": "29",
                "priceCurrency": "USD",
                "description": "Billed annually ($39/month if billed monthly)",
                "url": f"{SITE}/pricing",
            },
            {
                "@type": "Offer",
                "name": "Growth",
                "price": "99",
                "priceCurrency": "USD",
                "description": "Billed annually ($119/month if billed monthly)",
                "url": f"{SITE}/pricing",
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
    '<p class="price-desc" style="margin:0.75rem 0 0;font-size:0.75rem">'
    "Fair use limits apply to storage and processing volume — see Terms for details."
    "</p>"
)

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
          <p>Everything your team needs to build, deploy, and improve AI customer support.</p>
        </div>
        <div class="product-shot-grid reveal">
{cards}
        </div>
      </div>
    </section>
"""


FAQ_ITEMS = [
    ("What is Qefro?", "Qefro is an AI customer support and knowledge assistant that answers questions using only your company’s verified content — documents, FAQs, policies, and websites."),
    ("How much does Qefro cost?", "Starter is $29/month billed annually ($39 monthly), Growth is $99/month billed annually ($119 monthly), and Enterprise is custom. Start free forever — no credit card required."),
    ("What types of content can I upload?", "PDFs, Word documents, Markdown, plain text — or crawl entire websites automatically. Our pipeline processes and indexes everything."),
    ("How accurate are the answers?", FAQ_ACCURACY_ANSWER_HTML),
    ("Is my data secure?", "Your data is tenant-isolated, encrypted at rest and in transit, and never used to train AI models. SOC 2 compatible with private deployment available."),
    ("How long does integration take?", "Most teams are live in under 5 minutes — paste one script tag on your site. API and SDK available for deeper integrations."),
    ("Can I use this for internal teams only?", "Absolutely. Many customers use Qefro purely for internal self-service — HR, IT helpdesk, compliance, and engineering knowledge bases."),
    ("Do you offer enterprise pricing?", "Yes. Enterprise plans include unlimited conversations, private deployment, SSO, dedicated support, and custom SLAs."),
]

USE_CASES = [
    ("internal", "Internal Teams", "building", [
        "Employee onboarding", "HR & policy queries", "IT helpdesk", "SOP & compliance lookup",
        "Team wiki search", "Benefits lookup", "Compliance docs", "Knowledge sharing",
    ]),
    ("support", "Customer Support", "headphones", [
        "E-commerce FAQs", "Order & refund policies", "Product documentation", "Self-service support",
        "Shipping updates", "Returns handling", "Billing questions", "Product recommendations",
    ]),
    ("regulated", "Regulated Industries", "shield", [
        "Hospital staff protocols", "Medical guidelines", "Operations manuals", "Compliance docs",
        "Policy lookup", "Audit preparation", "Safety procedures", "Regulatory updates",
    ]),
    ("engineering", "Tech & Engineering", "server", [
        "Engineering runbooks", "Internal wikis", "API documentation", "Incident playbooks",
        "Dev onboarding", "Architecture docs", "Release notes", "Troubleshooting guides",
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
PAGES["index.html"] = page(
    title="Qefro — Turn business knowledge into instant answers",
    description="Deploy AI customer support in minutes. Train on your documents, automate website and WhatsApp support, and deliver multilingual answers with Qefro.",
    path="",
    jsonld=[ORG_JSON, WEBSITE_JSON, SOFTWARE_JSON],
    body=f"""    <section class="hero" aria-label="Hero">
      <div class="hero-grid" aria-hidden="true"></div>
      <div class="wrap-5xl hero-inner">
        <span class="eyebrow">{ICONS["sparkles"]} Retrieval-Augmented Generation</span>
        <h1>
          <span class="hero-line">Enterprise AI Customer Support</span>
          <span class="hero-accent">Grounded in Your Knowledge</span>
        </h1>
        <p class="hero-sub">Train on your documents, website, PDFs, and FAQs. Deploy multilingual support to your website, WhatsApp, and API in minutes — with answers designed to decline when relevant context is missing.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_LOGIN}">Start Free Trial {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">{ICONS["msg"]} Book a Demo</a>
        </div>
        <div class="hero-checks">
          <span>{ICONS["check"]} Start free forever</span>
          <span>{ICONS["check"]} No credit card required</span>
          <span>{ICONS["check"]} Setup in 5 minutes</span>
          <span>{ICONS["check"]} SOC 2 ready</span>
        </div>
        <div class="pipeline" role="list" aria-label="How Qefro answers a question">
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">01</span>
            <span class="pipeline-v">Upload</span>
            <span class="pipeline-d">Your docs, site &amp; PDFs</span>
          </div>
          <span class="pipeline-arrow" aria-hidden="true">{ICONS["chevr"]}</span>
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">02</span>
            <span class="pipeline-v">Understand</span>
            <span class="pipeline-d">Learns your content</span>
          </div>
          <span class="pipeline-arrow" aria-hidden="true">{ICONS["chevr"]}</span>
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">03</span>
            <span class="pipeline-v">Match</span>
            <span class="pipeline-d">Finds the right context</span>
          </div>
          <span class="pipeline-arrow" aria-hidden="true">{ICONS["chevr"]}</span>
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">04</span>
            <span class="pipeline-v">Answer</span>
            <span class="pipeline-d">Grounded — or it declines</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section-facts" aria-label="What you get with Qefro">
      <div class="wrap-5xl">
        <p class="facts-label">What it means for your team</p>
        <div class="facts-grid">
          <div class="fact"><div class="fact-v">Instant answers</div><div class="fact-k">Subsecond replies, around the clock</div></div>
          <div class="fact"><div class="fact-v">Answers you can trust</div><div class="fact-k">Declines when unsure — never fabricates</div></div>
          <div class="fact"><div class="fact-v">Your data stays private</div><div class="fact-k">Isolated per customer, SOC 2-ready</div></div>
          <div class="fact"><div class="fact-v">Deploy anywhere</div><div class="fact-k">Self-hostable, no vendor lock-in</div></div>
        </div>
      </div>
    </section>

    <section class="section" id="platform">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Platform</span>
          <h2>One Platform. Everything You Need.</h2>
          <p>A single product that handles ingestion, intelligence, and deployment end-to-end.</p>
        </div>
        <div class="direct-answer reveal">
          <p><strong>Qefro</strong> is an AI customer support and knowledge assistant for businesses. It retrieves relevant passages from your verified knowledge base and answers only from that context.</p>
        </div>
        <div class="cap-panel reveal">
        <div class="cap-grid">
          <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>PDF, Word &amp; Markdown ingestion</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>Website crawling &amp; indexing</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>Refusal-first, source-grounded RAG</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["msg"]}</div><span>Web widget, API &amp; WhatsApp</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Analytics &amp; conversation history</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["shield"]}</div><span>Tenant-isolated &amp; SOC 2 ready</span></div>
        </div>
        </div>
      </div>
    </section>

{product_screenshots_html()}
    <section class="section section-alt" id="how-it-works">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["check"]} Process</span>
          <h2>Get Started in 3 Steps</h2>
          <p>No technical expertise required.</p>
        </div>
        <div class="steps-grid reveal">
          <article class="step">
            <div class="step-num-wrap"><div class="step-num-inner">01</div></div>
            <h3>Upload Your Knowledge</h3>
            <p>Add documents, policies, PDFs, or crawl entire websites. We chunk, embed, and index everything automatically.</p>
          </article>
          <article class="step">
            <div class="step-num-wrap"><div class="step-num-inner">02</div></div>
            <h3>Configure Your Assistant</h3>
            <p>Set a name, persona, and deploy anywhere — your website, internal portal, or WhatsApp — in under 5 minutes.</p>
          </article>
          <article class="step">
            <div class="step-num-wrap"><div class="step-num-inner">03</div></div>
            <h3>Get Instant Answers</h3>
            <p>Every response is grounded strictly in your content. When relevant context isn&rsquo;t found, it declines to answer. Full audit trail and source citations.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section" id="why-qefro">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Why Qefro</span>
          <h2>Confident answers — or an honest &ldquo;I don&rsquo;t know&rdquo;</h2>
          <p>Generic chatbots fill the gaps by guessing. Qefro answers only from your verified content, shows its sources, and declines when the answer isn&rsquo;t there.</p>
        </div>
        <div class="compare reveal">
          <div class="compare-q">
            <span class="compare-q-label">A customer asks</span>
            <p>&ldquo;Can I still get a refund after 45 days?&rdquo;</p>
          </div>
          <div class="compare-cols">
            <article class="compare-card compare-bad">
              <span class="compare-tag compare-tag-bad">{ICONS["x"]} Generic chatbot</span>
              <p class="compare-answer">&ldquo;Absolutely! You can request a full refund any time within 60 days of purchase.&rdquo;</p>
              <p class="compare-note">{ICONS["x"]} Invents a policy that doesn&rsquo;t exist — confident, and wrong.</p>
            </article>
            <article class="compare-card compare-good">
              <span class="compare-tag compare-tag-good">{ICONS["check"]} Qefro</span>
              <p class="compare-answer">&ldquo;Our refund window is 30 days, so an order from 45 days ago isn&rsquo;t eligible. I can connect you with the support team if you&rsquo;d like.&rdquo;</p>
              <p class="compare-source">{ICONS["file"]} Answered from: Refund Policy.pdf</p>
            </article>
          </div>
        </div>
        <div class="why-tri reveal">
          <article class="why-item">
            <div class="why-item-head"><div class="why-ico">{ICONS["bot"]}</div><h3>Grounded in your content</h3></div>
            <p>Every answer comes from sources you&rsquo;ve approved — nothing invented, nothing off-brand.</p>
          </article>
          <article class="why-item">
            <div class="why-item-head"><div class="why-ico">{ICONS["file"]}</div><h3>Shows its sources</h3></div>
            <p>Each response links back to the document it used, so your team can verify every claim.</p>
          </article>
          <article class="why-item">
            <div class="why-item-head"><div class="why-ico">{ICONS["shield"]}</div><h3>Declines, doesn&rsquo;t guess</h3></div>
            <p>When your knowledge base doesn&rsquo;t cover a question, it says so instead of making something up.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section" id="use-cases">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-blue">{ICONS["building"]} Use Cases</span>
          <h2>Built for How Modern Businesses Work</h2>
          <p>Same platform, purpose-fit for every team and industry.</p>
        </div>
{uc_tabs_html()}
      </div>
    </section>

    <section class="section section-alt" id="demo">
      <div class="wrap">
        <div class="demo-split reveal">
          <div class="demo-copy">
            <span class="badge badge-green">{ICONS["play"]} Live Demo</span>
            <h2>Try It Right Now</h2>
            <p>Open the Qefro chat bubble in the bottom-right corner. Ask about pricing, security, integrations, or how grounded answers work — powered by our live demo knowledge base.</p>
            <div class="widget-demo-hint">
              <div class="widget-demo-card">
                <div class="widget-demo-icon">{ICONS["bot"]}</div>
                <div>
                  <strong>Live assistant is active on this page</strong>
                  <p>Click the purple chat button to start a real conversation. Every answer is retrieved from Qefro's demo knowledge base.</p>
                </div>
              </div>
              <p class="widget-demo-suggestions">Try asking: <span>What is Qefro pricing?</span> · <span>How does integration work?</span> · <span>Is my data secure?</span></p>
            </div>
          </div>
          <div class="demo-chat" aria-hidden="true">
            <div class="chat-mock">
              <div class="chat-mock-head">
                <div class="chat-mock-avatar">{ICONS["bot"]}</div>
                <div><strong>Qefro Assistant</strong><span>Powered by your knowledge base</span></div>
              </div>
              <div class="chat-mock-body">
                <div class="chat-bubble ai">Hi! I can answer questions about Qefro using our verified documentation. What would you like to know?</div>
                <div class="chat-bubble user">What is Qefro pricing?</div>
                <div class="chat-bubble ai">Starter is $29/month billed annually ($39 monthly), Growth is $99/month billed annually ($119 monthly), and Enterprise is custom. Start free forever — no credit card required.</div>
              </div>
              <div class="chat-mock-input">
                <span>Type your question…</span>
                <button type="button" aria-label="Send">{ICONS["arrow"]}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="security">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-green">{ICONS["shield"]} Security</span>
          <h2>Enterprise-Grade Trust</h2>
          <p>Your data is your competitive advantage. We treat it that way.</p>
        </div>
        <div class="trust-grid reveal">
          <article class="trust-card"><div class="trust-icon">{ICONS["shield"]}</div><h3>Data never trains AI</h3><p>Your content is never used to improve any AI model. It stays yours, forever.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["lock"]}</div><h3>Tenant-isolated storage</h3><p>Every organisation is completely separated at the database and vector store level.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["server"]}</div><h3>On-premise deployment</h3><p>Run the entire stack in your own cloud or data centre. Full infrastructure control.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["file"]}</div><h3>Audit logs &amp; RBAC</h3><p>SOC 2 compatible. Role-based access, SSO, and complete conversation audit history.</p></article>
        </div>
      </div>
    </section>

    <!-- TODO: Verify these are real customer testimonials/metrics before public launch. If illustrative/placeholder, either replace with real pilot data or add a disclaimer. -->
    <section class="section section-alt">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-yellow">{ICONS["star"]} Testimonials</span>
          <h2>What Our Customers Say</h2>
        </div>
        <div class="t-grid reveal">
          <article class="t-card">
            <div class="t-stars">{ICONS["star"]*5}</div>
            <p class="t-quote">"We cut support tickets by 60% in the first month. Our team now spends time on actual problems, not answering the same FAQ for the hundredth time."</p>
            <div class="t-person"><div class="t-avatar">SC</div><div><strong>Sarah Chen</strong><span>Head of Operations · Meridian Health</span></div></div>
          </article>
          <article class="t-card">
            <div class="t-stars">{ICONS["star"]*5}</div>
            <p class="t-quote">"Onboarding new engineers used to take two weeks. With Qefro indexing our runbooks, they're productive on day three."</p>
            <div class="t-person"><div class="t-avatar">MW</div><div><strong>Marcus Webb</strong><span>VP Engineering · Stackfire</span></div></div>
          </article>
          <article class="t-card">
            <div class="t-stars">{ICONS["star"]*5}</div>
            <p class="t-quote">"The zero-hallucination guarantee was the deciding factor. In healthcare you cannot have an AI making things up — Qefro gets that."</p>
            <div class="t-person"><div class="t-avatar">PN</div><div><strong>Dr. Priya Nair</strong><span>Chief Medical Officer · Apollo Clinics</span></div></div>
          </article>
        </div>
      </div>
    </section>

    <section class="section" id="pricing">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Pricing</span>
          <h2>Plans That Scale With Your Support Team</h2>
          <p>Start free forever. Save ~26% with yearly billing — Starter from $29/mo, Growth from $99/mo.</p>
        </div>
        <div class="direct-answer reveal">
          <p>Qefro pricing starts at <strong>$29/month billed annually</strong> for Starter ($39 monthly), <strong>$99/month billed annually</strong> for Growth ($119 monthly), and custom Enterprise plans with private deployment and SSO.</p>
        </div>
        <div class="billing-toggle reveal" role="group" aria-label="Billing period">
          <button type="button" data-billing="monthly">Monthly</button>
          <button type="button" data-billing="annual" class="is-active">Yearly <span>Save 26%</span></button>
        </div>
        <div class="price-grid reveal">
          <article class="price-card">
            <h3>Starter</h3>
            <div class="price-amount" data-price-annual="$29" data-price-monthly="$39">$29 <span>/month</span></div><p class="price-billed">billed annually · or $39/mo monthly</p>
            <p class="price-desc">For small teams getting started</p>
            <ul class="price-feats">
              <li>{ICONS["check"]} 1,000 conversations/month</li>
              <li>{ICONS["check"]} 50 documents</li>
              <li>{ICONS["check"]} Website widget</li>
              <li>{ICONS["check"]} Email support</li>
              <li>{ICONS["check"]} Custom branding</li>
            </ul>
            <a class="btn btn-plan" href="{PORTAL_LOGIN}">Start Free</a>
          </article>
          <article class="price-card is-popular">
            <div class="price-pop">{ICONS["star"]} Most Popular</div>
            <h3>Growth</h3>
            <div class="price-amount" data-price-annual="$99" data-price-monthly="$119">$99 <span>/month</span></div><p class="price-billed">billed annually · or $119/mo monthly</p>
            <p class="price-desc">For teams that need more power</p>
            <ul class="price-feats">
              <li>{ICONS["check"]} 10,000 conversations/month</li>
              <li>{ICONS["check"]} 500 documents</li>
              <li>{ICONS["check"]} Widget + WhatsApp</li>
              <li>{ICONS["check"]} Custom branding</li>
              <li>{ICONS["check"]} Priority support</li>
              <li>{ICONS["check"]} Analytics</li>
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-primary" href="{PORTAL_LOGIN}">Start Free</a>
          </article>
          <article class="price-card">
            <h3>Enterprise</h3>
            <div class="price-amount">Custom</div>
            <p class="price-desc">For organisations with advanced needs</p>
            <ul class="price-feats">
              <li>{ICONS["check"]} Unlimited conversations</li>
              <li>{ICONS["check"]} Unlimited documents</li>
              <li>{ICONS["check"]} Private deployment</li>
              <li>{ICONS["check"]} SSO &amp; SAML</li>
              <li>{ICONS["check"]} Dedicated CSM</li>
              <li>{ICONS["check"]} SLA guarantee</li>
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-plan" href="/contact">Book a Demo</a>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt">
      <div class="wrap-narrow">
        <div class="section-head reveal">
          <h2>Frequently Asked Questions</h2>
          <p>Everything you need to know before you start.</p>
        </div>
        <div class="faq-list reveal">
{"".join(f'''          <div class="faq-item">
            <button type="button" aria-expanded="false"><span>{q}</span><span class="faq-chevron">{ICONS["chevron"]}</span></button>
            <div class="faq-a"><p>{a}</p></div>
          </div>
''' for q, a in FAQ_ITEMS[:5])}
        </div>
        <p style="text-align:center;margin-top:1.5rem"><a class="btn btn-ghost" href="/faq">View all FAQ</a></p>
      </div>
    </section>

    <section class="cta-final">
      <div class="cta-final-glow" aria-hidden="true"></div>
      <div class="wrap-narrow reveal">
        <span class="badge badge-indigo">{ICONS["sparkles"]} Get Started Today</span>
        <h2>Ready to Give Your Team<br />Instant Answers?</h2>
        <p>Join thousands of teams already saving hours every week. Start free — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_LOGIN}">Start Free Trial {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Talk to Sales</a>
        </div>
      </div>
    </section>
""",
)

# Inner pages
def inner(title, h1, desc, path, active, answer, content, extra_jsonld=None):
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
    <section class="cta-final">
      <div class="cta-final-glow" aria-hidden="true"></div>
      <div class="wrap-narrow reveal">
        <h2>Ready to try Qefro?</h2>
        <p>Start free — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_LOGIN}">Start Free Trial {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Book a Demo</a>
        </div>
      </div>
    </section>
""",
    )


PAGES["features.html"] = inner(
    "Qefro features — RAG support, widget, workspaces",
    "Features",
    "Explore Qefro features: source-grounded refusal-first RAG, document and website ingestion, workspaces, analytics, website widget, API, and WhatsApp.",
    "features.html",
    "features.html",
    "<p>Qefro combines knowledge ingestion, hybrid retrieval, and source-grounded generation so every answer stays inside your approved content.</p>",
    f"""        <div class="cap-grid">
          <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>Source-grounded, refusal-first RAG</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>Document &amp; website ingestion</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["building"]}</div><span>Public &amp; private workspaces</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["msg"]}</div><span>Brandable website widget</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>API and WhatsApp channels</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Analytics &amp; knowledge gaps</span></div>
        </div>""",
)

PAGES["how-it-works.html"] = inner(
    "How Qefro works — upload, retrieve, answer",
    "How it Works",
    "Learn how Qefro works: upload knowledge, configure your assistant, embed the widget, and deliver source-grounded answers in under five minutes.",
    "how-it-works.html",
    "how-it-works.html",
    "<p>Qefro indexes your content, retrieves the most relevant passages when someone asks a question, and generates an answer using only that context.</p>",
    f"""        <div class="steps-grid">
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">01</div></div><h3>Upload Your Knowledge</h3><p>Add documents or crawl websites. Qefro chunks, embeds, and indexes automatically.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">02</div></div><h3>Configure Your Assistant</h3><p>Set workspace visibility, persona, and branding — then copy one widget script.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">03</div></div><h3>Get Instant Answers</h3><p>Every reply stays grounded in your content with sources and an audit trail.</p></article>
        </div>""",
)

PAGES["use-cases.html"] = inner(
    "Qefro use cases — support, HR, IT, engineering",
    "Use Cases",
    "See how teams use Qefro for customer support, employee onboarding, IT helpdesk, compliance lookup, and engineering runbooks.",
    "use-cases.html",
    "use-cases.html",
    "<p>Teams use Qefro to answer repetitive questions for customers and employees using only approved company knowledge.</p>",
    f"""        <div class="uc-grid">
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["building"]}</div><h3>Internal Teams</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Employee onboarding</li><li>{ICONS["chevr"]} HR &amp; policy</li><li>{ICONS["chevr"]} IT helpdesk</li><li>{ICONS["chevr"]} Compliance</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["headphones"]}</div><h3>Customer Support</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} E-commerce FAQs</li><li>{ICONS["chevr"]} Refunds</li><li>{ICONS["chevr"]} Product docs</li><li>{ICONS["chevr"]} Self-service</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["shield"]}</div><h3>Regulated Industries</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Protocols</li><li>{ICONS["chevr"]} Guidelines</li><li>{ICONS["chevr"]} Manuals</li><li>{ICONS["chevr"]} Compliance</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["server"]}</div><h3>Engineering</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Runbooks</li><li>{ICONS["chevr"]} Wikis</li><li>{ICONS["chevr"]} API docs</li><li>{ICONS["chevr"]} Incidents</li></ul></article>
        </div>""",
)

PAGES["security.html"] = inner(
    "Qefro security — tenant isolation, encryption, private deploy",
    "Security",
    "Qefro keeps your data yours: tenant-isolated storage, encryption in transit and at rest, no training on your content, and private deployment options.",
    "security.html",
    "security.html",
    "<p>Qefro never uses your data to train AI models. Content stays tenant-isolated, encrypted, and exportable — with private or on-premise deployment available on Enterprise.</p>",
    f"""        <div class="trust-grid">
          <article class="trust-card"><div class="trust-icon">{ICONS["shield"]}</div><h3>Data never trains AI</h3><p>Your content is never used to improve any AI model.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["lock"]}</div><h3>Tenant isolation</h3><p>Separated at database and vector store level.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["server"]}</div><h3>Private deployment</h3><p>Run in your own cloud or data centre.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["file"]}</div><h3>Audit &amp; RBAC</h3><p>SOC 2 compatible controls and SSO.</p></article>
        </div>""",
)

PAGES["pricing.html"] = inner(
    "Qefro pricing — Starter from $29/mo, Growth from $99/mo, Enterprise",
    "Pricing",
    "Qefro pricing: Starter from $29/month billed annually ($39 monthly), Growth from $99/month billed annually ($119 monthly). Start free forever — no credit card required.",
    "pricing.html",
    "pricing.html",
    "<p>Qefro offers three plans: <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly), and <strong>Enterprise with custom pricing</strong>. Start free forever — no credit card required.</p>",
    f"""        <div class="billing-toggle" role="group" aria-label="Billing period">
          <button type="button" data-billing="monthly">Monthly</button>
          <button type="button" data-billing="annual" class="is-active">Yearly <span>Save 26%</span></button>
        </div>
        <div class="price-grid">
          <article class="price-card"><h3>Starter</h3><div class="price-amount" data-price-annual="$29" data-price-monthly="$39">$29 <span>/month</span></div><p class="price-billed">billed annually · or $39/mo monthly</p><p class="price-desc">For small teams getting started</p><ul class="price-feats"><li>{ICONS["check"]} 1,000 conversations/month</li><li>{ICONS["check"]} 50 documents</li><li>{ICONS["check"]} Website widget</li><li>{ICONS["check"]} Email support</li><li>{ICONS["check"]} Custom branding</li></ul><a class="btn btn-plan" href="{PORTAL_LOGIN}">Start Free</a></article>
          <article class="price-card is-popular"><div class="price-pop">{ICONS["star"]} Most Popular</div><h3>Growth</h3><div class="price-amount" data-price-annual="$99" data-price-monthly="$119">$99 <span>/month</span></div><p class="price-billed">billed annually · or $119/mo monthly</p><p class="price-desc">For teams that need more power</p><ul class="price-feats"><li>{ICONS["check"]} 10,000 conversations/month</li><li>{ICONS["check"]} 500 documents</li><li>{ICONS["check"]} Widget + WhatsApp</li><li>{ICONS["check"]} Custom branding</li><li>{ICONS["check"]} Priority support</li><li>{ICONS["check"]} Analytics</li></ul>{PRICE_FAIR_USE_NOTE}<a class="btn btn-primary" href="{PORTAL_LOGIN}">Start Free</a></article>
          <article class="price-card"><h3>Enterprise</h3><div class="price-amount">Custom</div><p class="price-desc">For advanced security and scale</p><ul class="price-feats"><li>{ICONS["check"]} Unlimited usage options</li><li>{ICONS["check"]} Private deployment</li><li>{ICONS["check"]} SSO &amp; SAML</li><li>{ICONS["check"]} Dedicated CSM</li><li>{ICONS["check"]} SLA guarantee</li></ul>{PRICE_FAIR_USE_NOTE}<a class="btn btn-plan" href="/contact">Book a Demo</a></article>
        </div>""",
    extra_jsonld=[
        PRICING_OFFERS_JSON,
        faq_schema([("How much does Qefro cost?", "Qefro Starter is $29 per month billed annually ($39 monthly), Growth is $99 per month billed annually ($119 monthly), and Enterprise is custom pricing. Start free forever — no credit card required.")]),
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
    title="Qefro FAQ — pricing, security, accuracy, setup",
    description="Frequently asked questions about Qefro: pricing, accuracy, security, integrations, and internal use cases.",
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
    "Contact Qefro sales or support. Email support@qefro.com or start free at qefro.com.",
    "contact.html",
    None,
    '<p>Email <a href="mailto:support@qefro.com"><strong>support@qefro.com</strong></a> for product help, or talk to sales about Enterprise pricing, SSO, and private deployment.</p>',
    f"""        <div class="cap-grid">
          <a class="cap-card" href="mailto:support@qefro.com"><div class="cap-icon">{ICONS["msg"]}</div><span>support@qefro.com</span></a>
          <a class="cap-card" href="{PORTAL_LOGIN}"><div class="cap-icon">{ICONS["zap"]}</div><span>Start free</span></a>
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
        "What is Qefro? — definition",
        "What is Qefro?",
        "Qefro is an AI customer support and knowledge assistant for businesses. It answers questions using only your company’s verified content — documents, FAQs, policies, and websites — so responses stay accurate and grounded.",
        "<p>Teams use Qefro to reduce repetitive tickets, speed onboarding, and keep answers trustworthy across web widget, API, and WhatsApp channels.</p>",
    ),
    (
        "qefro-pricing.html",
        "How much does Qefro cost?",
        "How much does Qefro cost?",
        "Qefro Starter costs $29 per month billed annually ($39 monthly), Growth costs $99 per month billed annually ($119 monthly), and Enterprise is custom pricing. Start free forever — no credit card required.",
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
