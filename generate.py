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
ASSET_VERSION = "20"
OG_IMAGE = f"{SITE}/assets/images/og-cover.png"
OG_IMAGE_ALT = (
    "Qefro — AI Customer Support Platform. Knowledge, business integrations, and AI "
    "for accurate answers and secure actions."
)
DEMO_WIDGET_TOKEN = "demo-qefro-widget-token"
BUILD_DATE = date.today().isoformat()
WIDGET_WELCOME = (
    "Hi! I'm the Qefro assistant. Ask how Qefro combines knowledge and business "
    "integrations, or about pricing, security, and the widget identify() API."
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
    ("features", "Features"),
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
  <meta name="keywords" content="AI Customer Support, AI Support Platform, Business AI, AI Widget, AI Customer Service, WhatsApp AI, RAG Platform, AI Support Software" />
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
        <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI customer support platform logo" width="40" height="40" />
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
          <img class="logo-light" src="/assets/images/qefro-logo.png?v={ASSET_VERSION}" alt="Qefro AI customer support platform logo" width="40" height="40" />
          <img class="logo-dark" src="/assets/images/qefro-logo-dark.png?v={ASSET_VERSION}" alt="" width="40" height="40" aria-hidden="true" />
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
        <p>AI customer support that answers accurately and securely takes action.</p>
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
        "description": "AI customer support platform that combines knowledge, business integrations, and AI.",
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
            "AI customer support platform: ground answers in your knowledge base, "
            "securely call your business APIs, and deploy on website or WhatsApp — "
            "without replacing your authentication system."
        ),
        "keywords": (
            "AI Customer Support, AI Support Platform, Business AI, AI Widget, "
            "AI Customer Service, WhatsApp AI, RAG Platform, AI Support Software"
        ),
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
        "description": "AI customer support platform with knowledge retrieval, business integrations, website widget, and WhatsApp.",
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
    (
        "What is Qefro?",
        "Qefro is an AI customer support platform. It answers from your knowledge base, "
        "securely calls your existing business APIs (Business Tools / OpenAPI), and deploys "
        "to website and WhatsApp — without replacing your authentication system.",
    ),
    ("How much does Qefro cost?", "Qefro is freemium — start Free forever (100 conversations/month, 5 documents, 1 Business Tool). Starter is $29/month billed annually ($39 monthly, 5 Business Tools). Growth is $99/month billed annually ($119 monthly, unlimited Business Tools). Enterprise is custom. No credit card required."),
    ("What types of content can I upload?", "PDFs, Word documents, Markdown, plain text — or crawl entire websites automatically. Our pipeline processes and indexes everything."),
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
        "live data (orders, bookings) and perform support actions using encrypted credentials "
        "or end-user identity you forward via the widget identify() API.",
    ),
    ("How long does integration take?", "Most teams are live in under 5 minutes — paste one script tag on your site. Identify authenticated users with a few lines of JavaScript. API and SDK available for deeper integrations."),
    ("Can I use this for internal teams only?", "Absolutely. Many customers use Qefro purely for internal self-service — HR, IT helpdesk, compliance, and engineering knowledge bases."),
    ("Do you offer enterprise pricing?", "Yes. Enterprise plans include unlimited conversations, private deployment, dedicated support, and custom SLAs. SSO/SAML is on the roadmap — talk to sales about your timeline."),
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
        <span class="eyebrow">{ICONS["sparkles"]} AI Customer Support Platform</span>
        <h1>
          <span class="hero-line">AI customer support that answers questions</span>
          <span class="hero-accent">and securely takes action.</span>
        </h1>
        <p class="hero-sub">Train AI on your documentation. Connect your existing APIs. Deploy to your website or WhatsApp. Deliver accurate answers and secure business actions — without replacing your authentication system.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="#demo">{ICONS["play"]} Watch Demo</a>
        </div>
        <div class="hero-checks">
          <span>{ICONS["check"]} Knowledge + Integrations + AI</span>
          <span>{ICONS["check"]} Free forever · no credit card</span>
          <span>{ICONS["check"]} Setup in minutes</span>
          <span>{ICONS["check"]} Your auth stays yours</span>
        </div>
        <div class="pipeline pipeline-flow" role="list" aria-label="How Qefro turns knowledge into answers and actions">
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">01</span>
            <span class="pipeline-v">Knowledge</span>
            <span class="pipeline-d">Docs, FAQs &amp; site crawl</span>
          </div>
          <span class="pipeline-arrow" aria-hidden="true">{ICONS["chevr"]}</span>
          <div class="pipeline-node pipeline-node-accent" role="listitem">
            <span class="pipeline-k">02</span>
            <span class="pipeline-v">Qefro AI</span>
            <span class="pipeline-d">Grounded reasoning</span>
          </div>
          <span class="pipeline-arrow" aria-hidden="true">{ICONS["chevr"]}</span>
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">03</span>
            <span class="pipeline-v">Integrations</span>
            <span class="pipeline-d">Business Tools &amp; OpenAPI</span>
          </div>
          <span class="pipeline-arrow" aria-hidden="true">{ICONS["chevr"]}</span>
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">04</span>
            <span class="pipeline-v">Your APIs</span>
            <span class="pipeline-d">Orders, bookings, tickets</span>
          </div>
          <span class="pipeline-arrow" aria-hidden="true">{ICONS["chevr"]}</span>
          <div class="pipeline-node" role="listitem">
            <span class="pipeline-k">05</span>
            <span class="pipeline-v">Answer</span>
            <span class="pipeline-d">Accurate · actionable</span>
          </div>
        </div>
      </div>
    </section>

    <section class="section-facts" aria-label="Why Qefro">
      <div class="wrap-5xl">
        <p class="facts-label">Why teams choose Qefro over a chatbot</p>
        <div class="facts-grid">
          <div class="fact"><div class="fact-v">Knowledge</div><div class="fact-k">Answers grounded in your docs</div></div>
          <div class="fact"><div class="fact-v">Integrations</div><div class="fact-k">Securely calls your APIs</div></div>
          <div class="fact"><div class="fact-v">Channels</div><div class="fact-k">Website, WhatsApp &amp; voice</div></div>
          <div class="fact"><div class="fact-v">Your auth</div><div class="fact-k">Identify users — we never store passwords</div></div>
        </div>
      </div>
    </section>

    <section class="section" id="more-than-chatbot">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} More than a chatbot</span>
          <h2>Support that retrieves live data and gets work done</h2>
          <p>FAQ chatbots stop at documents. Qefro connects knowledge to the systems your customers already use.</p>
        </div>
        <div class="scenario-grid reveal">
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Where is my order?</p>
            <div class="scenario-flow"><span>AI calls Order API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Returns live tracking</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Book an appointment</p>
            <div class="scenario-flow"><span>AI calls Booking API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Appointment confirmed</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> Create a support ticket</p>
            <div class="scenario-flow"><span>AI calls Helpdesk API</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Ticket created</span></div>
          </article>
          <article class="scenario-card">
            <p class="scenario-ask"><span>Customer</span> What is your refund policy?</p>
            <div class="scenario-flow"><span>AI retrieves documentation</span><span class="scenario-arrow" aria-hidden="true">↓</span><span>Grounded answer with citations</span></div>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="integrations">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["server"]} Integrations</span>
          <h2>Connect your existing business systems</h2>
          <p>Import OpenAPI or configure REST tools. Encrypted credentials, secure execution, logs, and end-user identity forwarding — MCP on the roadmap.</p>
        </div>
        <div class="cap-panel reveal">
          <div class="cap-grid">
            <div class="cap-card"><div class="cap-icon">{ICONS["globe"]}</div><span>REST APIs</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["file"]}</div><span>OpenAPI import</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["shield"]}</div><span>Secure execution</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["lock"]}</div><span>Encrypted credentials</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["chart"]}</div><span>Execution logs</span></div>
            <div class="cap-card"><div class="cap-icon">{ICONS["bot"]}</div><span>End-user identity forwarding</span></div>
          </div>
          <p class="integrations-note">Coming soon: MCP connectors for even broader tool ecosystems.</p>
        </div>
      </div>
    </section>

