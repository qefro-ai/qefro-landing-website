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
ASSET_VERSION = "21"
OG_IMAGE = f"{SITE}/assets/images/og-cover.png"
OG_IMAGE_ALT = (
    "Qefro — AI Workspace Platform for organizations. Customer AI, Employee AI, "
    "and Admin Console on one shared knowledge and Business Tools platform."
)
DEMO_WIDGET_TOKEN = "demo-qefro-widget-token"
BUILD_DATE = date.today().isoformat()
WIDGET_WELCOME = (
    "Hi! I'm the Qefro assistant. Ask how Qefro deploys AI for customers and "
    "employees, or about workspaces, Business Tools, pricing, and security."
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
  <script src="/assets/js/main.js?v={ASSET_VERSION}" defer></script>"""


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
          <a href="/faq">FAQ</a>
          <a href="/contact">Contact</a>
          <a href="/llms.txt">llms.txt</a>
        </nav>
      </div>
      <div class="footer-bottom">
        <p>© <span data-year></span> qefro AI. All rights reserved.</p>
        <p>AI Workspace Platform for customers, employees, and operations.</p>
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
  </script>""" if not path else ""
    return f"""<!DOCTYPE html>
<html lang="en" data-api-url="{API}" data-widget-cdn="{WIDGET_CDN}">
<head>
{meta_block(title, description, path, robots=robots, include_canonical=include_canonical)}
{schemas}
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
        "description": "AI Workspace Platform for organizations — Customer AI, Employee AI, and Admin Console on one shared backend.",
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
        "description": (
            "AI Workspace Platform for organizations: deploy Customer AI on website "
            "and WhatsApp, Employee AI via a branded Internal Portal, and configure "
            "knowledge, Business Tools, and permissions from one Admin Console."
        ),
        "keywords": META_KEYWORDS,
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
        "description": "AI Workspace Platform with knowledge retrieval, Business Tools, website widget, Internal Portal, and WhatsApp.",
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
        "Qefro is an AI Workspace Platform for organizations. Configure AI once in the Admin Console, "
        "deploy Customer AI on your website and WhatsApp, and give employees a branded Internal Portal — "
        "all sharing one knowledge platform, one permission system, and one set of Business Tools.",
    ),
    ("How much does Qefro cost?", "Qefro is freemium — start Free forever (100 conversations/month, 2 documents, 1 Business Tool). Starter is $29/month billed annually ($39 monthly, 5 Business Tools). Growth is $99/month billed annually ($119 monthly, unlimited Business Tools). Enterprise is custom. No credit card required."),
    ("What types of content can I upload?", "PDFs, Word documents, Markdown, plain text — or crawl entire websites automatically. Content is indexed per workspace with source citations when answering."),
    ("How accurate are the answers?", FAQ_ACCURACY_ANSWER_HTML),
    (
        "Is my data secure?",
        "Your data is tenant-isolated and workspace-isolated, encrypted at rest and in transit, "
        "and never used to train AI models. API secrets are encrypted; end-user passwords are "
        "never stored. Private deployment available for Enterprise. "
        "We are building toward SOC 2; contact sales for the current compliance roadmap.",
    ),
    (
        "Can Qefro take action in my systems?",
        "Yes. Connect REST APIs or import OpenAPI specs as Business Tools. The AI can retrieve "
        "live data and perform defined business actions using encrypted credentials "
        "or end-user identity you forward via the widget identify() API.",
    ),
    ("How long does integration take?", "Most teams embed the website widget in under 5 minutes. Identify authenticated users with a few lines of JavaScript. WhatsApp, Internal Portal, and API access are available for deeper rollouts."),
    (
        "Can I use this for employees as well as customers?",
        "Yes. Customer AI runs on your website and WhatsApp. Employee AI runs in a branded Internal Portal "
        "(yourcompany.qefro.com) connected to company knowledge, Business Tools, and workspace permissions.",
    ),
    ("Do you offer enterprise pricing?", "Yes. Enterprise plans include unlimited conversations, private deployment, dedicated support, and custom SLAs. SSO/SAML is on the roadmap — talk to sales about your timeline."),
    (
        "Does Qefro support multiple languages?",
        "Yes. Qefro indexes and answers in the languages present in your knowledge base — including English, Arabic, Tamil, Hindi, and more. "
        "Upload multilingual PDFs and docs; OCR extracts text from scanned pages and images so nothing is left out of search.",
    ),
    (
        "How does widget authentication work?",
        "The embed script loads with a short-lived widget JWT issued by your backend or our portal. "
        "For signed-in users, call identify() with a user id and optional JWT so Business Tools can act on their behalf — "
        "Qefro never stores end-user passwords.",
    ),
    (
        "Can customers talk to a human agent?",
        "Yes. When the AI cannot answer or the customer asks for a person, conversations can be handed off to your team from the inbox. "
        "Full message history and tool execution logs stay attached for context.",
    ),
    (
        "What channels can I deploy on?",
        "Website widget (with optional voice — speech-to-text and text-to-speech), public chat pages, "
        "branded Internal Portal for employees, WhatsApp on Growth+, and direct API/WebSocket access for custom UIs.",
    ),
    (
        "How are workspaces and team roles handled?",
        "Each organization can create AI Workspaces (for example Customer Support, HR, or IT) with their own knowledge, "
        "instructions, Business Tools, conversations, and access rules. "
        "Owner, Admin, and Member roles control who can upload documents, configure tools, manage billing, and invite teammates.",
    ),
]

USE_CASES = [
    ("internal", "Employee AI", "building", [
        "Internal Portal access", "HR & policy queries", "IT helpdesk", "SOP & compliance lookup",
        "Team wiki search", "Benefits lookup", "Finance procedures", "Knowledge sharing",
    ]),
    ("support", "Customer Support", "headphones", [
        "Website & WhatsApp AI", "Order & refund policies", "Product documentation", "Self-service support",
        "Business Tool actions", "Returns handling", "Lead capture", "Human handoff",
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
def home_faq_preview(n: int = 6) -> str:
    return "".join(
        f"""          <div class="faq-item">
            <button type="button" aria-expanded="false"><span>{q}</span><span class="faq-chevron">{ICONS["chevron"]}</span></button>
            <div class="faq-a"><p>{a}</p></div>
          </div>
"""
        for q, a in FAQ_ITEMS[:n]
    )


def home_body() -> str:
    return f"""    <section class="hero" aria-label="Hero">
      <div class="hero-grid" aria-hidden="true"></div>
      <div class="wrap-5xl hero-inner">
        <span class="eyebrow">{ICONS["sparkles"]} AI Workspace Platform</span>
        <h1>
          <span class="hero-line">Your Company&rsquo;s</span>
          <span class="hero-accent">AI Workspace</span>
        </h1>
        <p class="hero-sub">Qefro is one AI platform for organizations. Answer customer questions, help employees, search company knowledge, connect to internal APIs, and perform business actions securely — with organizational permissions enforced — from a single shared backend.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Book Demo</a>
        </div>
        <div class="hero-checks">
          <span>{ICONS["check"]} One platform · three experiences</span>
          <span>{ICONS["check"]} Free forever · no credit card</span>
          <span>{ICONS["check"]} Customers, employees &amp; ops</span>
          <span>{ICONS["check"]} Your auth stays yours</span>
        </div>
        <div class="arch-diagram reveal" role="img" aria-label="Qefro platform: Website Widget, Internal Portal, and WhatsApp on a shared AI platform with Knowledge, Business Tools, RBAC, Conversations, Voice, and Analytics">
          <div class="arch-hub">
            <span class="arch-hub-label">Qefro</span>
            <span class="arch-hub-sub">Shared AI Platform</span>
          </div>
          <div class="arch-channels">
            <div class="arch-channel">
              <span class="arch-channel-icon">{ICONS["globe"]}</span>
              <strong>Website Widget</strong>
              <span>Customer AI</span>
            </div>
            <div class="arch-channel arch-channel-accent">
              <span class="arch-channel-icon">{ICONS["building"]}</span>
              <strong>Internal Portal</strong>
              <span>Employee AI</span>
            </div>
            <div class="arch-channel">
              <span class="arch-channel-icon">{ICONS["msg"]}</span>
              <strong>WhatsApp</strong>
              <span>Customer AI</span>
            </div>
          </div>
          <div class="arch-foundation">
            <span>Knowledge</span>
            <span>Business Tools</span>
            <span>RBAC</span>
            <span>Conversations</span>
            <span>Voice</span>
            <span>Analytics</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section-facts" id="trusted" aria-label="Trusted by teams">
      <div class="wrap-5xl">
        <p class="facts-label">Trusted by teams deploying organizational AI</p>
        <div class="logo-cloud" aria-hidden="true">
          <span class="logo-placeholder">Customer Support</span>
          <span class="logo-placeholder">SaaS</span>
          <span class="logo-placeholder">Healthcare</span>
          <span class="logo-placeholder">Education</span>
          <span class="logo-placeholder">Retail</span>
          <span class="logo-placeholder">Professional Services</span>
        </div>
      </div>
    </section>

    <section class="section" id="platform">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} One Platform</span>
          <h2>One platform. Multiple AI experiences.</h2>
          <p>Configure AI once. Deploy it everywhere your organization needs it — customers, employees, and operations — on one shared knowledge platform, permission system, and set of Business Tools.</p>
        </div>
        <div class="facts-grid reveal">
          <div class="fact"><div class="fact-v">Customer AI</div><div class="fact-k">Website, WhatsApp &amp; voice</div></div>
          <div class="fact"><div class="fact-v">Employee AI</div><div class="fact-k">Branded Internal Portal</div></div>
          <div class="fact"><div class="fact-v">Admin Console</div><div class="fact-k">Configure once, govern everywhere</div></div>
          <div class="fact"><div class="fact-v">Shared backend</div><div class="fact-k">Knowledge · Tools · RBAC</div></div>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="experiences">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["sparkles"]} Three Experiences</span>
          <h2>Customer AI. Employee AI. Admin Console.</h2>
          <p>Three surfaces. One organizational AI system.</p>
        </div>
        <div class="exp-grid reveal">
          <article class="exp-card">
            <div class="exp-icon">{ICONS["headphones"]}</div>
            <h3>Customer AI</h3>
            <p>Meet customers on your website and WhatsApp with AI that knows your business and can take defined actions.</p>
            <ul>
              <li>Website widget &amp; live chat</li>
              <li>Voice in the widget</li>
              <li>FAQ &amp; knowledge answers</li>
              <li>Business actions via your APIs</li>
              <li>Lead capture &amp; human handoff</li>
              <li>Multilingual responses</li>
            </ul>
          </article>
          <article class="exp-card exp-card-featured">
            <div class="exp-icon">{ICONS["building"]}</div>
            <h3>Employee AI</h3>
            <p>Give every team a ChatGPT-style workspace connected to company knowledge, APIs, and permissions.</p>
            <ul>
              <li>Branded Internal Portal</li>
              <li>Company knowledge search</li>
              <li>HR, IT, Finance, Sales, Engineering</li>
              <li>Workspace-specific AI</li>
              <li>Role-based access</li>
              <li>Voice &amp; document search</li>
            </ul>
          </article>
          <article class="exp-card">
            <div class="exp-icon">{ICONS["server"]}</div>
            <h3>Admin Console</h3>
            <p>Configure everything in one place — then deploy the same AI across every experience.</p>
            <ul>
              <li>Knowledge &amp; Business Tools</li>
              <li>Teams, members &amp; permissions</li>
              <li>Workspaces &amp; branding</li>
              <li>Widget &amp; WhatsApp setup</li>
              <li>Analytics &amp; inbox</li>
              <li>Workspace management</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

