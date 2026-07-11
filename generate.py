#!/usr/bin/env python3
"""Generate Qefro static landing pages with shared chrome and SEO/AEO markup."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://qefro-ai.github.io/qefro-landing-website"
ORG = "Qefro"
PORTAL = "https://qefro.com"

NAV = [
    ("features.html", "Features"),
    ("how-it-works.html", "How it works"),
    ("use-cases.html", "Use cases"),
    ("security.html", "Security"),
    ("pricing.html", "Pricing"),
    ("faq.html", "FAQ"),
]


def meta_block(title, description, path, og_type="website"):
    url = f"{SITE}/{path}" if path else SITE + "/"
    canon = url
    return f"""  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="author" content="Qefro" />
  <meta name="theme-color" content="#0c6e6b" />
  <link rel="canonical" href="{canon}" />
  <link rel="alternate" type="text/plain" href="{SITE}/llms.txt" title="LLM-readable summary" />

  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="Qefro" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:image" content="{SITE}/assets/images/og-cover.svg" />
  <meta property="og:locale" content="en_US" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{SITE}/assets/images/og-cover.svg" />

  <meta name="geo.region" content="IN" />
  <meta name="geo.placename" content="Global" />
  <meta name="ICBM" content="0, 0" />

  <link rel="icon" href="assets/images/favicon.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="assets/css/styles.css" />"""


def nav(active=None):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if active == href else ""
        links.append(f'        <a href="{href}"{cur}>{label}</a>')
    return "\n".join(links)


def header(active=None):
    return f"""  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap nav" data-nav>
      <a class="brand" href="index.html" aria-label="Qefro home">
        <span class="brand-mark" aria-hidden="true"></span>
        Qefro
      </a>
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false">
        <span></span>
      </button>
      <nav class="nav-links" aria-label="Primary">
{nav(active)}
      </nav>
      <div class="nav-cta">
        <a class="btn btn-ghost" href="{PORTAL}">Sign in</a>
        <a class="btn btn-primary" href="{PORTAL}">Start free trial</a>
      </div>
    </div>
  </header>"""


def footer():
    return f"""  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div>
        <a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"></span>Qefro</a>
        <p>AI customer support grounded only in your verified knowledge — documents, FAQs, policies, and websites.</p>
      </div>
      <div>
        <h3>Product</h3>
        <ul>
          <li><a href="features.html">Features</a></li>
          <li><a href="pricing.html">Pricing</a></li>
          <li><a href="how-it-works.html">How it works</a></li>
          <li><a href="security.html">Security</a></li>
        </ul>
      </div>
      <div>
        <h3>Answers</h3>
        <ul>
          <li><a href="faq.html">FAQ</a></li>
          <li><a href="use-cases.html">Use cases</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="llms.txt">llms.txt</a></li>
        </ul>
      </div>
      <div>
        <h3>Company</h3>
        <ul>
          <li><a href="mailto:support@qefro.com">support@qefro.com</a></li>
          <li><a href="{PORTAL}">Customer portal</a></li>
          <li><a href="sitemap.xml">Sitemap</a></li>
        </ul>
      </div>
    </div>
    <div class="wrap footer-bottom">
      <span>© <span data-year></span> {ORG}. All rights reserved.</span>
      <span>Built for SEO, AEO, and GEO-friendly discovery.</span>
    </div>
  </footer>
  <script src="assets/js/main.js" defer></script>"""