{product_screenshots_html()}
    <section class="section" id="platform">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Outcomes</span>
          <h2>Everything you need to run AI support</h2>
          <p>Organized around results — not a feature dump.</p>
        </div>
        <div class="outcome-grid reveal">
          <article class="outcome-card">
            <h3>Knowledge</h3>
            <ul>
              <li>Upload PDFs</li>
              <li>Website crawler</li>
              <li>Markdown &amp; FAQs</li>
              <li>Source citations</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Business Integrations</h3>
            <ul>
              <li>REST APIs</li>
              <li>OpenAPI</li>
              <li>Business Tools</li>
              <li>Execution logs</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Channels</h3>
            <ul>
              <li>Website widget</li>
              <li>WhatsApp</li>
              <li>Voice</li>
              <li>API access</li>
            </ul>
          </article>
          <article class="outcome-card">
            <h3>Administration</h3>
            <ul>
              <li>Analytics</li>
              <li>Billing</li>
              <li>Teams &amp; roles</li>
              <li>Workspaces</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="how-it-works">
      <div class="wrap-5xl">
        <div class="section-head reveal">
          <span class="badge badge-purple">{ICONS["check"]} Developer experience</span>
          <h2>No infrastructure. No RAG setup. No LLM hosting.</h2>
          <p>Upload knowledge. Connect APIs. Deploy. We handle vectors, models, and scaling.</p>
        </div>
        <div class="steps-grid reveal">
          <article class="step">
            <div class="step-num-wrap"><div class="step-num-inner">01</div></div>
            <h3>Upload knowledge</h3>
            <p>Documents, policies, PDFs, or crawl your site. Indexed automatically.</p>
          </article>
          <article class="step">
            <div class="step-num-wrap"><div class="step-num-inner">02</div></div>
            <h3>Connect APIs</h3>
            <p>Import OpenAPI or add REST tools with encrypted secrets and identity forwarding.</p>
          </article>
          <article class="step">
            <div class="step-num-wrap"><div class="step-num-inner">03</div></div>
            <h3>Deploy</h3>
            <p>Drop the widget on your site or connect WhatsApp. Live in minutes.</p>
          </article>
        </div>
      </div>
    </section>

    <section class="section" id="developers">
      <div class="wrap">
        <div class="dev-split reveal">
          <div class="dev-copy">
            <span class="badge badge-blue">{ICONS["bot"]} Authenticated users</span>
            <h2>Integrate signed-in customers in minutes</h2>
            <p>Qefro is not an identity provider. Your app owns login and JWTs. Forward identity to Business Tools with <code>identify()</code> — passwords never touch Qefro.</p>
          </div>
          <pre class="code-panel" tabindex="0"><code>const widget = new Widget({{
  token: "..."
}});