{product_screenshots_html()}
    <section class="section" id="workspaces">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-blue">{ICONS["building"]} AI Workspaces</span>
          <h2>Organize AI around how your company works</h2>
          <p>AI Workspaces are the core unit of Qefro. Create a workspace for each team or use case — each with its own knowledge, instructions, Business Tools, conversations, and permissions.</p>
        </div>
        <div class="workspace-grid reveal">
          <article class="workspace-card"><h3>Customer Support</h3><p>Policies, order lookups, tickets, and handoff.</p></article>
          <article class="workspace-card"><h3>HR</h3><p>Handbooks, benefits, leave, and onboarding.</p></article>
          <article class="workspace-card"><h3>IT Helpdesk</h3><p>Runbooks, access requests, and SOPs.</p></article>
          <article class="workspace-card"><h3>Sales Assistant</h3><p>Product knowledge, CRM queries, and playbooks.</p></article>
          <article class="workspace-card"><h3>Finance</h3><p>Policies, approvals, and internal procedures.</p></article>
          <article class="workspace-card"><h3>Engineering</h3><p>Docs, APIs, incidents, and architecture notes.</p></article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="business-tools">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["server"]} Business Tools</span>
          <h2>Connect AI directly to your business systems</h2>
          <p>Import OpenAPI specs or configure REST endpoints. Qefro executes defined actions with encrypted credentials, schema validation, and execution logs — MCP connectors coming soon.</p>
        </div>
        <div class="scenario-grid reveal">
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Where is my order?</p>
            <div class="scenario-flow"><span>AI calls your Order API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Live tracking returned</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Book an appointment</p>
            <div class="scenario-flow"><span>AI calls your Booking API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Appointment confirmed</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Employee</span> Approve my leave request</p>
            <div class="scenario-flow"><span>AI calls your HR API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Request submitted</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Ops</span> Check inventory for SKU-19</p>
            <div class="scenario-flow"><span>AI calls your ERP/API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Stock levels returned</span></div>
          </article>
        </div>
        <div class="cap-panel reveal" style="margin-top:2.5rem">
          <div class="cap-grid">
            <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>REST APIs</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>OpenAPI import</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["shield"]}</div><span>Secure execution</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["lock"]}</div><span>Encrypted secrets</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Execution logs</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>Identity forwarding</span></div>
          </div>
          <p class="integrations-note">Examples: track or cancel orders, create tickets, query CRM, call ERP — via your APIs, not as native replacements for those systems.</p>
        </div>
      </div>
    </section>

    <section class="section" id="knowledge">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["file"]} Knowledge Platform</span>
          <h2>One knowledge layer for the whole organization</h2>
          <p>Upload documents or crawl your website. Qefro indexes content automatically, answers with source citations, and keeps knowledge isolated by workspace.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card">
            <h3>Ingest</h3>
            <ul>
              <li>PDF, DOCX, Markdown, TXT</li>
              <li>Website crawling</li>
              <li>OCR for scans &amp; images</li>
              <li>Automatic indexing</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Retrieve</h3>
            <ul>
              <li>Hybrid RAG search</li>
              <li>Source citations</li>
              <li>Refusal when unsure</li>
              <li>Multilingual content</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Govern</h3>
            <ul>
              <li>Workspace isolation</li>
              <li>Public &amp; private scopes</li>
              <li>Team permissions</li>
              <li>Document reindex</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Improve</h3>
            <ul>
              <li>Conversation analytics</li>
              <li>Knowledge gap signals</li>
              <li>Inbox review</li>
              <li>Human handoff context</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="security">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-green">{ICONS["shield"]} Security</span>
          <h2>Enterprise-ready by design</h2>
          <p>Multi-tenant architecture with workspace isolation, team-based RBAC, encrypted secrets, and conversation isolation — so one organization never sees another&rsquo;s data.</p>
        </div>
        <div class="trust-grid reveal">
          <article class="trust-card"><div class="trust-icon">{ICONS["building"]}</div><h3>Multi-tenant isolation</h3><p>Tenant boundaries at the database and vector store. No cross-organization data leakage.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["lock"]}</div><h3>Workspace &amp; conversation isolation</h3><p>Knowledge, tools, and threads stay scoped to the workspaces and permissions you define.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["shield"]}</div><h3>Team-based RBAC</h3><p>Owner, Admin, and Member roles control documents, Business Tools, billing, and invites.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["server"]}</div><h3>Secure Business Tool execution</h3><p>Encrypted secrets, SSRF protections, schema validation, and full execution logs.</p></article>
        </div>
        <p class="integrations-note reveal" style="text-align:center;margin-top:1.75rem"><a href="/security">Read the security overview</a> · SSO / SAML on the Enterprise roadmap</p>
      </div>
    </section>

    <section class="section" id="integrations">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-blue">{ICONS["globe"]} Integrations</span>
          <h2>Deploy where your people already work</h2>
          <p>Same AI. Same knowledge. Same Business Tools. Different surfaces for customers and employees.</p>
        </div>
        <div class="channel-grid reveal">
          <article class="channel-card">
            <div class="channel-icon">{ICONS["globe"]}</div>
            <h3>Website Widget</h3>
            <p>Embed in minutes. Answer questions, run Business Tools, capture leads, and transfer to humans when needed.</p>
          </article>
          <article class="channel-card">
            <div class="channel-icon">{ICONS["building"]}</div>
            <h3>Internal Portal</h3>
            <p>Employees get <code>yourcompany.qefro.com</code> — a branded AI workspace connected to company knowledge and APIs, respecting permissions.</p>
          </article>
          <article class="channel-card">
            <div class="channel-icon">{ICONS["msg"]}</div>
            <h3>WhatsApp</h3>
            <p>Native WhatsApp conversations powered by the same AI, knowledge, and Business Tools. Available on Growth and Enterprise.</p>
          </article>
        </div>
        <div class="dev-split reveal" style="margin-top:3rem">
          <div class="dev-copy">
            <span class="badge badge-blue">{ICONS["bot"]} Authenticated users</span>
            <h2>Your auth stays yours</h2>
            <p>Qefro is not an identity provider. Forward signed-in identity with <code>identify()</code> so Business Tools act on behalf of real users — passwords never touch Qefro.</p>
          </div>
          <pre class="code-panel" tabindex="0"><code>widget.identify({{
  id: user.id,
  email: user.email,
  auth: {{
    mode: "jwt",
    token: userJwt
  }}
}});</code></pre>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="why-qefro">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["chart"]} Comparison</span>
          <h2>Traditional AI chatbot vs Qefro</h2>
          <p>Answering questions is table stakes. Organizations need actions, employee access, and workspace permissions.</p>
        </div>
        <div class="table-wrap reveal">
          <table class="compare-table">
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

    <section class="section" id="use-cases">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-blue">{ICONS["building"]} Solutions</span>
          <h2>Built for how modern organizations work</h2>
          <p>Customer support, internal IT, regulated teams, and engineering — same platform, purpose-fit workspaces.</p>
        </div>
{uc_tabs_html()}
        <p class="integrations-note reveal" style="text-align:center;margin-top:1.75rem">Also a fit for SaaS, healthcare, education, manufacturing, retail, professional services, and government teams. <a href="/use-cases">Explore solutions</a></p>
      </div>
    </section>

    <section class="section section-alt" id="demo">
      <div class="wrap">
        <div class="demo-split reveal">
          <div class="demo-copy">
            <span class="badge badge-green">{ICONS["play"]} Live demo</span>
            <h2>Try Customer AI on this page</h2>
            <p>Open the chat bubble in the corner. Ask about the platform, workspaces, Business Tools, pricing, or security.</p>
            <div class="widget-demo-hint">
              <div class="widget-demo-card">
                <div class="widget-demo-icon">{ICONS["bot"]}</div>
                <div>
                  <strong>Live assistant is active on this page</strong>
                  <p>Answers come from Qefro&rsquo;s demo knowledge base.</p>
                </div>
              </div>
              <p class="widget-demo-suggestions">Try: <span>What is Qefro?</span> · <span>What are AI Workspaces?</span> · <span>Is my data secure?</span></p>
            </div>
          </div>
          <div class="demo-chat" aria-hidden="true">
            <div class="chat-mock">
              <div class="chat-mock-head">
                <div class="chat-mock-avatar">{ICONS["bot"]}</div>
                <div><strong>Qefro Assistant</strong><span>AI Workspace Platform</span></div>
              </div>
              <div class="chat-mock-body">
                <div class="chat-bubble ai">Hi! I can explain how Qefro deploys AI for customers and employees from one platform.</div>
                <div class="chat-bubble user">What makes Qefro an AI platform?</div>
                <div class="chat-bubble ai">One shared backend powers Customer AI, Employee AI, and the Admin Console — with knowledge, Business Tools, and permissions in one place.</div>
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

    <section class="section" id="pricing">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Pricing</span>
          <h2>Plans that scale with your organization</h2>
          <p>Freemium — Free forever. Save ~26% with yearly billing — Starter from $29/mo, Growth from $99/mo.</p>
        </div>
        <div class="direct-answer reveal">
          <p>Qefro has a <strong>Free plan</strong> (100 conversations/month, 2 documents, 1 Business Tool), then <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly), and custom Enterprise plans.</p>
        </div>
        <div class="billing-toggle reveal" role="group" aria-label="Billing period">
          <button type="button" data-billing="monthly">Monthly</button>
          <button type="button" data-billing="annual" class="is-active">Yearly <span>Save 26%</span></button>
        </div>
        <div class="price-grid reveal">
          <article class="price-card">
            <h3>Free</h3>
            <div class="price-amount">$0</div>
            <p class="price-desc">Forever free — no credit card</p>
            <ul class="price-feats">
              <li>{ICONS["check"]} 100 conversations/month</li>
              <li>{ICONS["check"]} 2 documents</li>
              <li>{ICONS["check"]} 1 Business Tool</li>
              <li>{ICONS["check"]} 2 team members</li>
              <li>{ICONS["check"]} Website widget</li>
              <li>{ICONS["check"]} Community support</li>
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}">Start Free</a>
          </article>
          <article class="price-card">
            <h3>Starter</h3>
            <div class="price-amount" data-price-annual="$29" data-price-monthly="$39">$29 <span>/month</span></div><p class="price-billed">billed annually · or $39/mo monthly</p>
            <p class="price-desc">For small teams getting started</p>
            <ul class="price-feats">
              <li>{ICONS["check"]} 1,000 conversations/month</li>
              <li>{ICONS["check"]} 50 documents</li>
              <li>{ICONS["check"]} 5 Business Tools</li>
              <li>{ICONS["check"]} Website widget</li>
              <li>{ICONS["check"]} Email support</li>
              <li>{ICONS["check"]} Custom branding</li>
            </ul>
            <a class="btn btn-plan" href="{PORTAL_SIGNUP}">Get Started</a>
          </article>
          <article class="price-card is-popular">
            <div class="price-pop">{ICONS["star"]} Most Popular</div>
            <h3>Growth</h3>
            <div class="price-amount" data-price-annual="$99" data-price-monthly="$119">$99 <span>/month</span></div><p class="price-billed">billed annually · or $119/mo monthly</p>
            <p class="price-desc">For teams deploying across channels</p>
            <ul class="price-feats">
              <li>{ICONS["check"]} 10,000 conversations/month</li>
              <li>{ICONS["check"]} 500 documents</li>
              <li>{ICONS["check"]} Widget + WhatsApp</li>
              <li>{ICONS["check"]} Unlimited Business Tools</li>
              <li>{ICONS["check"]} Priority support</li>
              <li>{ICONS["check"]} Analytics</li>
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-primary" href="{PORTAL_SIGNUP}">Get Started</a>
          </article>
          <article class="price-card">
            <h3>Enterprise</h3>
            <div class="price-amount">Custom</div>
            <p class="price-desc">For organizations with advanced needs</p>
            <ul class="price-feats">
              <li>{ICONS["check"]} Unlimited conversations</li>
              <li>{ICONS["check"]} Unlimited documents</li>
              <li>{ICONS["check"]} Private deployment</li>
              <li>{ICONS["check"]} SSO &amp; SAML (roadmap)</li>
              <li>{ICONS["check"]} Dedicated CSM</li>
              <li>{ICONS["check"]} Unlimited Business Tools</li>
              <li>{ICONS["check"]} SLA guarantee</li>
            </ul>
            {PRICE_FAIR_USE_NOTE}
            <a class="btn btn-plan" href="/contact">Talk to Sales</a>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="faq">
      <div class="wrap-narrow">
        <div class="section-head reveal">
          <h2>Frequently asked questions</h2>
          <p>Everything you need to know before you start.</p>
        </div>
        <div class="faq-list reveal">
{home_faq_preview()}
        </div>
        <p style="text-align:center;margin-top:1.5rem"><a class="btn btn-ghost" href="/faq">View all FAQ</a></p>
      </div>
    </section>

    <section class="cta-final">
      <div class="cta-final-glow" aria-hidden="true"></div>
      <div class="wrap-narrow reveal">
        <span class="badge badge-indigo">{ICONS["sparkles"]} Get started today</span>
        <h2>Deploy your company&rsquo;s AI workspace.</h2>
        <p>Start free for Customer AI, Employee AI, and the Admin Console — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Book Demo</a>
        </div>
        <p class="integrations-note" style="margin-top:1.25rem"><a href="/contact">Talk to Sales</a> for Enterprise</p>
      </div>
    </section>