def page(title, description, path, body, active=None, jsonld=None, og_type="website"):
    schemas = "\n".join(
        f'  <script type="application/ld+json">\n{block}\n  </script>'
        for block in (jsonld or [])
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{meta_block(title, description, path, og_type)}
{schemas}
</head>
<body>
{header(active)}
  <main id="main">
{body}
  </main>
{footer()}
</body>
</html>
"""


ORG_JSON = """{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Qefro",
  "url": "https://qefro.com",
  "logo": "https://qefro-ai.github.io/qefro-landing-website/assets/images/favicon.svg",
  "email": "support@qefro.com",
  "sameAs": ["https://github.com/qefro-ai"]
}"""

SOFTWARE_JSON = """{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Qefro",
  "applicationCategory": "BusinessApplication",
  "operatingSystem": "Web",
  "url": "https://qefro.com",
  "description": "AI customer support and knowledge assistant that answers only from your verified company content.",
  "offers": {
    "@type": "AggregateOffer",
    "lowPrice": "49",
    "priceCurrency": "USD",
    "offerCount": "3"
  }
}"""


def crumbs(items):
    # items: list of (name, href or "")
    lis = []
    for name, href in items:
        if href:
            lis.append(f'<a href="{href}">{name}</a><span aria-hidden="true">/</span>')
        else:
            lis.append(f"<span>{name}</span>")
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + "".join(lis) + "</nav>"


def breadcrumb_json(items):
    elements = []
    for i, (name, href) in enumerate(items, start=1):
        item = f"{SITE}/{href}" if href else SITE + "/"
        if not href and name == "Home":
            item = SITE + "/"
        elements.append(
            f"""    {{
      "@type": "ListItem",
      "position": {i},
      "name": "{name}",
      "item": "{item}"
    }}"""
        )
    return "{\n  \"@context\": \"https://schema.org\",\n  \"@type\": \"BreadcrumbList\",\n  \"itemListElement\": [\n" + ",\n".join(elements) + "\n  ]\n}"


PAGES = {}

PAGES["index.html"] = page(
    title="Qefro — AI support grounded in your knowledge",
    description="Qefro is an AI customer support assistant that answers only from your verified docs, FAQs, policies, and websites. Go live in minutes with a website widget.",
    path="",
    active=None,
    jsonld=[ORG_JSON, SOFTWARE_JSON],
    body=f"""    <section class="hero" aria-label="Qefro hero">
      <div class="hero-visual" role="img" aria-label="Full-bleed visual of the Qefro assistant reading a knowledge base"></div>
      <div class="wrap hero-copy">
        <p class="hero-brand">Qefro</p>
        <h1 class="hero-headline">Answers from your knowledge — never invented.</h1>
        <p class="hero-sub">Give customers and teams instant, source-grounded support from the documents you already trust.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="{PORTAL}">Start free trial</a>
          <a class="btn btn-ghost" href="how-it-works.html">See how it works</a>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="wrap split reveal">
        <div>
          <p class="section-kicker">What is Qefro</p>
          <h2 class="section-title">A support assistant that stays inside your content</h2>
          <div class="direct-answer">
            <p><strong>Qefro</strong> is an AI customer support and knowledge assistant for businesses. It retrieves relevant passages from your verified knowledge base and answers only from that context — so responses stay accurate, citable, and audit-ready.</p>
          </div>
          <p class="section-lead">Upload PDFs, Word docs, Markdown, or crawl your website. Embed one widget. Start deflecting repetitive tickets the same day.</p>
        </div>
        <ol class="steps">
          <li>
            <div>
              <h3>Ingest your knowledge</h3>
              <p>Chunk, embed, and index documents and sites automatically.</p>
            </div>
          </li>
          <li>
            <div>
              <h3>Retrieve with precision</h3>
              <p>Hybrid search finds the passages that actually answer the question.</p>
            </div>
          </li>
          <li>
            <div>
              <h3>Reply with sources</h3>
              <p>If it is not in your content, Qefro says it does not know.</p>
            </div>
          </li>
        </ol>
      </div>
    </section>

    <section class="section">
      <div class="wrap reveal">
        <p class="section-kicker">Why teams choose Qefro</p>
        <h2 class="section-title">Built for trust, not demos</h2>
        <p class="section-lead">Zero-hallucination RAG, tenant isolation, and multi-channel delivery for support and internal helpdesks.</p>
        <ul class="feature-list">
          <li>
            <h3>Zero-hallucination answers</h3>
            <p>Responses are constrained to retrieved context from your knowledge base — no invented policies.</p>
          </li>
          <li>
            <h3>Website widget in minutes</h3>
            <p>Paste one script tag. Works with React, Next.js, WordPress, Shopify, and plain HTML.</p>
          </li>
          <li>
            <h3>Workspaces for public and private knowledge</h3>
            <p>Separate customer-facing help from HR, IT, and engineering runbooks.</p>
          </li>
          <li>
            <h3>Security by default</h3>
            <p>Tenant-isolated storage, encryption, and optional private deployment for Enterprise.</p>
          </li>
        </ul>
        <p style="margin-top:1.5rem"><a class="btn btn-ghost" href="features.html">Explore features</a></p>
      </div>
    </section>

    <section class="section">
      <div class="wrap reveal">
        <p class="section-kicker">Use cases</p>
        <h2 class="section-title">One assistant, many teams</h2>
        <div class="use-grid">
          <article>
            <h3>Customer support</h3>
            <p>Deflect FAQs, refunds, and product questions with answers grounded in your help center.</p>
          </article>
          <article>
            <h3>Internal helpdesk</h3>
            <p>Onboard employees faster with HR, IT, and policy answers from approved SOPs.</p>
          </article>
          <article>
            <h3>Regulated operations</h3>
            <p>Prefer “I don’t know” over unsafe invented guidance in healthcare and compliance contexts.</p>
          </article>
          <article>
            <h3>Engineering knowledge</h3>
            <p>Query runbooks, API docs, and incident playbooks without digging through folders.</p>
          </article>
        </div>
        <p style="margin-top:1.5rem"><a class="btn btn-ghost" href="use-cases.html">See use cases</a></p>
      </div>
    </section>

    <section class="section">
      <div class="wrap reveal">
        <p class="section-kicker">Pricing</p>
        <h2 class="section-title">Simple plans, 14-day trial</h2>
        <div class="direct-answer">
          <p>Qefro pricing starts at <strong>$49/month</strong> for Starter, <strong>$149/month</strong> for Growth, and custom Enterprise plans with private deployment and SSO.</p>
        </div>
        <p><a class="btn btn-primary" href="pricing.html">View pricing</a></p>
      </div>
    </section>

    <section class="section">
      <div class="wrap reveal">
        <div class="cta-band">
          <h2>Ready to ground your support in truth?</h2>
          <p>Start a free 14-day trial — no credit card required — or talk with us about Enterprise.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="{PORTAL}">Start free trial</a>
            <a class="btn btn-ghost" href="contact.html">Talk to sales</a>
          </div>
        </div>
      </div>
    </section>
""",
)

PAGES["features.html"] = page(
    title="Qefro features — RAG support, widget, workspaces",
    description="Explore Qefro features: zero-hallucination RAG, document and website ingestion, workspaces, analytics, website widget, API, and WhatsApp.",
    path="features.html",
    active="features.html",
    jsonld=[
        breadcrumb_json([("Home", "index.html"), ("Features", "features.html")]),
        SOFTWARE_JSON,
    ],
    body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), ("Features", "")])}
      <h1>Features built for grounded support</h1>
      <div class="direct-answer">
        <p>Qefro combines knowledge ingestion, hybrid retrieval, and source-grounded generation so every answer stays inside your approved content.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap prose reveal">
        <h2>What can Qefro do?</h2>
        <ul class="feature-list" style="padding-left:0;list-style:none">
          <li><h3>Zero-hallucination RAG</h3><p>Answers only from retrieved context. Missing facts return a clear “I don’t know.”</p></li>
          <li><h3>Document and website ingestion</h3><p>PDF, Word, Markdown, plain text, and site crawling with automatic chunking and embeddings.</p></li>
          <li><h3>Public and private workspaces</h3><p>Keep customer help separate from internal HR, IT, and engineering knowledge.</p></li>
          <li><h3>Website widget</h3><p>Brandable chat widget with streaming replies and optional voice where enabled.</p></li>
          <li><h3>API and WhatsApp</h3><p>Reach customers on web and messaging channels from Growth and Enterprise plans.</p></li>
          <li><h3>Analytics and knowledge gaps</h3><p>See conversation volume, unanswered questions, and where docs need updates.</p></li>
        </ul>
        <p><a class="btn btn-primary" href="{PORTAL}">Try Qefro free</a></p>
      </div>
    </section>
""",
)