widget.identify({{
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
          <span class="badge badge-indigo">{ICONS["zap"]} Comparison</span>
          <h2>Traditional chatbot vs Qefro</h2>
          <p>Why not another FAQ bot? Because support needs live data and safe actions — not just canned replies.</p>
        </div>
        <div class="approach-compare reveal">
          <article class="approach-card">
            <h3>Traditional chatbot</h3>
            <ul>
              <li>Answers FAQs</li>
              <li class="muted">Stops at documents</li>
              <li class="muted">No live order or booking data</li>
              <li class="muted">Cannot complete support actions</li>
            </ul>
          </article>
          <article class="approach-card approach-card-featured">
            <h3>Qefro</h3>
            <ul>
              <li>Answers FAQs</li>
              <li>Retrieves live business data</li>
              <li>Performs customer support actions</li>
              <li>Uses your existing authentication</li>
              <li>Multilingual AI</li>
              <li>Grounded responses with citations</li>
            </ul>
          </article>
        </div>
        <div class="compare reveal" style="margin-top:3rem">
          <div class="compare-q">
            <span class="compare-q-label">When the answer is only in your docs</span>
            <p>&ldquo;Can I still get a refund after 45 days?&rdquo;</p>
          </div>
          <div class="compare-cols">
            <article class="compare-card compare-bad">
              <span class="compare-tag compare-tag-bad">{ICONS["x"]} Guessing chatbot</span>
              <p class="compare-answer">&ldquo;Absolutely! Full refunds within 60 days.&rdquo;</p>
              <p class="compare-note">{ICONS["x"]} Invents a policy — confident and wrong.</p>
            </article>
            <article class="compare-card compare-good">
              <span class="compare-tag compare-tag-good">{ICONS["check"]} Qefro</span>
              <p class="compare-answer">&ldquo;Our refund window is 30 days, so that order isn&rsquo;t eligible. I can open a ticket if you want.&rdquo;</p>
              <p class="compare-source">{ICONS["file"]} Docs + optional Helpdesk API action</p>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section class="section" id="security">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-green">{ICONS["shield"]} Security</span>
          <h2>Enterprise-grade security</h2>
          <p>Customer authentication stays with your application. Qefro never stores passwords.</p>
        </div>
        <div class="trust-grid reveal">
          <article class="trust-card"><div class="trust-icon">{ICONS["lock"]}</div><h3>Encrypted secrets</h3><p>API keys and bearer tokens encrypted at rest. HTTPS-only outbound calls.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["shield"]}</div><h3>Tenant &amp; workspace isolation</h3><p>Multi-tenant by design. Data stays separated at database and vector store level.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["file"]}</div><h3>Audit &amp; execution logs</h3><p>Conversation history and Business Tool runs for accountability.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["bot"]}</div><h3>Secure execution</h3><p>SSRF protections, schema validation, and end-user identity forwarding — not shared tenant secrets by default.</p></article>
        </div>
      </div>
    </section>

    <section class="section section-alt" id="vision">
      <div class="wrap-narrow reveal" style="text-align:center">
        <span class="badge badge-indigo">{ICONS["sparkles"]} Product vision</span>
        <h2>Today: accurate answers. Tomorrow: secure workflows.</h2>
        <p class="vision-copy">Today we help you answer customers from your knowledge and take defined actions through your APIs. We&rsquo;re building toward securely automating support workflows — without promising unsupervised autonomous agents.</p>
      </div>
    </section>

    <section class="section" id="use-cases">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-blue">{ICONS["building"]} Use cases</span>
          <h2>Built for how modern businesses work</h2>
          <p>Same platform — purpose-fit for every team.</p>
        </div>
{uc_tabs_html()}
      </div>
    </section>

    <section class="section section-alt" id="demo">
      <div class="wrap">
        <div class="demo-split reveal">
          <div class="demo-copy">
            <span class="badge badge-green">{ICONS["play"]} Live demo</span>
            <h2>Try it right now</h2>
            <p>Open the chat bubble in the corner. Ask about pricing, security, integrations, or how Qefro differs from a chatbot.</p>
            <div class="widget-demo-hint">
              <div class="widget-demo-card">
                <div class="widget-demo-icon">{ICONS["bot"]}</div>
                <div>
                  <strong>Live assistant is active on this page</strong>
                  <p>Every answer is retrieved from Qefro&rsquo;s demo knowledge base.</p>
                </div>
              </div>
              <p class="widget-demo-suggestions">Try: <span>What is Qefro?</span> · <span>How do integrations work?</span> · <span>Is my data secure?</span></p>
            </div>
          </div>
          <div class="demo-chat" aria-hidden="true">
            <div class="chat-mock">
              <div class="chat-mock-head">
                <div class="chat-mock-avatar">{ICONS["bot"]}</div>
                <div><strong>Qefro Assistant</strong><span>Knowledge + business actions</span></div>
              </div>
              <div class="chat-mock-body">
                <div class="chat-bubble ai">Hi! I can answer from Qefro docs and explain how Business Tools connect to your APIs.</div>
                <div class="chat-bubble user">How is Qefro different from a chatbot?</div>
                <div class="chat-bubble ai">Qefro grounds answers in your knowledge and can securely call your REST APIs for live data and support actions — while your app keeps ownership of authentication.</div>
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

    <section class="section" id="trust-band">
      <div class="wrap-5xl reveal">
        <div class="trust-band">
          <span>Built for businesses</span>
          <span>Multi-tenant</span>
          <span>Secure</span>
          <span>Reliable</span>
          <span>Fast</span>
          <span>Multilingual</span>
        </div>
      </div>
    </section>

    <section class="section" id="pricing">
      <div class="wrap">
        <div class="section-head reveal">
          <span class="badge badge-indigo">{ICONS["zap"]} Pricing</span>
          <h2>Plans that scale with your support team</h2>
          <p>Freemium — Free forever. Save ~26% with yearly billing — Starter from $29/mo, Growth from $99/mo.</p>
        </div>
        <div class="direct-answer reveal">
          <p>Qefro has a <strong>Free plan</strong> (100 conversations/month, 5 documents, 1 Business Tool), then <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly), and custom Enterprise plans.</p>
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
              <li>{ICONS["check"]} 5 documents</li>
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
            <p class="price-desc">For teams that need more power</p>
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
            <p class="price-desc">For organisations with advanced needs</p>
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
            <a class="btn btn-plan" href="/contact">Book a Demo</a>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-alt">
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
        <h2>Deploy an AI customer support platform that answers accurately and securely interacts with your business systems.</h2>
        <p>Start on the free tier — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Talk to Sales</a>
        </div>
      </div>
    </section>
