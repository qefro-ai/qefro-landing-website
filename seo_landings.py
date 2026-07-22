"""Programmatic SEO landing pages for Qefro (topics, industries, features)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Landing:
    slug: str
    kind: str  # topic | industry | feature
    h1: str
    title: str
    description: str
    answer: str
    paragraphs: tuple[str, ...]
    bullets: tuple[str, ...]
    related: tuple[tuple[str, str], ...] = ()
    faqs: tuple[tuple[str, str], ...] = ()
    badge: str = ""


def _t(
    slug: str,
    h1: str,
    title: str,
    description: str,
    answer: str,
    paragraphs: tuple[str, ...],
    bullets: tuple[str, ...],
    related: tuple[tuple[str, str], ...] = (),
    faqs: tuple[tuple[str, str], ...] = (),
) -> Landing:
    return Landing(
        slug=slug,
        kind="topic",
        h1=h1,
        title=title,
        description=description,
        answer=answer,
        paragraphs=paragraphs,
        bullets=bullets,
        related=related,
        faqs=faqs,
        badge="Topic",
    )


def _i(
    slug: str,
    h1: str,
    title: str,
    description: str,
    answer: str,
    paragraphs: tuple[str, ...],
    bullets: tuple[str, ...],
    related: tuple[tuple[str, str], ...] = (),
    faqs: tuple[tuple[str, str], ...] = (),
) -> Landing:
    return Landing(
        slug=slug,
        kind="industry",
        h1=h1,
        title=title,
        description=description,
        answer=answer,
        paragraphs=paragraphs,
        bullets=bullets,
        related=related,
        faqs=faqs,
        badge="Industry",
    )


def _f(
    slug: str,
    h1: str,
    title: str,
    description: str,
    answer: str,
    paragraphs: tuple[str, ...],
    bullets: tuple[str, ...],
    related: tuple[tuple[str, str], ...] = (),
    faqs: tuple[tuple[str, str], ...] = (),
) -> Landing:
    return Landing(
        slug=slug,
        kind="feature",
        h1=h1,
        title=title,
        description=description,
        answer=answer,
        paragraphs=paragraphs,
        bullets=bullets,
        related=related,
        faqs=faqs,
        badge="Feature",
    )


TOPIC_LANDINGS: tuple[Landing, ...] = (
    _t(
        "ai-customer-support",
        "AI Customer Support",
        "AI Customer Support Platform | Qefro",
        "Qefro AI customer support answers from your knowledge base, runs secure business actions, and works on website chat and WhatsApp.",
        "<p><strong>Qefro</strong> is an AI customer support platform that grounds answers in your docs and APIs, then takes secure actions — not just chat replies.</p>",
        (
            "Generic chatbots often invent answers. Qefro retrieves from your verified content, cites sources, and is designed to decline when nothing relevant exists — so support stays accurate.",
            "Beyond Q&A, connect order, billing, and ticketing systems via REST/OpenAPI or the Backend SDK so the assistant can look up live status, create tickets, and hand off to humans with full context.",
            "Deploy Customer AI on your website widget and WhatsApp from one Admin Console, with workspace isolation, RBAC, and encrypted secrets.",
        ),
        (
            "Grounded answers with source citations",
            "Secure business actions through your APIs",
            "Website widget + WhatsApp channels",
            "Human handoff and lead capture",
            "14-day free trial — no credit card",
        ),
        related=(
            ("website-ai-chat", "Website AI chat"),
            ("whatsapp-ai-agent", "WhatsApp AI agent"),
            ("helpdesk-ai", "Helpdesk AI"),
            ("customer-support-automation", "Support automation"),
        ),
        faqs=(
            (
                "How is Qefro different from a basic AI chatbot?",
                "Qefro combines knowledge retrieval with secure business actions, workspace permissions, and channels for both customers and employees — not chat-only demos.",
            ),
            (
                "Can it create tickets or look up orders?",
                "Yes. Connect your helpdesk or order APIs as Business Tools, or use the Backend SDK so actions run with the end-user’s identity.",
            ),
        ),
    ),
    _t(
        "ai-chatbot",
        "AI Chatbot for Business",
        "AI Chatbot for Business | Qefro",
        "Build a business AI chatbot with Qefro: multilingual RAG, citations, WhatsApp, website widget, and secure API actions.",
        "<p>Qefro’s business AI chatbot answers from your company knowledge and can execute approved actions in your systems.</p>",
        (
            "Most chatbot tools stop at conversation. Qefro indexes PDFs, sites, and docs, then answers with citations across languages including English, Arabic, Tamil, and Hindi.",
            "When customers need more than text — order status, refunds, appointment links — Business Tools call your APIs with encrypted credentials or forwarded identity.",
            "One platform covers Customer AI, Employee AI, and an Admin Console so you configure knowledge and permissions once.",
        ),
        (
            "Hybrid retrieval (keyword + vectors)",
            "OCR for scans and image PDFs",
            "Widget JWT auth and streaming replies",
            "Internal Portal for employee chatbots",
            "Refuse when the knowledge base has no answer",
        ),
        related=(
            ("rag-chatbot", "RAG chatbot"),
            ("multilingual-ai-chatbot", "Multilingual chatbot"),
            ("document-chat-ai", "Document chat AI"),
            ("live-chat", "Live chat"),
        ),
    ),
    _t(
        "website-ai-chat",
        "Website AI Chat",
        "Website AI Chat Widget | Qefro",
        "Add website AI chat with Qefro’s embeddable widget — grounded answers, voice options, lead capture, and secure business actions.",
        "<p>Embed Qefro’s website AI chat widget to answer visitors from your knowledge base and trigger secure actions on your stack.</p>",
        (
            "Install with a short script and widget token. Messages stream over WebSocket, stay size-bounded, and can scrub PII before model calls.",
            "Visitors get answers grounded in your site crawl and uploaded docs. When they need a human, hand off to your team inbox with conversation context.",
            "Optional voice STT/TTS in the widget helps mobile and accessibility use cases without a separate product.",
        ),
        (
            "One-line embed for your site",
            "Crawl your public site into the knowledge base",
            "Lead capture forms in-chat",
            "Brand colors and welcome message",
            "Works with identify() for signed-in users",
        ),
        related=(
            ("ai-customer-support", "AI customer support"),
            ("website-crawl", "Website crawl"),
            ("voice-ai", "Voice AI"),
            ("live-chat", "Live chat"),
        ),
    ),
    _t(
        "whatsapp-ai-agent",
        "WhatsApp AI Agent",
        "WhatsApp AI Agent for Business | Qefro",
        "Run a WhatsApp AI agent with Qefro — same knowledge and business actions as your website chat, with Starter+ WhatsApp support.",
        "<p>Qefro’s WhatsApp AI agent uses the same workspaces, knowledge, and Business Tools as your website assistant.</p>",
        (
            "Customers already live in WhatsApp. Connect the channel once in the Admin Console so policies, FAQs, and API actions stay consistent with web chat.",
            "Identity-aware actions let authenticated flows look up accounts or create tickets without storing end-user passwords in Qefro.",
            "Available on Starter and above so growing teams can add messaging without rebuilding RAG infrastructure.",
        ),
        (
            "Shared knowledge with website Customer AI",
            "Business actions via REST/OpenAPI or SDK",
            "Handoff path to human agents",
            "Workspace-scoped instructions and tools",
            "Audit-friendly execution logs",
        ),
        related=(
            ("ai-customer-support", "AI customer support"),
            ("whatsapp-ai", "WhatsApp AI feature"),
            ("customer-support-automation", "Support automation"),
        ),
    ),
    _t(
        "multilingual-ai-chatbot",
        "Multilingual AI Chatbot",
        "Multilingual AI Chatbot | Qefro",
        "Multilingual AI chatbot with Qefro RAG — English, Arabic, Tamil, Hindi and more, with OCR and source citations.",
        "<p>Qefro’s multilingual AI chatbot retrieves and answers across languages using hybrid search, OCR, and citations.</p>",
        (
            "Global teams need support that matches the customer’s language without separate bots per locale. Qefro indexes mixed-language corpora in isolated workspaces.",
            "OCR helps scanned PDFs and image-heavy manuals stay searchable. Hybrid BM25 + vector retrieval improves recall for short queries and proper nouns.",
            "Refusal behavior reduces hallucinations when the corpus has no matching content — critical for regulated copy in every language.",
        ),
        (
            "EN, AR, TA, HI and more",
            "OCR for non-Latin scanned docs",
            "Per-workspace language content",
            "Cited sources in answers",
            "Website and WhatsApp channels",
        ),
        related=(
            ("rag-chatbot", "RAG chatbot"),
            ("document-chat-ai", "Document chat"),
            ("knowledge-base-ai", "Knowledge base AI"),
        ),
    ),
    _t(
        "rag-chatbot",
        "RAG Chatbot",
        "RAG Chatbot Platform | Qefro",
        "Deploy a production RAG chatbot with Qefro — hybrid retrieval, citations, refusal when unsure, and optional API actions.",
        "<p>Qefro is a production RAG chatbot platform: chunk, embed, retrieve, cite — then optionally act through your APIs.</p>",
        (
            "Retrieval-augmented generation only works if retrieval is reliable. Qefro combines dense vectors with full-text search and workspace filters for tenant-safe results.",
            "Every answer can cite source documents. When retrieval is empty or weak, the assistant is designed to say it does not know instead of guessing.",
            "Add Business Tools when chat must change state — refunds, lookups, tickets — with encrypted secrets and execution logs.",
        ),
        (
            "Document + website ingestion",
            "Hybrid BM25 + vector search",
            "Source citations and grounding",
            "Tenant and workspace isolation",
            "Benchmark methodology published",
        ),
        related=(
            ("document-chat-ai", "Document chat AI"),
            ("knowledge-base", "Knowledge base feature"),
            ("benchmark", "Benchmark"),
            ("ai-chatbot", "AI chatbot"),
        ),
        faqs=(
            (
                "Do I host my own vector database?",
                "No. Qefro runs retrieval infrastructure for you. You upload content and configure workspaces in the Admin Console.",
            ),
        ),
    ),
    _t(
        "document-chat-ai",
        "Document Chat AI",
        "Document Chat AI | Ask PDFs with Qefro",
        "Chat with PDFs, DOCX, Markdown, and crawled pages using Qefro document chat AI — citations, OCR, and workspace isolation.",
        "<p>Qefro document chat AI lets teams ask questions over PDFs and docs with citations — and optional actions when APIs are connected.</p>",
        (
            "Upload handbooks, contracts, and product manuals. Qefro chunks and indexes them per workspace so HR content never leaks into a public support bot.",
            "OCR unlocks scanned packets. Employees use the Internal Portal; customers use the website widget against public workspaces only.",
            "Combine document answers with Business Tools when the next step is submitting a form or opening a ticket in your system of record.",
        ),
        (
            "PDF, DOCX, Markdown, TXT",
            "Website crawl into the same index",
            "OCR for image-based PDFs",
            "Cited passages in answers",
            "Private vs public workspaces",
        ),
        related=(
            ("knowledge-base-ai", "Knowledge base AI"),
            ("rag-chatbot", "RAG chatbot"),
            ("internal-ai", "Internal AI"),
        ),
    ),
    _t(
        "customer-support-automation",
        "Customer Support Automation",
        "Customer Support Automation | Qefro",
        "Automate customer support with Qefro — deflection for FAQs, API actions for live data, and human handoff when needed.",
        "<p>Qefro customer support automation deflects routine questions, executes approved API actions, and escalates with context.</p>",
        (
            "Automation fails when it hides humans. Qefro keeps handoff first-class: agents see the thread, sources, and tool runs.",
            "Automate the repetitive layer — shipping status, password reset links via your API, policy quotes — while complex cases reach people faster.",
            "Measure quality with grounded answers and refusal behavior instead of vanity “messages answered” metrics alone.",
        ),
        (
            "FAQ and policy deflection",
            "Live data via Business Tools",
            "Inbox handoff for agents",
            "Lead capture for sales-assist flows",
            "Analytics on conversations",
        ),
        related=(
            ("ai-customer-support", "AI customer support"),
            ("helpdesk-ai", "Helpdesk AI"),
            ("team-inbox", "Team inbox"),
            ("analytics", "Analytics"),
        ),
    ),
    _t(
        "helpdesk-ai",
        "Helpdesk AI",
        "Helpdesk AI Software | Qefro",
        "Helpdesk AI with Qefro: grounded answers, ticket creation via your APIs, Internal Portal for agents, and audit-friendly logs.",
        "<p>Use Qefro as helpdesk AI that answers from docs and creates tickets in your existing helpdesk through secure integrations.</p>",
        (
            "Qefro does not replace your CRM or ticketing system of record. It sits in front with knowledge and actions that call your APIs.",
            "Agents and employees can use the Internal Portal for runbooks while customers use the widget — same Admin Console configuration.",
            "Execution logs show which tools ran, supporting QA and compliance reviews.",
        ),
        (
            "Create tickets via OpenAPI/REST",
            "Runbook and SOP retrieval",
            "Employee + customer surfaces",
            "RBAC and workspace isolation",
            "Encrypted integration secrets",
        ),
        related=(
            ("customer-support-automation", "Support automation"),
            ("integrations", "Integrations"),
            ("audit-logs", "Audit logs"),
            ("team-inbox", "Team inbox"),
        ),
    ),
    _t(
        "knowledge-base-ai",
        "Knowledge Base AI",
        "Knowledge Base AI | Qefro",
        "Turn your knowledge base into AI answers with Qefro — uploads, site crawl, multilingual RAG, citations, and workspace isolation.",
        "<p>Qefro knowledge base AI turns documents and crawled pages into grounded conversational answers with citations.</p>",
        (
            "Static FAQ pages go stale. Keep a living knowledge base in workspaces and let Customer AI and Employee AI share the same indexed content with different visibility.",
            "Hybrid retrieval helps both exact policy IDs and natural-language questions. OCR covers legacy scans.",
            "When content is missing, refusal beats a wrong answer — especially for legal, medical, or financial copy.",
        ),
        (
            "Upload and crawl into one index",
            "Per-workspace knowledge isolation",
            "Multilingual retrieval",
            "Source citations",
            "Admin Console governance",
        ),
        related=(
            ("knowledge-base", "Knowledge base feature"),
            ("document-chat-ai", "Document chat"),
            ("website-crawl", "Website crawl"),
            ("rag-chatbot", "RAG chatbot"),
        ),
    ),
)


INDUSTRY_LANDINGS: tuple[Landing, ...] = (
    _i(
        "ai-for-hospitals",
        "AI for Hospitals",
        "AI for Hospitals | Internal & Patient Support | Qefro",
        "AI for hospitals with Qefro: protocol lookup for staff, patient-facing FAQs with citations, tenant isolation, and secure API actions.",
        "<p>Hospitals use Qefro for staff protocol lookup and carefully scoped patient FAQs — with isolation, citations, and optional secure actions.</p>",
        (
            "Clinical and operational teams need fast access to protocols without chatting across department boundaries. Workspaces keep nursing, IT, and HR knowledge separated.",
            "Patient-facing bots should stick to approved public content and refuse medical advice outside the knowledge base. Qefro’s grounding and refusal design support that posture.",
            "Enterprise options include private deployment discussions for organizations with stricter hosting requirements.",
        ),
        (
            "Workspace isolation for departments",
            "Cited answers from approved docs",
            "PII scrubbing on model calls",
            "Audit and execution logs",
            "Private deployment conversations for Enterprise",
        ),
        related=(
            ("internal-ai", "Internal AI"),
            ("knowledge-base-ai", "Knowledge base AI"),
            ("security", "Security"),
            ("ai-for-schools", "AI for schools"),
        ),
        faqs=(
            (
                "Is Qefro a clinical decision system?",
                "No. Qefro retrieves and acts on content and APIs you configure. It is not a diagnostic device and should only use approved knowledge.",
            ),
        ),
    ),
    _i(
        "ai-for-hotels",
        "AI for Hotels",
        "AI for Hotels | Guest & Staff Assistants | Qefro",
        "AI for hotels: guest website and WhatsApp answers, staff Internal Portal for SOPs, and booking or PMS actions via your APIs.",
        "<p>Hotels use Qefro for guest FAQs on web and WhatsApp plus staff SOP assistants — with optional PMS or booking API actions.</p>",
        (
            "Guests ask about amenities, check-in, and local tips. Ground answers in your property content and escalate edge cases to the front desk with handoff.",
            "Staff use the Internal Portal for housekeeping and security SOPs without exposing those docs on the public widget.",
            "Connect booking or loyalty APIs as Business Tools when you want the assistant to fetch reservation status securely.",
        ),
        (
            "Multilingual guest support",
            "WhatsApp for travelers",
            "Staff-only workspaces",
            "API actions for live reservation data",
            "Brandable widget",
        ),
        related=(
            ("whatsapp-ai-agent", "WhatsApp AI agent"),
            ("website-ai-chat", "Website AI chat"),
            ("ai-for-travel", "AI for travel"),
            ("multilingual-ai-chatbot", "Multilingual chatbot"),
        ),
    ),
    _i(
        "ai-for-schools",
        "AI for Schools",
        "AI for Schools & Universities | Qefro",
        "AI for schools: student and parent FAQs, staff policy portals, multilingual RAG, and integrations with your SIS or ticketing APIs.",
        "<p>Schools and universities use Qefro for admissions FAQs, campus services, and staff policy assistants with workspace isolation.</p>",
        (
            "Parents and students need consistent answers about calendars, fees, and procedures. Keep public content in a public workspace and internal HR in a private one.",
            "Multilingual retrieval helps diverse communities. OCR covers scanned circulars and handwritten-adjacent scans when digitized.",
            "Ticket creation via your helpdesk API keeps IT and registrar workflows in systems you already trust.",
        ),
        (
            "Admissions and campus FAQ bots",
            "Staff Internal Portal",
            "Multilingual knowledge",
            "Helpdesk API actions",
            "Role-based access",
        ),
        related=(
            ("internal-ai", "Internal AI"),
            ("multilingual-ai-chatbot", "Multilingual chatbot"),
            ("helpdesk-ai", "Helpdesk AI"),
            ("document-chat-ai", "Document chat"),
        ),
    ),
    _i(
        "ai-for-saas",
        "AI for SaaS",
        "AI for SaaS Companies | Qefro",
        "AI for SaaS: in-app or website support, docs RAG, identify() for logged-in users, and product API actions for account tasks.",
        "<p>SaaS teams use Qefro to turn product docs into support AI — with identity-aware actions for signed-in customers.</p>",
        (
            "Deflect “how do I…” tickets with cited docs, then use identify() so billing or workspace actions run as the real user against your APIs.",
            "Employee AI helps CS and success teams search runbooks while Customer AI stays on public and authenticated experiences you choose.",
            "OpenAPI import speeds connecting your existing customer-facing APIs as Business Tools.",
        ),
        (
            "Docs + changelog ingestion",
            "identify() for authenticated chat",
            "OpenAPI Business Tools",
            "In-app or marketing-site widget",
            "Growth plan WhatsApp option",
        ),
        related=(
            ("ai-customer-support", "AI customer support"),
            ("api", "API"),
            ("integrations", "Integrations"),
            ("rag-chatbot", "RAG chatbot"),
        ),
    ),
    _i(
        "ai-for-ecommerce",
        "AI for Ecommerce",
        "AI for Ecommerce | Orders, Policies & Chat | Qefro",
        "AI for ecommerce: policy answers with citations, order tracking via your APIs, website and WhatsApp chat, and human handoff.",
        "<p>Ecommerce brands use Qefro for policy Q&A, order lookups through your APIs, and WhatsApp or website chat with handoff.</p>",
        (
            "Shoppers ask about shipping, returns, and sizing. Ground answers in your policies and product content; refuse when SKU data is not in the knowledge base.",
            "Connect order and subscription APIs so “where is my order?” returns live tracking instead of a generic script.",
            "Handoff preserves cart and conversation context for agents during peak seasons.",
        ),
        (
            "Returns and shipping policy RAG",
            "Order API business actions",
            "WhatsApp for post-purchase support",
            "Lead capture for abandoned-cart assists",
            "Workspace separation for brands",
        ),
        related=(
            ("whatsapp-ai-agent", "WhatsApp AI agent"),
            ("customer-support-automation", "Support automation"),
            ("website-ai-chat", "Website AI chat"),
            ("integrations", "Integrations"),
        ),
    ),
    _i(
        "ai-for-manufacturing",
        "AI for Manufacturing",
        "AI for Manufacturing | SOPs & Ops AI | Qefro",
        "AI for manufacturing: SOP and safety doc chat for operators, engineering runbooks, OCR for manuals, and optional MES/ticket APIs.",
        "<p>Manufacturers use Qefro so operators and engineers can query SOPs and runbooks with citations — plus optional plant system actions.</p>",
        (
            "Paper manuals and PDF equipment packs are hard to search on the floor. OCR and document chat make procedures findable in the Internal Portal.",
            "Keep safety-critical content in controlled workspaces with RBAC. Public marketing chat stays separate from plant knowledge.",
            "Integrate ticketing or maintenance APIs when the assistant should open work orders instead of only quoting a PDF.",
        ),
        (
            "SOP and safety document RAG",
            "OCR for equipment manuals",
            "Operator Internal Portal",
            "Maintenance ticket actions",
            "Audit-friendly logs",
        ),
        related=(
            ("document-chat-ai", "Document chat"),
            ("internal-ai", "Internal AI"),
            ("knowledge-base-ai", "Knowledge base AI"),
            ("audit-logs", "Audit logs"),
        ),
    ),
    _i(
        "ai-for-real-estate",
        "AI for Real Estate",
        "AI for Real Estate | Listing & Client AI | Qefro",
        "AI for real estate: listing and brochure chat, agent Internal Portal, lead capture, and CRM actions via your APIs.",
        "<p>Real estate teams use Qefro to answer listing questions, capture leads, and assist agents with internal playbooks.</p>",
        (
            "Buyers ask about amenities, fees, and availability. Ground public answers in listing packs and site content; push hot leads into your CRM through Business Tools.",
            "Agents use Employee AI for compliance scripts and transaction checklists without exposing them on the public widget.",
            "Multilingual chat helps cross-border and diaspora buyers engage in their preferred language.",
        ),
        (
            "Listing and brochure RAG",
            "Website lead capture",
            "CRM/API follow-ups",
            "Agent Internal Portal",
            "Multilingual support",
        ),
        related=(
            ("website-ai-chat", "Website AI chat"),
            ("multilingual-ai-chatbot", "Multilingual chatbot"),
            ("live-chat", "Live chat"),
            ("integrations", "Integrations"),
        ),
    ),
    _i(
        "ai-for-travel",
        "AI for Travel",
        "AI for Travel & Tourism | Qefro",
        "AI for travel: itinerary and policy FAQs, WhatsApp traveler support, multilingual RAG, and booking system actions via APIs.",
        "<p>Travel companies use Qefro for traveler FAQs on web and WhatsApp, with optional booking API lookups and multilingual RAG.</p>",
        (
            "Travelers message at odd hours about visas, baggage, and changes. Keep answers cited from your published policies and escalate exceptions to humans.",
            "WhatsApp reaches travelers on the move. Share the same knowledge as your website assistant for consistency.",
            "Connect booking engines as Business Tools when you want authenticated itinerary status without building a custom RAG stack.",
        ),
        (
            "Policy and itinerary FAQs",
            "WhatsApp traveler support",
            "Multilingual retrieval",
            "Booking API actions",
            "Human handoff",
        ),
        related=(
            ("ai-for-hotels", "AI for hotels"),
            ("whatsapp-ai-agent", "WhatsApp AI agent"),
            ("multilingual-ai-chatbot", "Multilingual chatbot"),
            ("ai-customer-support", "AI customer support"),
        ),
    ),
)


FEATURE_LANDINGS: tuple[Landing, ...] = (
    _f(
        "live-chat",
        "Live Chat",
        "Live Chat with AI + Humans | Qefro",
        "Qefro live chat combines AI answers on your website with human handoff, lead capture, and optional API actions.",
        "<p>Qefro live chat starts with grounded AI replies and hands off to humans when needed — with full thread context.</p>",
        (
            "Visitors open the widget for instant answers from your knowledge base. When they ask for a person, agents continue in the team inbox.",
            "Lead capture collects emails mid-conversation for sales-assist flows without a separate form tool.",
            "Pair live chat with Business Tools so “track my order” hits your API instead of a canned reply.",
        ),
        (
            "Website widget live chat",
            "AI deflection + human handoff",
            "Lead capture",
            "Streaming responses",
            "Brandable UI",
        ),
        related=(
            ("website-ai-chat", "Website AI chat"),
            ("team-inbox", "Team inbox"),
            ("voice-ai", "Voice AI"),
            ("ai-customer-support", "AI customer support"),
        ),
    ),
    _f(
        "voice-ai",
        "Voice AI",
        "Voice AI in Website Chat | Qefro",
        "Qefro Voice AI adds speech-to-text and text-to-speech inside the website widget for hands-free customer support.",
        "<p>Use Qefro Voice AI in the website widget so visitors can speak questions and hear answers without a separate voice product.</p>",
        (
            "Voice lowers friction on mobile and for accessibility. STT/TTS runs in the widget experience alongside text chat.",
            "Answers still come from your RAG knowledge and can trigger the same Business Tools as typed messages.",
            "Keep voice on Customer AI surfaces you enable — internal teams can continue with text in the Internal Portal.",
        ),
        (
            "STT and TTS in the widget",
            "Same knowledge as text chat",
            "Works with business actions",
            "Optional per deployment",
            "Pairs with live chat handoff",
        ),
        related=(
            ("website-ai-chat", "Website AI chat"),
            ("live-chat", "Live chat"),
            ("ai-customer-support", "AI customer support"),
        ),
    ),
    _f(
        "knowledge-base",
        "Knowledge Base",
        "AI Knowledge Base | Qefro",
        "Qefro knowledge base features: uploads, crawl, OCR, multilingual hybrid RAG, citations, and per-workspace isolation.",
        "<p>The Qefro knowledge base powers grounded answers for Customer AI and Employee AI with citations and isolation.</p>",
        (
            "Each workspace gets its own index so public support content never mixes with confidential HR files.",
            "Ingest PDFs, DOCX, Markdown, TXT, and crawled pages. OCR covers scans. Hybrid search improves tough queries.",
            "Govern from the Admin Console: who can upload, which channels can read which workspace, and how tools are scoped.",
        ),
        (
            "Multi-format ingestion",
            "Website crawl",
            "OCR",
            "Citations and refusal",
            "Workspace isolation",
        ),
        related=(
            ("knowledge-base-ai", "Knowledge base AI"),
            ("website-crawl", "Website crawl"),
            ("rag", "RAG"),
            ("document-chat-ai", "Document chat"),
        ),
    ),
    _f(
        "website-crawl",
        "Website Crawl",
        "Website Crawl for AI Knowledge | Qefro",
        "Crawl your website into Qefro’s knowledge base so Customer AI stays updated with public pages and FAQs.",
        "<p>Qefro website crawl indexes your public pages into a workspace knowledge base for grounded chat answers.</p>",
        (
            "Keep marketing and help center pages in sync without manual copy-paste into a bot CMS.",
            "Combine crawl with PDF uploads for deeper manuals that are not on the public site.",
            "Re-crawl when content changes so answers track your latest policies.",
        ),
        (
            "Automated site ingestion",
            "Pairs with document uploads",
            "Workspace-scoped indexes",
            "Feeds website and WhatsApp AI",
            "Admin Console controls",
        ),
        related=(
            ("knowledge-base", "Knowledge base"),
            ("website-ai-chat", "Website AI chat"),
            ("rag-chatbot", "RAG chatbot"),
        ),
    ),
    _f(
        "whatsapp-ai",
        "WhatsApp AI",
        "WhatsApp AI Channel | Qefro",
        "Enable WhatsApp AI on Qefro Starter+ — shared knowledge and business actions with your website Customer AI.",
        "<p>Qefro WhatsApp AI uses the same workspaces, retrieval, and Business Tools as your website assistant.</p>",
        (
            "Configure WhatsApp in the Admin Console instead of maintaining a second bot stack.",
            "Customers get consistent answers whether they message on-site or in WhatsApp.",
            "Available on Starter and higher plans with Growth unlocking unlimited business system connections.",
        ),
        (
            "Shared RAG knowledge",
            "Business Tool actions",
            "Handoff-ready threads",
            "Starter+ availability",
            "Admin Console setup",
        ),
        related=(
            ("whatsapp-ai-agent", "WhatsApp AI agent"),
            ("ai-customer-support", "AI customer support"),
            ("pricing", "Pricing"),
        ),
    ),
    _f(
        "internal-ai",
        "Internal AI",
        "Internal AI Portal for Employees | Qefro",
        "Qefro Internal AI gives employees a branded portal for workspace chat, documents, citations, and secure internal actions.",
        "<p>Employee AI on Qefro is a branded Internal Portal — workspaces, conversations, documents, and citations for your teams.</p>",
        (
            "HR, IT, Finance, and Engineering each get isolated knowledge and tools under one organization.",
            "Hosted as yourcompany.qefro.com style experiences so employees have a clear place to ask and act.",
            "Same security model as Customer AI: RBAC, encryption, and optional API actions with identity controls.",
        ),
        (
            "Branded Internal Portal",
            "Per-team workspaces",
            "Document chat with citations",
            "Internal Business Tools",
            "Owner/Admin/Member roles",
        ),
        related=(
            ("knowledge-base", "Knowledge base"),
            ("sso", "SSO"),
            ("ai-for-saas", "AI for SaaS"),
            ("helpdesk-ai", "Helpdesk AI"),
        ),
    ),
    _f(
        "analytics",
        "Analytics",
        "AI Conversation Analytics | Qefro",
        "Qefro analytics help you monitor conversations, channels, and assistant usage from the Admin Console.",
        "<p>Use Qefro analytics in the Admin Console to understand conversation volume and how Customer AI and Employee AI are used.</p>",
        (
            "See where demand concentrates — widget, WhatsApp, or internal portal — and which workspaces are busiest.",
            "Pair analytics with execution logs when debugging Business Tool runs.",
            "Improve content where refusal rates or handoffs signal knowledge gaps.",
        ),
        (
            "Conversation and channel insights",
            "Admin Console dashboards",
            "Supports content iteration",
            "Complements audit logs",
            "Org-wide visibility for owners",
        ),
        related=(
            ("team-inbox", "Team inbox"),
            ("audit-logs", "Audit logs"),
            ("customer-support-automation", "Support automation"),
        ),
    ),
    _f(
        "team-inbox",
        "Team Inbox",
        "Team Inbox & Human Handoff | Qefro",
        "Qefro team inbox receives human handoffs from AI chat with full conversation context for support agents.",
        "<p>The Qefro team inbox lets agents take over AI conversations with history, sources, and tool context intact.</p>",
        (
            "Customers should never restart their story after escalation. Handoff brings the thread to humans cleanly.",
            "Use inbox workflows alongside AI deflection so routine questions never reach agents.",
            "Owners and admins manage access through RBAC so only the right teams see customer conversations.",
        ),
        (
            "AI-to-human handoff",
            "Full thread context",
            "Works with website chat",
            "RBAC-aware access",
            "Pairs with analytics",
        ),
        related=(
            ("live-chat", "Live chat"),
            ("ai-customer-support", "AI customer support"),
            ("helpdesk-ai", "Helpdesk AI"),
        ),
    ),
    _f(
        "rag",
        "RAG",
        "RAG Retrieval for Business AI | Qefro",
        "Qefro RAG: hybrid BM25 + vector retrieval, multilingual indexing, citations, workspace filters, and refusal when unsure.",
        "<p>Qefro’s RAG stack retrieves only from your tenant’s content with hybrid search, citations, and safe refusals.</p>",
        (
            "Production RAG needs filters for tenant and workspace, not a single shared index. Qefro isolates by design.",
            "Hybrid search helps exact IDs and fuzzy questions. Multilingual and OCR expand what you can index.",
            "Publishable benchmark methodology explains how we think about accuracy and refusal — not vanity chat scores.",
        ),
        (
            "Hybrid retrieval",
            "Citations",
            "Workspace filters",
            "Multilingual + OCR",
            "Managed infrastructure",
        ),
        related=(
            ("rag-chatbot", "RAG chatbot"),
            ("benchmark", "Benchmark"),
            ("knowledge-base", "Knowledge base"),
            ("document-chat-ai", "Document chat"),
        ),
    ),
    _f(
        "api",
        "API",
        "Qefro API & Backend SDK",
        "Use the Qefro API surface and Backend SDK for identity, tool callbacks, and secure business actions alongside REST/OpenAPI tools.",
        "<p>Integrate with Qefro via REST/OpenAPI Business Tools or the Backend SDK for auth and workflow control.</p>",
        (
            "Import OpenAPI specs to expose existing APIs as assistant tools with encrypted credentials.",
            "Prefer the Backend SDK when authentication and multi-step workflows must stay in your service.",
            "identify() forwards end-user identity into chat so actions authorize as the real user.",
        ),
        (
            "OpenAPI import",
            "REST Business Tools",
            "Backend SDK",
            "identify() identity forwarding",
            "Execution logs",
        ),
        related=(
            ("integrations", "Integrations"),
            ("sso", "SSO"),
            ("ai-for-saas", "AI for SaaS"),
            ("docs", "Docs"),
        ),
    ),
    _f(
        "sso",
        "SSO",
        "SSO / SAML for Qefro (Roadmap)",
        "SSO and SAML are on the Qefro Enterprise roadmap. Today: email OTP auth, RBAC, and identity forwarding for actions.",
        "<p>SSO/SAML is on Qefro’s Enterprise roadmap. Today organizations use email OTP, RBAC, and identify() for end-user actions.</p>",
        (
            "We list SSO honestly as roadmap so buyers can plan identity strategy without surprise marketing claims.",
            "Current controls still include workspace RBAC, tenant isolation, and encrypted secrets.",
            "Contact Sales for Enterprise identity timelines and private deployment options.",
        ),
        (
            "SSO/SAML on Enterprise roadmap",
            "Email OTP today (no password store)",
            "Owner/Admin/Member RBAC",
            "identify() for customer identity",
            "Talk to Sales for roadmap dates",
        ),
        related=(
            ("security", "Security"),
            ("internal-ai", "Internal AI"),
            ("contact", "Contact"),
            ("pricing", "Pricing"),
        ),
    ),
    _f(
        "integrations",
        "Integrations",
        "Integrations | REST, OpenAPI & SDK | Qefro",
        "Qefro integrations connect your APIs as Business Tools via REST/OpenAPI or the Backend SDK — with encrypted secrets and logs.",
        "<p>Integrate Qefro with your stack through REST/OpenAPI Business Tools or the Backend SDK — no rip-and-replace of systems of record.</p>",
        (
            "Import an OpenAPI document or configure REST endpoints. Credentials stay encrypted at rest.",
            "Outbound calls use HTTPS with SSRF protections. Execution logs support debugging and audits.",
            "Use the SDK when you need custom auth or multi-step workflows behind your firewall.",
        ),
        (
            "OpenAPI import",
            "REST tools",
            "Backend SDK",
            "Encrypted secrets",
            "SSRF-aware webhooks",
        ),
        related=(
            ("api", "API"),
            ("helpdesk-ai", "Helpdesk AI"),
            ("ai-for-ecommerce", "AI for ecommerce"),
            ("audit-logs", "Audit logs"),
        ),
    ),
    _f(
        "audit-logs",
        "Audit Logs",
        "Audit & Execution Logs | Qefro",
        "Qefro audit and execution logs attach conversation history and Business Tool runs for accountability and review.",
        "<p>Qefro keeps conversation and Business Tool execution logs so teams can review what the assistant answered and which actions ran.</p>",
        (
            "Support QA and compliance stakeholders need evidence — not black-box chat. Logs show tool invocations alongside threads.",
            "Combine with RBAC so only authorized roles inspect sensitive conversations.",
            "Platform-wide admin audit trail enhancements remain on the Enterprise roadmap; execution logs are available for Business Tools today.",
        ),
        (
            "Conversation history",
            "Business Tool execution logs",
            "Supports QA reviews",
            "Works with RBAC",
            "Enterprise audit roadmap items",
        ),
        related=(
            ("security", "Security"),
            ("integrations", "Integrations"),
            ("analytics", "Analytics"),
            ("sso", "SSO"),
        ),
    ),
)


def all_landings() -> tuple[Landing, ...]:
    from seo_verticals import VERTICAL_LANDINGS

    return TOPIC_LANDINGS + INDUSTRY_LANDINGS + FEATURE_LANDINGS + VERTICAL_LANDINGS


def sitemap_slugs() -> list[str]:
    return [L.slug for L in all_landings()]


def topic_link_grid() -> list[tuple[str, str]]:
    return [(L.slug, L.h1) for L in TOPIC_LANDINGS]


def industry_link_grid() -> list[tuple[str, str]]:
    return [(L.slug, L.h1) for L in INDUSTRY_LANDINGS]


def feature_link_grid() -> list[tuple[str, str]]:
    return [(L.slug, L.h1) for L in FEATURE_LANDINGS]


def vertical_link_grid() -> list[tuple[str, str]]:
    from seo_verticals import vertical_link_grid as _grid

    return _grid()