PAGES["how-it-works.html"] = page(
    title="How Qefro works — upload, retrieve, answer",
    description="Learn how Qefro works: upload knowledge, configure your assistant, embed the widget, and deliver source-grounded answers in under five minutes.",
    path="how-it-works.html",
    active="how-it-works.html",
    jsonld=[breadcrumb_json([("Home", "index.html"), ("How it works", "how-it-works.html")])],
    body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), ("How it works", "")])}
      <h1>How Qefro works</h1>
      <div class="direct-answer">
        <p>Qefro indexes your content, retrieves the most relevant passages when someone asks a question, and generates an answer using only that context.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
        <ol class="steps">
          <li><div><h3>Create your account</h3><p>Start a 14-day free trial at qefro.com. No credit card required.</p></div></li>
          <li><div><h3>Create a workspace</h3><p>Use Public for the website widget or Private for internal assistants.</p></div></li>
          <li><div><h3>Upload knowledge</h3><p>Add documents or crawl websites. Qefro chunks, embeds, and indexes automatically.</p></div></li>
          <li><div><h3>Embed the widget</h3><p>Copy one script tag from Settings → Widget and paste it before your site’s closing body tag.</p></div></li>
          <li><div><h3>Answer with sources</h3><p>Every reply stays grounded in your content with an audit trail.</p></div></li>
        </ol>
        <p style="margin-top:2rem"><a class="btn btn-primary" href="{PORTAL}">Start free trial</a>
        <a class="btn btn-ghost" href="faq.html">Read FAQ</a></p>
      </div>
    </section>