"""


PAGES["index.html"] = page(
    title="Qefro — AI Workspace Platform for Organizations",
    description=(
        "Qefro is an AI Workspace Platform for organizations. Deploy Customer AI, "
        "Employee AI, and an Admin Console on one shared knowledge and Business Tools platform. "
        "Website widget, Internal Portal, WhatsApp. Start free — no credit card."
    ),
    path="",
    jsonld=[ORG_JSON, WEBSITE_JSON, SOFTWARE_JSON],
    body=home_body(),
)

# Inner pages — detailed content for menu-linked pages
def features_page_content() -> str:
    return f"""        <div class="outcome-grid">
          <article class="outcome-card"><h3>Knowledge Platform</h3><ul><li>PDF, DOCX, Markdown, TXT</li><li>Website crawler</li><li>OCR for scans &amp; images</li><li>Multilingual (EN, AR, TA, HI+)</li><li>Hybrid BM25 + vector search</li><li>Source citations &amp; refusal when unsure</li></ul></article>
          <article class="outcome-card"><h3>Business Tools</h3><ul><li>REST &amp; OpenAPI import</li><li>Encrypted API credentials</li><li>End-user identity via identify()</li><li>SSRF &amp; DNS-pinned webhooks</li><li>Execution logs &amp; schema validation</li><li>Conversation variables</li></ul></article>
          <article class="outcome-card"><h3>AI Experiences</h3><ul><li>Website widget (JWT auth)</li><li>Internal Portal for employees</li><li>WhatsApp (Growth+)</li><li>Voice STT/TTS in widget</li><li>WebSocket streaming</li><li>Handoff to human agents</li></ul></article>
          <article class="outcome-card"><h3>Admin Console</h3><ul><li>AI Workspaces (public &amp; private)</li><li>Owner / Admin / Member RBAC</li><li>Analytics &amp; inbox</li><li>Branding &amp; channel setup</li><li>Email OTP verification</li><li>Document reindex</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["file"]} Knowledge</span>
          <h2>Grounded answers from your content — in any language</h2>
          <p>Upload documents or crawl your site. Qefro chunks, embeds, and indexes automatically. Answers cite sources and refuse when nothing relevant is found — no confident guessing.</p>
        </div>
        <div class="cap-grid reveal">
          <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>PDF &amp; DOCX ingestion</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>Multilingual RAG</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>OCR for images &amp; scans</span></div>
          <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Hybrid retrieval</span></div>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-purple">{ICONS["server"]} Business Tools</span>
          <h2>Connect AI to the systems your organization already runs</h2>
          <p>Import OpenAPI or configure REST endpoints for order lookup, booking, ticketing, CRM queries, or ERP reads. Credentials are encrypted; outbound calls use HTTPS with SSRF protections.</p>
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
          <h2>Customer AI, Employee AI, and Admin Console</h2>
          <p>One script tag for the website widget. Branded Internal Portal for employees. WhatsApp on Growth+. Optional voice in the widget. Public chat URLs for help centers.</p>
        </div>
        <div class="dev-split reveal">
          <div class="dev-copy">
            <h3>Authenticated users in minutes</h3>
            <p>Your app owns login. Forward identity with <code>identify()</code> so Business Tools act on behalf of signed-in users — passwords never touch Qefro.</p>
          </div>
          <pre class="code-panel" tabindex="0"><code>widget.identify({{
  id: user.id,
  email: user.email,
  auth: {{ mode: "jwt", token: userJwt }}
}});</code></pre>
        </div>"""


def how_it_works_page_content() -> str:
    return f"""        <div class="steps-grid">
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">01</div></div><h3>Configure in Admin Console</h3><p>Create AI Workspaces, upload knowledge, set instructions, invite teams, and define Owner / Admin / Member permissions.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">02</div></div><h3>Connect Business Tools</h3><p>Import OpenAPI or configure REST endpoints. Store encrypted credentials or forward end-user JWTs via identify(). Scope tools per workspace.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">03</div></div><h3>Deploy experiences</h3><p>Launch Customer AI on website and WhatsApp, and Employee AI on a branded Internal Portal — same knowledge and tools underneath.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">04</div></div><h3>Monitor &amp; improve</h3><p>Review conversations, analytics, and tool runs. Hand off to humans when needed. Reindex documents as policies change.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>What we handle for you</h2>
          <p>No RAG pipeline to build, no LLM hosting, no embedding model management. Qefro runs retrieval, tool calling, PII scrubbing, and rate limits — you focus on knowledge, APIs, and permissions.</p>
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
            <li>REST API for documents, tools, conversations, and billing</li>
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
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["server"]}</div><h3>Engineering &amp; Ops</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Runbook &amp; incident playbooks</li><li>{ICONS["chevr"]} API docs + OpenAPI tools</li><li>{ICONS["chevr"]} Multilingual wiki search</li><li>{ICONS["chevr"]} Internal self-service portal</li></ul></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <span class="badge badge-indigo">{ICONS["zap"]} Real scenarios</span>
          <h2>Knowledge plus live business actions</h2>
          <p>Every solution combines grounded document answers with optional Business Tool calls through your existing systems.</p>
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
          <article class="trust-card"><div class="trust-icon">{ICONS["lock"]}</div><h3>Your auth stays yours</h3><p>Qefro is not an identity provider. Forward JWTs or session ids via identify() — end-user passwords are never stored or processed by Qefro.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["shield"]}</div><h3>Widget JWT auth</h3><p>Embeds load with short-lived widget tokens. Messages are bounded (8 KB), PII is scrubbed before model calls, and tenants cannot access each other&rsquo;s data.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["building"]}</div><h3>Tenant &amp; workspace isolation</h3><p>Multi-tenant by design at the database and vector store level. AI Workspaces control which knowledge and tools each experience can use.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["file"]}</div><h3>Encrypted secrets &amp; logs</h3><p>Business Tool credentials encrypted at rest. HTTPS-only outbound calls with SSRF protections and DNS-pinned webhooks. Full conversation and tool execution history.</p></article>
        </div>
        <div class="section-head reveal" style="text-align:left;margin-top:3.5rem">
          <h2>Enterprise platform controls</h2>
          <p>Built for organizational AI — not demo chat experiences.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card"><h3>Access control</h3><ul><li>Owner / Admin / Member RBAC</li><li>Email OTP — no password storage</li><li>Billing actions restricted to owners</li><li>Workspace-scoped documents &amp; tools</li></ul></article>
          <article class="outcome-card"><h3>Data handling</h3><ul><li>PII scrubbing on outbound LLM calls</li><li>Never used to train AI models</li><li>Encrypted at rest &amp; in transit</li><li>Conversation isolation</li></ul></article>
          <article class="outcome-card"><h3>Tool execution</h3><ul><li>OpenAPI schema validation</li><li>SSRF &amp; DNS pinning for webhooks</li><li>Per-tool allow-from-public-chat toggle</li><li>Execution logs for accountability</li></ul></article>
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
          <article class="price-card"><h3>Free</h3><div class="price-amount">$0</div><p class="price-desc">Forever free — no credit card</p><ul class="price-feats"><li>{ICONS["check"]} 100 conversations/month</li><li>{ICONS["check"]} 2 documents</li><li>{ICONS["check"]} 1 Business Tool</li><li>{ICONS["check"]} 2 team members</li><li>{ICONS["check"]} Website widget + voice</li><li>{ICONS["check"]} Multilingual RAG</li><li>{ICONS["check"]} Community support</li></ul><a class="btn btn-plan" href="{PORTAL_SIGNUP}">Start Free</a></article>
          <article class="price-card"><h3>Starter</h3><div class="price-amount" data-price-annual="$29" data-price-monthly="$39">$29 <span>/month</span></div><p class="price-billed">billed annually · or $39/mo monthly</p><p class="price-desc">For small teams getting started</p><ul class="price-feats"><li>{ICONS["check"]} 1,000 conversations/month</li><li>{ICONS["check"]} 50 documents</li><li>{ICONS["check"]} 5 Business Tools</li><li>{ICONS["check"]} Website widget + voice</li><li>{ICONS["check"]} Custom branding</li><li>{ICONS["check"]} Email support</li></ul><a class="btn btn-plan" href="{PORTAL_SIGNUP}">Get Started</a></article>
          <article class="price-card is-popular"><div class="price-pop">{ICONS["star"]} Most Popular</div><h3>Growth</h3><div class="price-amount" data-price-annual="$99" data-price-monthly="$119">$99 <span>/month</span></div><p class="price-billed">billed annually · or $119/mo monthly</p><p class="price-desc">For teams that need more power</p><ul class="price-feats"><li>{ICONS["check"]} 10,000 conversations/month</li><li>{ICONS["check"]} 500 documents</li><li>{ICONS["check"]} Widget + WhatsApp + voice</li><li>{ICONS["check"]} Unlimited Business Tools</li><li>{ICONS["check"]} Analytics &amp; agent handoff</li><li>{ICONS["check"]} Priority support</li></ul>{PRICE_FAIR_USE_NOTE}<a class="btn btn-primary" href="{PORTAL_SIGNUP}">Get Started</a></article>
          <article class="price-card"><h3>Enterprise</h3><div class="price-amount">Custom</div><p class="price-desc">For advanced security and scale</p><ul class="price-feats"><li>{ICONS["check"]} Unlimited usage options</li><li>{ICONS["check"]} Unlimited Business Tools</li><li>{ICONS["check"]} Private deployment</li><li>{ICONS["check"]} SSO &amp; SAML (roadmap)</li><li>{ICONS["check"]} Dedicated CSM</li><li>{ICONS["check"]} SLA guarantee</li></ul>{PRICE_FAIR_USE_NOTE}<a class="btn btn-plan" href="/contact">Book a Demo</a></article>
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
          <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>Business Tools &amp; OpenAPI</span></div>
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
    "Qefro AI Workspace Platform: knowledge RAG, Business Tools (REST/OpenAPI), Customer AI widget, Internal Portal, WhatsApp, voice, AI Workspaces, RBAC, and agent handoff.",
    "features.html",
    "features",
    "<p>Qefro combines a <strong>knowledge platform</strong>, <strong>Business Tools</strong>, and <strong>three AI experiences</strong> — Customer AI, Employee AI, and Admin Console — so organizations can answer questions, take secure actions, and govern access in one place.</p>",
    features_page_content(),
)