"""


PAGES["index.html"] = page(
    title="Qefro — AI Customer Support Platform",
    description=(
        "AI customer support that answers from your knowledge and securely takes action "
        "in your business systems. Website widget, WhatsApp, REST/OpenAPI integrations. "
        "Start free — no credit card."
    ),
    path="",
    jsonld=[ORG_JSON, WEBSITE_JSON, SOFTWARE_JSON],
    body=home_body(),
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
        <h2>Ready to deploy AI customer support?</h2>
        <p>Start free — no credit card required.</p>
        <div class="hero-actions">
          <a class="btn btn-primary btn-lg" href="{PORTAL_SIGNUP}">Start Free {ICONS["arrow"]}</a>
          <a class="btn btn-ghost btn-lg" href="/contact">Book a Demo</a>
        </div>
      </div>
    </section>
""",
    )


PAGES["features.html"] = inner(
    "Qefro features — AI customer support platform",
    "Features",
    "Qefro AI customer support platform: knowledge (PDFs, crawler, FAQs), business integrations (REST, OpenAPI), channels (widget, WhatsApp, voice), and admin (analytics, teams, billing).",
    "features.html",
    "features.html",
    "<p>Qefro combines <strong>knowledge</strong>, <strong>business integrations</strong>, and <strong>AI</strong> so support can answer accurately and take secure actions — not just reply to FAQs.</p>",
    f"""        <div class="outcome-grid">
          <article class="outcome-card"><h3>Knowledge</h3><ul><li>Upload PDFs</li><li>Website crawler</li><li>Markdown &amp; FAQs</li><li>Source citations</li></ul></article>
          <article class="outcome-card"><h3>Business Integrations</h3><ul><li>REST APIs</li><li>OpenAPI import</li><li>Business Tools</li><li>Execution logs</li></ul></article>
          <article class="outcome-card"><h3>Channels</h3><ul><li>Website widget</li><li>WhatsApp</li><li>Voice</li><li>API access</li></ul></article>
          <article class="outcome-card"><h3>Administration</h3><ul><li>Analytics</li><li>Billing</li><li>Teams &amp; roles</li><li>Workspaces</li></ul></article>
        </div>""",
)