""",
)

PAGES["use-cases.html"] = page(
    title="Qefro use cases — support, HR, IT, engineering",
    description="See how teams use Qefro for customer support, employee onboarding, IT helpdesk, compliance lookup, and engineering runbooks.",
    path="use-cases.html",
    active="use-cases.html",
    jsonld=[breadcrumb_json([("Home", "index.html"), ("Use cases", "use-cases.html")])],
    body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), ("Use cases", "")])}
      <h1>Use cases</h1>
      <div class="direct-answer">
        <p>Teams use Qefro to answer repetitive questions for customers and employees using only approved company knowledge.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap use-grid reveal">
        <article>
          <h3>Customer support</h3>
          <p>Handle order status, refunds, shipping, and product FAQs 24/7 without growing headcount overnight.</p>
        </article>
        <article>
          <h3>HR and people ops</h3>
          <p>Answer leave policy, benefits, and onboarding questions from the latest handbook.</p>
        </article>
        <article>
          <h3>IT helpdesk</h3>
          <p>Guide employees through VPN, device, and access procedures with runbook-backed replies.</p>
        </article>
        <article>
          <h3>Engineering</h3>
          <p>Surface API docs, incident playbooks, and wiki pages inside chat for faster resolution.</p>
        </article>
        <article>
          <h3>Healthcare operations</h3>
          <p>Keep staff protocols grounded in approved manuals — refuse to invent clinical guidance.</p>
        </article>
        <article>
          <h3>E-commerce</h3>
          <p>Reduce ticket volume with instant, policy-accurate answers on your storefront.</p>
        </article>
      </div>
    </section>
""",
)

PAGES["security.html"] = page(
    title="Qefro security — tenant isolation, encryption, private deploy",
    description="Qefro keeps your data yours: tenant-isolated storage, encryption in transit and at rest, no training on your content, and private deployment options.",
    path="security.html",
    active="security.html",
    jsonld=[breadcrumb_json([("Home", "index.html"), ("Security", "security.html")])],
    body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), ("Security", "")])}
      <h1>Security and privacy</h1>
      <div class="direct-answer">
        <p>Qefro never uses your data to train AI models. Content stays tenant-isolated, encrypted, and exportable — with private or on-premise deployment available on Enterprise.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap trust-strip reveal">
        <article>
          <h3>Data ownership</h3>
          <p>Your content stays yours. Export or delete anytime.</p>
        </article>
        <article>
          <h3>Tenant isolation</h3>
          <p>Database and vector storage separated per organisation.</p>
        </article>
        <article>
          <h3>Encryption</h3>
          <p>Protected in transit and at rest across the stack.</p>
        </article>
        <article>
          <h3>Enterprise controls</h3>
          <p>SSO/SAML, audit logs, RBAC, and private deployment.</p>
        </article>
      </div>
      <div class="wrap prose reveal" style="margin-top:2rem">
        <h2>Is Qefro SOC 2 compatible?</h2>
        <p>Yes. Qefro is designed with SOC 2 compatible controls, role-based access, and conversation audit history suitable for teams that need grounded answers in sensitive environments.</p>
        <p><a class="btn btn-primary" href="contact.html">Ask about Enterprise security</a></p>
      </div>
    </section>