PAGES["how-it-works.html"] = inner(
    "Qefro platform — configure once, deploy everywhere",
    "Platform",
    "How the Qefro platform works: configure AI Workspaces and Business Tools in the Admin Console, then deploy Customer AI and Employee AI — no RAG infrastructure required.",
    "how-it-works.html",
    "how-it-works",
    "<p>Four steps from configuration to production organizational AI. We handle vectors, models, PII scrubbing, and tool execution — you bring knowledge, APIs, and permissions.</p>",
    how_it_works_page_content(),
)

PAGES["use-cases.html"] = inner(
    "Qefro solutions — Customer AI, Employee AI, HR, IT, engineering",
    "Solutions",
    "Teams use Qefro for Customer AI with live API actions, Employee AI portals for HR/IT, regulated compliance lookup, and engineering runbooks — multilingual RAG included.",
    "use-cases.html",
    "use-cases",
    "<p>Same AI Workspace Platform for customer-facing experiences and internal operations — grounded answers from docs plus optional Business Tool actions through your existing APIs.</p>",
    use_cases_page_content(),
)

PAGES["security.html"] = inner(
    "Qefro security — enterprise AI Workspace Platform",
    "Security",
    "Enterprise security for organizational AI: multi-tenant isolation, workspace RBAC, encrypted secrets, conversation isolation, SSRF-protected Business Tools, and execution logs.",
    "security.html",
    "security",
    "<p>Authentication stays in your app. Qefro never stores passwords. Secrets are encrypted, messages are bounded and scrubbed, and every tool call is logged.</p>",
    security_page_content(),
)