PAGES["how-it-works.html"] = inner(
    "How Qefro works — knowledge, integrations, deploy",
    "How it Works",
    "How Qefro works: upload knowledge, connect your business APIs, deploy to website or WhatsApp — no RAG infrastructure or LLM hosting required.",
    "how-it-works.html",
    "how-it-works.html",
    "<p>No infrastructure. No RAG setup. No vector database. No LLM hosting. Upload knowledge, connect APIs, deploy.</p>",
    f"""        <div class="steps-grid">
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">01</div></div><h3>Upload knowledge</h3><p>Documents, policies, PDFs, or crawl your site. Indexed automatically for grounded answers.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">02</div></div><h3>Connect APIs</h3><p>Import OpenAPI or add REST Business Tools with encrypted secrets and end-user identity forwarding.</p></article>
          <article class="step"><div class="step-num-wrap"><div class="step-num-inner">03</div></div><h3>Deploy</h3><p>Embed the website widget or connect WhatsApp. Identify signed-in users with a few lines of JavaScript.</p></article>
        </div>""",
)

PAGES["use-cases.html"] = inner(
    "Qefro use cases — AI customer support, HR, IT, engineering",
    "Use Cases",
    "See how teams use Qefro for AI customer support, employee onboarding, IT helpdesk, compliance lookup, and engineering runbooks.",
    "use-cases.html",
    "use-cases.html",
    "<p>Teams use Qefro to answer from approved knowledge and — when connected — retrieve live business data or complete defined support actions through their APIs.</p>",
    f"""        <div class="uc-grid">
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["building"]}</div><h3>Internal Teams</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Employee onboarding</li><li>{ICONS["chevr"]} HR &amp; policy</li><li>{ICONS["chevr"]} IT helpdesk</li><li>{ICONS["chevr"]} Compliance</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["headphones"]}</div><h3>Customer Support</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Order &amp; tracking lookups</li><li>{ICONS["chevr"]} Refunds &amp; FAQs</li><li>{ICONS["chevr"]} Ticket creation</li><li>{ICONS["chevr"]} Self-service</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["shield"]}</div><h3>Regulated Industries</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Protocols</li><li>{ICONS["chevr"]} Guidelines</li><li>{ICONS["chevr"]} Manuals</li><li>{ICONS["chevr"]} Compliance</li></ul></article>
          <article class="uc-card"><div class="uc-head"><div class="uc-icon">{ICONS["server"]}</div><h3>Engineering</h3></div><ul class="uc-list"><li>{ICONS["chevr"]} Runbooks</li><li>{ICONS["chevr"]} Wikis</li><li>{ICONS["chevr"]} API docs</li><li>{ICONS["chevr"]} Incidents</li></ul></article>
        </div>""",
)