""",
)

PAGES["pricing.html"] = page(
    title="Qefro pricing — Starter $49, Growth $149, Enterprise",
    description="Qefro pricing: Starter $49/month, Growth $149/month, and custom Enterprise plans. 14-day free trial on all plans. No credit card required.",
    path="pricing.html",
    active="pricing.html",
    jsonld=[
        breadcrumb_json([("Home", "index.html"), ("Pricing", "pricing.html")]),
        """{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "How much does Qefro cost?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "Qefro Starter is $49 per month, Growth is $149 per month, and Enterprise is custom pricing. All plans include a 14-day free trial with no credit card required."
    }
  }]
}""",
    ],
    body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), ("Pricing", "")])}
      <h1>Pricing</h1>
      <div class="direct-answer">
        <p>Qefro offers three plans: <strong>Starter at $49/month</strong>, <strong>Growth at $149/month</strong>, and <strong>Enterprise with custom pricing</strong>. Every plan includes a 14-day free trial and no credit card to start.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap price-table reveal">
        <article class="price-plan">
          <h3>Starter</h3>
          <p class="amount">$49 <span>/month</span></p>
          <p class="desc">For small teams getting started</p>
          <ul>
            <li>1,000 conversations/month</li>
            <li>50 documents</li>
            <li>1 assistant</li>
            <li>Website widget</li>
            <li>Email support</li>
          </ul>
          <a class="btn btn-ghost" href="{PORTAL}">Start free trial</a>
        </article>
        <article class="price-plan is-featured">
          <h3>Growth</h3>
          <p class="amount">$149 <span>/month</span></p>
          <p class="desc">Most popular for scaling teams</p>
          <ul>
            <li>10,000 conversations/month</li>
            <li>Unlimited documents</li>
            <li>5 assistants</li>
            <li>Widget + WhatsApp</li>
            <li>Custom branding</li>
            <li>Priority support</li>
            <li>Analytics</li>
          </ul>
          <a class="btn btn-primary" href="{PORTAL}">Start free trial</a>
        </article>
        <article class="price-plan">
          <h3>Enterprise</h3>
          <p class="amount">Custom</p>
          <p class="desc">For advanced security and scale</p>
          <ul>
            <li>Unlimited conversations</li>
            <li>Unlimited documents</li>
            <li>Unlimited assistants</li>
            <li>Private deployment</li>
            <li>SSO &amp; SAML</li>
            <li>Dedicated CSM</li>
            <li>SLA guarantee</li>
          </ul>
          <a class="btn btn-ghost" href="contact.html">Talk to sales</a>
        </article>
      </div>
    </section>
""",
)

FAQ_ITEMS = [
    (
        "What is Qefro?",
        "Qefro is an AI customer support and knowledge assistant that answers questions using only your company’s verified content — documents, FAQs, policies, and websites.",
    ),
    (
        "How much does Qefro cost?",
        "Starter is $49/month, Growth is $149/month, and Enterprise is custom. All plans include a 14-day free trial with no credit card required.",
    ),
    (
        "What content can I upload?",
        "PDFs, Word documents, Markdown, plain text, or crawl entire websites. Qefro processes and indexes them automatically.",
    ),
    (
        "How accurate are the answers?",
        "Qefro responds using your verified content only. It does not fabricate facts. If information is missing, it says so.",
    ),
    (
        "Is my data secure?",
        "Yes. Data is tenant-isolated, encrypted, and never used to train AI models. Private deployment is available on Enterprise.",
    ),
    (
        "How long does integration take?",
        "Most teams are live in under five minutes with one script tag. API and SDK options exist for deeper integrations.",
    ),
    (
        "Can I use Qefro for internal teams only?",
        "Yes. Many customers use private workspaces for HR, IT helpdesk, compliance, and engineering knowledge bases.",
    ),
    (
        "Do you offer enterprise pricing?",
        "Yes. Enterprise includes unlimited usage options, private deployment, SSO, dedicated support, and custom SLAs. Contact sales via qefro.com.",
    ),
]