PAGES["pricing.html"] = inner(
    "Qefro pricing — Starter from $29/mo, Growth from $99/mo, Enterprise",
    "Pricing",
    "Qefro pricing: Free forever (100 conversations, multilingual RAG, widget + voice). Starter $29/mo annual, Growth $99/mo with WhatsApp and unlimited Business Tools.",
    "pricing.html",
    "pricing",
    "<p>Start free with multilingual RAG, widget JWT auth, and voice. Scale to WhatsApp and unlimited Business Tools on Growth. Enterprise adds private deployment and custom SLAs.</p>",
    pricing_page_content(),
    extra_jsonld=[
        PRICING_OFFERS_JSON,
        faq_schema([("How much does Qefro cost?", "Qefro is freemium: Free plan includes 100 conversations/month, 2 documents, and 1 Business Tool. Starter is $29/month billed annually ($39 monthly) with 5 Business Tools. Growth is $99/month billed annually ($119 monthly) with unlimited Business Tools. Enterprise is custom. No credit card required to start Free.")]),
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
    description="FAQ about the Qefro AI Workspace Platform: pricing, accuracy, security, Business Tools, Internal Portal, workspaces, and setup.",
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
        "Qefro is an AI Workspace Platform for organizations. Configure AI once in the Admin Console, deploy Customer AI on website and WhatsApp, and give employees a branded Internal Portal — sharing one knowledge platform, permission system, and set of Business Tools.",
        "<p>Unlike a traditional AI chatbot that only answers FAQs, Qefro is a complete platform: Customer AI, Employee AI, and Admin Console on one shared backend — with grounded knowledge answers, secure Business Tool actions via your APIs, and workspace-level permissions.</p>",
    ),
    (
        "qefro-pricing.html",
        "How much does Qefro cost?",
        "How much does Qefro cost?",
        "Qefro is freemium. Free forever: 100 conversations/month, 2 documents, 1 Business Tool. Starter from $29/month billed annually (5 Business Tools). Growth from $99/month billed annually (unlimited Business Tools). Enterprise is custom. No credit card required.",
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