PAGES["security.html"] = inner(
    "Qefro security — enterprise-grade AI customer support",
    "Security",
    "Enterprise-grade security for AI customer support: your app keeps authentication, Qefro never stores passwords, encrypted secrets, HTTPS only, tool execution logs, tenant and workspace isolation.",
    "security.html",
    "security.html",
    "<p>Customer authentication stays with your application. Qefro never stores passwords. Secrets are encrypted, traffic is HTTPS-only, and execution is tenant- and workspace-isolated.</p>",
    f"""        <div class="trust-grid">
          <article class="trust-card"><div class="trust-icon">{ICONS["lock"]}</div><h3>Your auth stays yours</h3><p>Forward JWTs or session ids via identify() — passwords never touch Qefro.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["shield"]}</div><h3>Encrypted secrets</h3><p>API credentials encrypted at rest. HTTPS-only outbound Business Tool calls.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["building"]}</div><h3>Tenant &amp; workspace isolation</h3><p>Multi-tenant by design at database and vector store level.</p></article>
          <article class="trust-card"><div class="trust-icon">{ICONS["file"]}</div><h3>Secure execution &amp; logs</h3><p>Conversation history, Business Tool execution logs, SSRF protections, and schema validation. Platform admin audit trail and SSO are on the Enterprise roadmap.</p></article>
        </div>""",
)