def faq_json():
    import json

    payload = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in FAQ_ITEMS
        ],
    }
    return json.dumps(payload, indent=2)


faq_html_items = "\n".join(
    f"""        <div class="faq-item">
          <button type="button" aria-expanded="false"><span>{q}</span><span aria-hidden="true">+</span></button>
          <div class="faq-a"><p>{a}</p></div>
        </div>"""
    for q, a in FAQ_ITEMS
)

PAGES["faq.html"] = page(
    title="Qefro FAQ — pricing, security, accuracy, setup",
    description="Frequently asked questions about Qefro: pricing, accuracy, security, integrations, and internal use cases. Clear answers for customers and answer engines.",
    path="faq.html",
    active="faq.html",
    jsonld=[
        breadcrumb_json([("Home", "index.html"), ("FAQ", "faq.html")]),
        faq_json(),
    ],
    body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), ("FAQ", "")])}
      <h1>Frequently asked questions</h1>
      <div class="direct-answer">
        <p>Short, factual answers about what Qefro is, how much it costs, how accurate it is, and how quickly you can go live.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap faq-list reveal">
{faq_html_items}
      </div>
    </section>
""",
)

PAGES["contact.html"] = page(
    title="Contact Qefro — sales and support",
    description="Contact Qefro sales or support. Email support@qefro.com or start a free trial at qefro.com.",
    path="contact.html",
    active=None,
    jsonld=[breadcrumb_json([("Home", "index.html"), ("Contact", "contact.html")])],
    body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), ("Contact", "")])}
      <h1>Contact</h1>
      <div class="direct-answer">
        <p>Email <a href="mailto:support@qefro.com"><strong>support@qefro.com</strong></a> for product help, or talk to sales about Enterprise pricing, SSO, and private deployment.</p>
      </div>
    </section>
    <section class="section">
      <div class="wrap reveal">
        <div class="cta-band">
          <h2>Talk with Qefro</h2>
          <p>Start a trial instantly, or reach the team for a tailored Enterprise quote.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="{PORTAL}">Start free trial</a>
            <a class="btn btn-ghost" href="mailto:support@qefro.com">Email support</a>
          </div>
        </div>
      </div>
    </section>
""",
)

PAGES["404.html"] = page(
    title="Page not found — Qefro",
    description="The page you requested was not found on the Qefro website.",
    path="404.html",
    body=f"""    <section class="page-hero wrap">
      <h1>Page not found</h1>
      <p class="section-lead">That URL is not in our sitemap. Try the homepage or FAQ.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="index.html">Go home</a>
        <a class="btn btn-ghost" href="faq.html">Read FAQ</a>
      </div>
    </section>
""",
)

# Answer-oriented AEO pages
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
        "Qefro Starter costs $49 per month, Growth costs $149 per month, and Enterprise is custom pricing. All plans include a 14-day free trial with no credit card required.",
        '<p>See the full comparison on the <a href="pricing.html">pricing page</a>.</p>',
    ),
]:
    import json

    faq = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
            ],
        },
        indent=2,
    )
    PAGES[slug] = page(
        title=title,
        description=a,
        path=slug,
        jsonld=[breadcrumb_json([("Home", "index.html"), (q, slug)]), faq],
        body=f"""    <section class="page-hero wrap">
      {crumbs([("Home", "index.html"), (q, "")])}
      <h1>{q}</h1>
      <div class="direct-answer"><p>{a}</p></div>
      <div class="prose">{extra}
        <p><a class="btn btn-primary" href="{PORTAL}">Start free trial</a></p>
      </div>
    </section>
""",
    )


def write_all():
    for name, html in PAGES.items():
        (ROOT / name).write_text(html, encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    write_all()