PAGES["pricing.html"] = inner(
    "Qefro pricing — Starter from $29/mo, Growth from $99/mo, Enterprise",
    "Pricing",
    "Qefro pricing: Starter from $29/month billed annually ($39 monthly), Growth from $99/month billed annually ($119 monthly). Free plan forever (100 conversations/month, 5 documents, 1 Business Tool) — no credit card required.",
    "pricing.html",
    "pricing.html",
    "<p>Qefro offers a <strong>Free plan</strong> (100 conversations/month, 5 documents, 1 Business Tool), then <strong>Starter from $29/month billed annually</strong> ($39 monthly), <strong>Growth from $99/month billed annually</strong> ($119 monthly), and <strong>Enterprise with custom pricing</strong>.</p>",
    f"""        <div class="billing-toggle" role="group" aria-label="Billing period">
          <button type="button" data-billing="monthly">Monthly</button>
          <button type="button" data-billing="annual" class="is-active">Yearly <span>Save 26%</span></button>
        </div>
        <div class="price-grid">
          <article class="price-card"><h3>Free</h3><div class="price-amount">$0</div><p class="price-desc">Forever free — no credit card</p><ul class="price-feats"><li>{ICONS["check"]} 100 conversations/month</li><li>{ICONS["check"]} 5 documents</li><li>{ICONS["check"]} 1 Business Tool</li><li>{ICONS["check"]} 2 team members</li><li>{ICONS["check"]} Website widget</li><li>{ICONS["check"]} Community support</li></ul><a class="btn btn-plan" href="{PORTAL_SIGNUP}">Start Free</a></article>
          <article class="price-card"><h3>Starter</h3><div class="price-amount" data-price-annual="$29" data-price-monthly="$39">$29 <span>/month</span></div><p class="price-billed">billed annually · or $39/mo monthly</p><p class="price-desc">For small teams getting started</p><ul class="price-feats"><li>{ICONS["check"]} 1,000 conversations/month</li><li>{ICONS["check"]} 50 documents</li><li>{ICONS["check"]} 5 Business Tools</li><li>{ICONS["check"]} Website widget</li><li>{ICONS["check"]} Email support</li><li>{ICONS["check"]} Custom branding</li></ul><a class="btn btn-plan" href="{PORTAL_SIGNUP}">Get Started</a></article>
          <article class="price-card is-popular"><div class="price-pop">{ICONS["star"]} Most Popular</div><h3>Growth</h3><div class="price-amount" data-price-annual="$99" data-price-monthly="$119">$99 <span>/month</span></div><p class="price-billed">billed annually · or $119/mo monthly</p><p class="price-desc">For teams that need more power</p><ul class="price-feats"><li>{ICONS["check"]} 10,000 conversations/month</li><li>{ICONS["check"]} 500 documents</li><li>{ICONS["check"]} Widget + WhatsApp</li><li>{ICONS["check"]} Unlimited Business Tools</li><li>{ICONS["check"]} Priority support</li><li>{ICONS["check"]} Analytics</li></ul>{PRICE_FAIR_USE_NOTE}<a class="btn btn-primary" href="{PORTAL_SIGNUP}">Get Started</a></article>
          <article class="price-card"><h3>Enterprise</h3><div class="price-amount">Custom</div><p class="price-desc">For advanced security and scale</p><ul class="price-feats"><li>{ICONS["check"]} Unlimited usage options</li><li>{ICONS["check"]} Unlimited Business Tools</li><li>{ICONS["check"]} Private deployment</li><li>{ICONS["check"]} SSO &amp; SAML (roadmap)</li><li>{ICONS["check"]} Dedicated CSM</li><li>{ICONS["check"]} SLA guarantee</li></ul>{PRICE_FAIR_USE_NOTE}<a class="btn btn-plan" href="/contact">Book a Demo</a></article>
        </div>""",
    extra_jsonld=[
        PRICING_OFFERS_JSON,
        faq_schema([("How much does Qefro cost?", "Qefro is freemium: Free plan includes 100 conversations/month, 5 documents, and 1 Business Tool. Starter is $29/month billed annually ($39 monthly) with 5 Business Tools. Growth is $99/month billed annually ($119 monthly) with unlimited Business Tools. Enterprise is custom. No credit card required to start Free.")]),
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
    title="Qefro FAQ — AI customer support, pricing, security, integrations",
    description="FAQ about Qefro AI customer support platform: pricing, accuracy, security, Business Tools integrations, authenticated users, and setup.",
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
              <textarea class="input" name="use_case" rows="4" required placeholder="What should Qefro answer for your customers?"></textarea>
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
        "What is Qefro? — AI Customer Support Platform",
        "What is Qefro?",
        "Qefro is an AI customer support platform. It answers from your knowledge base, securely calls your existing business APIs, and deploys to website and WhatsApp — without replacing your authentication system.",
        "<p>Unlike a traditional chatbot that only answers FAQs, Qefro combines knowledge, business integrations, and AI so support can retrieve live data and perform defined actions — with grounded responses and citations when answering from docs.</p>",
    ),
    (
        "qefro-pricing.html",
        "How much does Qefro cost?",
        "How much does Qefro cost?",
        "Qefro is freemium. Free forever: 100 conversations/month, 5 documents, 1 Business Tool. Starter from $29/month billed annually (5 Business Tools). Growth from $99/month billed annually (unlimited Business Tools). Enterprise is custom. No credit card required.",
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
