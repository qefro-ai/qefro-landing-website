"""AI Customer Support for {vertical} programmatic pages.

Each vertical is a structured record. The builder produces unique copy so we can
scale to many niches without hand-writing full HTML for every page.
"""

from __future__ import annotations

from dataclasses import dataclass

from seo_landings import Landing


@dataclass(frozen=True)
class VerticalSpec:
    key: str  # slug suffix: dental-clinics → ai-customer-support-for-dental-clinics
    label: str  # Dental Clinics
    audience: str  # patients, guests, students…
    setting: str  # clinic, hotel, campus…
    top_questions: tuple[str, str, str]
    actions: tuple[str, str, str]
    staff_workspace: str
    trust_note: str
    channel_note: str
    related_keys: tuple[str, ...] = ()


# Seed verticals — extend this list to grow topical surface area.
VERTICAL_SPECS: tuple[VerticalSpec, ...] = (
    VerticalSpec(
        "dental-clinics",
        "Dental Clinics",
        "patients",
        "dental practice",
        (
            "Do you accept my insurance?",
            "How do I prepare for a root canal?",
            "Can I reschedule my cleaning?",
        ),
        (
            "Look up appointment slots via your scheduling API",
            "Create a front-desk ticket for insurance questions",
            "Send post-visit care instructions from approved docs",
        ),
        "hygiene protocols, fee guides, and front-desk scripts",
        "Keep clinical advice limited to approved patient education — refuse when content is missing.",
        "Website widget for new patients; optional WhatsApp for reminders and FAQs.",
        ("clinics", "hospitals", "healthcare-practices"),
    ),
    VerticalSpec(
        "clinics",
        "Clinics",
        "patients",
        "outpatient clinic",
        (
            "What are your visiting hours?",
            "How do I get lab results?",
            "Where do I park for my appointment?",
        ),
        (
            "Check appointment status in your EMR/scheduling API",
            "Open a nurse-line ticket for callback requests",
            "Route billing questions to your billing workflow API",
        ),
        "nursing SOPs, referral policies, and intake checklists",
        "Separate public FAQs from internal clinical protocols with workspace isolation.",
        "Embed on the clinic site; use WhatsApp where patients already message staff.",
        ("dental-clinics", "hospitals", "urgent-care"),
    ),
    VerticalSpec(
        "hotels",
        "Hotels",
        "guests",
        "hotel property",
        (
            "What time is check-in?",
            "Is breakfast included?",
            "Can I request a late checkout?",
        ),
        (
            "Fetch reservation status from your PMS API",
            "Create a concierge ticket for special requests",
            "Share local guide content from your knowledge base",
        ),
        "housekeeping SOPs, safety procedures, and upsell playbooks",
        "Public guest answers stay cited from property content; staff SOPs stay in private workspaces.",
        "Website chat for bookers; WhatsApp for in-stay questions.",
        ("restaurants", "travel-agencies", "vacation-rentals"),
    ),
    VerticalSpec(
        "universities",
        "Universities",
        "students and parents",
        "campus",
        (
            "When does registration open?",
            "How do I apply for housing?",
            "Where do I find financial aid forms?",
        ),
        (
            "Create an IT or registrar helpdesk ticket",
            "Point to the correct portal link from approved docs",
            "Capture leads for admissions follow-up",
        ),
        "faculty handbooks, IT runbooks, and student services scripts",
        "Multilingual RAG helps diverse student communities without separate bots per language.",
        "Public admissions widget plus Internal Portal for staff and faculty.",
        ("schools", "colleges", "edtech"),
    ),
    VerticalSpec(
        "hospitals",
        "Hospitals",
        "patients and families",
        "hospital system",
        (
            "How do I find a specialist?",
            "What documents do I bring for admission?",
            "Where is the visitor desk?",
        ),
        (
            "Create a patient-services ticket",
            "Share wayfinding and department FAQs from approved content",
            "Escalate clinical questions to human staff — never invent care advice",
        ),
        "department protocols, IT runbooks, and HR policies",
        "Not a diagnostic system — only retrieve approved knowledge and hand off clinical questions.",
        "Public FAQs on the hospital site; staff Internal Portal for protocols.",
        ("clinics", "dental-clinics", "urgent-care"),
    ),
    VerticalSpec(
        "restaurants",
        "Restaurants",
        "diners",
        "restaurant group",
        (
            "Do you have vegan options?",
            "Can I book a table for six?",
            "What are your catering packages?",
        ),
        (
            "Check reservation availability via your booking API",
            "Capture catering leads for the events team",
            "Share allergen and menu PDFs with citations",
        ),
        "franchise SOPs, allergen procedures, and shift checklists",
        "Allergen answers must come from current menu docs — refuse when the knowledge base is outdated.",
        "Website widget + WhatsApp for reservations and catering.",
        ("hotels", "retail", "cafes"),
    ),
    VerticalSpec(
        "logistics",
        "Logistics",
        "shippers and consignees",
        "logistics company",
        (
            "Where is my shipment?",
            "What are your cut-off times?",
            "How do I file a claim?",
        ),
        (
            "Look up tracking status from your TMS/WMS API",
            "Create a claims or support ticket with shipment context",
            "Quote published rate-card rules from documents",
        ),
        "driver SOPs, warehouse safety docs, and exception playbooks",
        "Live tracking should come from your systems of record — Qefro calls your APIs rather than storing shipment truth.",
        "Customer portal widget and WhatsApp for high-volume status questions.",
        ("retail", "ecommerce", "manufacturing"),
    ),
    VerticalSpec(
        "retail",
        "Retail",
        "shoppers",
        "retail brand",
        (
            "What is your return policy?",
            "Do you price-match?",
            "Where is my online order?",
        ),
        (
            "Fetch order status from your ecommerce/OMS API",
            "Create a support ticket for damaged items",
            "Capture leads for personal shopping appointments",
        ),
        "store ops manuals, loss-prevention briefs, and seasonal playbooks",
        "Keep return windows and promos cited from current policy docs to avoid outdated answers.",
        "Site chat for shoppers; WhatsApp for post-purchase support.",
        ("ecommerce", "restaurants", "logistics"),
    ),
    # Additional niches for surface area (still unique structured fields)
    VerticalSpec(
        "schools",
        "Schools",
        "parents and students",
        "K-12 school",
        (
            "When is the school calendar published?",
            "How do I report an absence?",
            "What are bus routes?",
        ),
        (
            "Create an attendance or IT ticket",
            "Share handbook sections with citations",
            "Capture enrollment interest leads",
        ),
        "teacher handbooks and facilities SOPs",
        "Keep student PII out of public workspaces; use private portals for staff.",
        "Public FAQ widget; staff Internal Portal for policies.",
        ("universities", "colleges", "daycare"),
    ),
    VerticalSpec(
        "colleges",
        "Colleges",
        "students",
        "college campus",
        (
            "How do I drop a class?",
            "Where is the counseling center?",
            "How do meal plans work?",
        ),
        (
            "Open a registrar or student-services ticket",
            "Link to the correct self-service portal from docs",
            "Answer housing FAQs from approved packets",
        ),
        "student affairs playbooks and IT runbooks",
        "Workspace isolation keeps student-facing FAQs separate from HR content.",
        "Website and optional WhatsApp for student services.",
        ("universities", "schools", "edtech"),
    ),
    VerticalSpec(
        "ecommerce",
        "Ecommerce Brands",
        "online shoppers",
        "online store",
        (
            "How long does shipping take?",
            "Can I change my address?",
            "Do you ship internationally?",
        ),
        (
            "Return live tracking from your order API",
            "Start a return or exchange ticket",
            "Quote shipping zones from policy docs",
        ),
        "CX macros, fraud playbooks, and warehouse SOPs",
        "Ground sizing and policy answers in current catalogs — refuse when SKU data is not indexed.",
        "Storefront widget + WhatsApp for order updates.",
        ("retail", "logistics", "saas"),
    ),
    VerticalSpec(
        "saas",
        "SaaS Companies",
        "product users",
        "software company",
        (
            "How do I reset SSO?",
            "Where are webhook docs?",
            "How do I upgrade my plan?",
        ),
        (
            "Create a support ticket in your helpdesk API",
            "Run account lookups with identify() for signed-in users",
            "Point to changelog and docs with citations",
        ),
        "CS runbooks and on-call playbooks",
        "Use identify() so account actions authorize as the real user — passwords never stored in Qefro.",
        "In-app or marketing-site widget; Internal Portal for CS and success.",
        ("ecommerce", "fintech", "agencies"),
    ),
    VerticalSpec(
        "real-estate",
        "Real Estate Agencies",
        "buyers and renters",
        "brokerage",
        (
            "Is this listing still available?",
            "What are HOA fees?",
            "Can I schedule a viewing?",
        ),
        (
            "Capture a viewing-request lead to your CRM API",
            "Share brochure and disclosure PDFs with citations",
            "Escalate negotiation questions to a human agent",
        ),
        "compliance scripts and transaction checklists",
        "Public listing answers stay in public workspaces; offer docs stay private to agents.",
        "Website chat for listings; WhatsApp for touring logistics.",
        ("property-management", "hotels", "mortgage"),
    ),
    VerticalSpec(
        "property-management",
        "Property Management",
        "tenants",
        "property portfolio",
        (
            "How do I submit a maintenance request?",
            "When is rent due?",
            "How do I renew my lease?",
        ),
        (
            "Create a maintenance work order via your API",
            "Share lease FAQ excerpts with citations",
            "Route payment questions to your billing workflow",
        ),
        "vendor SOPs and emergency procedures",
        "Emergency safety instructions must come from approved docs and escalate quickly to humans.",
        "Tenant portal widget; staff Internal Portal for ops.",
        ("real-estate", "hotels", "facilities"),
    ),
    VerticalSpec(
        "travel-agencies",
        "Travel Agencies",
        "travelers",
        "travel agency",
        (
            "What is your cancellation policy?",
            "Do I need a visa for this trip?",
            "Can I change my flight dates?",
        ),
        (
            "Look up booking status via your GDS/booking API",
            "Create a change-request ticket for agents",
            "Share visa checklist PDFs from approved content",
        ),
        "destination playbooks and supplier escalation guides",
        "Visa and medical advice must be limited to published checklists — hand off edge cases.",
        "Website + WhatsApp for travelers across time zones.",
        ("hotels", "airlines", "tour-operators"),
    ),
    VerticalSpec(
        "manufacturing",
        "Manufacturing",
        "B2B buyers and partners",
        "manufacturing company",
        (
            "What is the lead time for SKU X?",
            "Where is my PO status?",
            "Do you have ISO certificates?",
        ),
        (
            "Fetch order or PO status from ERP APIs",
            "Share certificate PDFs with citations",
            "Create a quality or logistics ticket",
        ),
        "SOP manuals, safety docs, and quality playbooks",
        "Operator Internal Portal for SOPs; public site for buyer FAQs only.",
        "Buyer portal chat; optional WhatsApp for distributors.",
        ("logistics", "wholesale", "industrial-supplies"),
    ),
    VerticalSpec(
        "law-firms",
        "Law Firms",
        "prospective clients",
        "law practice",
        (
            "Do you handle my case type?",
            "How do consultations work?",
            "Where are your offices?",
        ),
        (
            "Capture intake leads to your CRM/practice API",
            "Share published practice-area FAQs with citations",
            "Book consult slots via your scheduling API when allowed",
        ),
        "intake checklists and conflicts procedures",
        "Never invent legal advice — only published marketing FAQs, then human attorneys.",
        "Website widget for intake; private workspaces for staff knowledge.",
        ("accounting-firms", "insurance", "consultancies"),
    ),
    VerticalSpec(
        "accounting-firms",
        "Accounting Firms",
        "clients",
        "accounting practice",
        (
            "When are tax documents due?",
            "How do I upload my files securely?",
            "Who is my account manager?",
        ),
        (
            "Create a client-service ticket",
            "Share filing calendar excerpts from approved docs",
            "Point to your secure upload portal link",
        ),
        "engagement letter templates and internal review checklists",
        "Tax guidance must stay within published firm content; escalate complex scenarios to CPAs.",
        "Client portal widget; Internal Portal for staff.",
        ("law-firms", "insurance", "fintech"),
    ),
    VerticalSpec(
        "insurance",
        "Insurance Agencies",
        "policyholders",
        "insurance agency",
        (
            "How do I file a claim?",
            "What does my deductible mean?",
            "Can I update my beneficiaries?",
        ),
        (
            "Start a claim intake ticket via your API",
            "Cite policy FAQ language from approved docs",
            "Escalate coverage disputes to licensed agents",
        ),
        "claims playbooks and compliance scripts",
        "Coverage answers must cite current policy materials; licensed humans handle advice.",
        "Website and WhatsApp for FNOL-style FAQs with handoff.",
        ("fintech", "healthcare-practices", "law-firms"),
    ),
    VerticalSpec(
        "fintech",
        "Fintech",
        "account holders",
        "fintech product",
        (
            "How do I verify my identity?",
            "Why was my transfer delayed?",
            "Where are fee disclosures?",
        ),
        (
            "Create a support case in your ticketing API",
            "Share fee schedule PDFs with citations",
            "Use identify() for authenticated account questions",
        ),
        "ops runbooks and compliance macros",
        "Refuse speculative financial advice; stick to disclosed product docs and human escalation.",
        "In-app or web widget with identity forwarding.",
        ("saas", "insurance", "ecommerce"),
    ),
    VerticalSpec(
        "gyms",
        "Gyms & Fitness Clubs",
        "members",
        "fitness club",
        (
            "What are your class times?",
            "How do I freeze my membership?",
            "Do you have day passes?",
        ),
        (
            "Check membership status via your club API",
            "Create a front-desk ticket for billing issues",
            "Share class schedule pages from crawled content",
        ),
        "trainer SOPs and safety procedures",
        "Medical or training advice stays limited to approved club content.",
        "Website chat + WhatsApp for memberships and classes.",
        ("spas", "retail", "healthcare-practices"),
    ),
    VerticalSpec(
        "spas",
        "Spas & Wellness",
        "guests",
        "spa",
        (
            "Which treatments are available today?",
            "What is your cancellation policy?",
            "Do you offer couples packages?",
        ),
        (
            "Check booking availability via your spa API",
            "Capture package inquiry leads",
            "Cite aftercare instructions from approved PDFs",
        ),
        "therapist protocols and sanitation checklists",
        "Clinical-adjacent claims must stay within published service descriptions.",
        "Website and WhatsApp for bookings.",
        ("gyms", "hotels", "dental-clinics"),
    ),
    VerticalSpec(
        "auto-dealerships",
        "Auto Dealerships",
        "shoppers and owners",
        "dealership",
        (
            "Is this vehicle still available?",
            "What financing options do you offer?",
            "How do I book a service appointment?",
        ),
        (
            "Create a sales or service lead in your CRM API",
            "Book service slots via your DMS/scheduling API",
            "Share warranty FAQ excerpts with citations",
        ),
        "F&I scripts and service advisor playbooks",
        "Financing details must cite current offers; humans close regulated credit conversations.",
        "Inventory pages widget; WhatsApp for service reminders.",
        ("retail", "insurance", "logistics"),
    ),
    VerticalSpec(
        "veterinary-clinics",
        "Veterinary Clinics",
        "pet owners",
        "vet clinic",
        (
            "Do you take emergencies?",
            "What vaccines does my puppy need?",
            "How do I refill a prescription?",
        ),
        (
            "Create a triage or callback ticket",
            "Share vaccine schedule PDFs from approved content",
            "Point to prescription refill portal links",
        ),
        "clinical SOPs and controlled-substance procedures",
        "Not a substitute for veterinary diagnosis — educate from approved materials and escalate.",
        "Website widget for FAQs; staff portal for protocols.",
        ("clinics", "dental-clinics", "pet-stores"),
    ),
    VerticalSpec(
        "pharmacies",
        "Pharmacies",
        "patients",
        "pharmacy",
        (
            "Is my prescription ready?",
            "What are your hours?",
            "Do you deliver?",
        ),
        (
            "Check refill status via your pharmacy API when integrated",
            "Share published counseling FAQs with citations",
            "Create a pharmacist-callback ticket",
        ),
        "dispensing SOPs and counseling checklists",
        "Medication advice must stay within approved counseling content; pharmacists handle clinical judgment.",
        "Store site widget; optional WhatsApp for pickup updates.",
        ("clinics", "hospitals", "healthcare-practices"),
    ),
    VerticalSpec(
        "healthcare-practices",
        "Healthcare Practices",
        "patients",
        "medical practice",
        (
            "How do I complete intake forms?",
            "Which insurers do you accept?",
            "How do telehealth visits work?",
        ),
        (
            "Share intake links from approved content",
            "Create a front-desk callback ticket",
            "Cite telehealth policies from current docs",
        ),
        "clinical admin SOPs and billing macros",
        "No diagnostic chatbot claims — grounded education and human escalation only.",
        "Practice website chat; staff Internal Portal.",
        ("clinics", "hospitals", "dental-clinics"),
    ),
    VerticalSpec(
        "urgent-care",
        "Urgent Care Centers",
        "patients",
        "urgent care clinic",
        (
            "What is the current wait time?",
            "Do I need an appointment?",
            "What should I bring?",
        ),
        (
            "Publish wait guidance from approved ops content",
            "Create a front-desk triage ticket",
            "Share location and insurance FAQs with citations",
        ),
        "triage scripts and facility SOPs",
        "Emergency symptoms should always escalate to human/ER guidance from approved scripts.",
        "Website widget for wait/FAQ; WhatsApp optional.",
        ("clinics", "hospitals", "healthcare-practices"),
    ),
    VerticalSpec(
        "banks",
        "Banks & Credit Unions",
        "members and customers",
        "financial institution",
        (
            "How do I report a lost card?",
            "What are wire cut-off times?",
            "Where are fee schedules?",
        ),
        (
            "Create a secure-messaging or branch ticket",
            "Cite fee schedules from published disclosures",
            "Escalate fraud concerns to human specialists immediately",
        ),
        "branch ops manuals and fraud playbooks",
        "Regulated advice stays with licensed staff; AI cites disclosures and routes securely.",
        "Authenticated widget with identify(); public pages for product FAQs only.",
        ("fintech", "insurance", "mortgage"),
    ),
    VerticalSpec(
        "mortgage",
        "Mortgage Lenders",
        "borrowers",
        "mortgage company",
        (
            "What documents do I need to apply?",
            "How long does underwriting take?",
            "What are today’s published rate disclaimers?",
        ),
        (
            "Capture application interest leads to your LOS/CRM",
            "Share checklist PDFs with citations",
            "Create a loan-officer callback ticket",
        ),
        "processor checklists and compliance macros",
        "Rate and credit advice must follow published disclosures; humans close regulated conversations.",
        "Website chat for checklists; authenticated portal for borrowers when integrated.",
        ("real-estate", "banks", "insurance"),
    ),
    VerticalSpec(
        "agencies",
        "Marketing Agencies",
        "clients and prospects",
        "agency",
        (
            "What services do you offer?",
            "How do retainers work?",
            "Can I see case studies?",
        ),
        (
            "Capture RFP leads to your CRM",
            "Share case-study pages from crawled content",
            "Create an account-management ticket for clients",
        ),
        "delivery playbooks and brand guidelines",
        "Client workspaces stay private; public site answers stay on marketing content.",
        "Agency site widget; Internal Portal for teams.",
        ("saas", "consultancies", "ecommerce"),
    ),
    VerticalSpec(
        "consultancies",
        "Consultancies",
        "clients",
        "consulting firm",
        (
            "Which industries do you serve?",
            "How do engagements start?",
            "Where can I read whitepapers?",
        ),
        (
            "Capture inbound leads to CRM",
            "Cite published methodology PDFs",
            "Create a partner-request ticket",
        ),
        "delivery kits and proposal templates",
        "Confidential client materials stay in private workspaces — never on public Customer AI.",
        "Website widget for inbound; Internal Portal for consultants.",
        ("agencies", "law-firms", "saas"),
    ),
    VerticalSpec(
        "nonprofits",
        "Nonprofits",
        "donors and beneficiaries",
        "nonprofit organization",
        (
            "How do I donate?",
            "What programs do you run?",
            "How do I volunteer?",
        ),
        (
            "Capture donor or volunteer leads",
            "Share program FAQs with citations",
            "Create a constituent-services ticket",
        ),
        "program SOPs and volunteer handbooks",
        "Keep beneficiary PII out of public bots; use private staff workspaces.",
        "Website chat for donors; WhatsApp where communities prefer messaging.",
        ("schools", "government", "healthcare-practices"),
    ),
    VerticalSpec(
        "government",
        "Government Services",
        "residents",
        "public agency",
        (
            "How do I renew a permit?",
            "Where do I pay a fine?",
            "What are office hours?",
        ),
        (
            "Link to official payment portals from approved content",
            "Create a constituent ticket for callbacks",
            "Cite ordinance or FAQ pages carefully",
        ),
        "internal procedure manuals for staff",
        "Official answers must cite published agency content; escalate legal interpretations to staff.",
        "Public site widget; Internal Portal for employees.",
        ("utilities", "nonprofits", "universities"),
    ),
    VerticalSpec(
        "utilities",
        "Utilities",
        "ratepayers",
        "utility provider",
        (
            "How do I report an outage?",
            "How do I set up autopay?",
            "What is the reconnection process?",
        ),
        (
            "Create an outage or billing ticket via your API",
            "Cite published reconnection FAQs",
            "Share safety advisories from approved docs",
        ),
        "field ops SOPs and safety protocols",
        "Safety and outage guidance must come from approved scripts with fast human escalation.",
        "Website + WhatsApp for high-volume status questions.",
        ("government", "logistics", "property-management"),
    ),
    VerticalSpec(
        "airlines",
        "Airlines",
        "passengers",
        "airline",
        (
            "What is the baggage allowance?",
            "How do I change my flight?",
            "What is your disruption policy?",
        ),
        (
            "Look up booking status via your PSS/API when integrated",
            "Create a rebooking assistance ticket",
            "Cite published fare rules and baggage pages",
        ),
        "airport ops playbooks and disruption macros",
        "Operational changes move fast — ground answers in current published policies and hand off exceptions.",
        "Web + WhatsApp for travelers; staff portal for ops.",
        ("travel-agencies", "hotels", "logistics"),
    ),
    VerticalSpec(
        "tour-operators",
        "Tour Operators",
        "travelers",
        "tour company",
        (
            "What is included in the package?",
            "What is the cancellation window?",
            "Do you need fitness requirements?",
        ),
        (
            "Capture booking interest leads",
            "Cite itinerary PDFs with sources",
            "Create an operations ticket for day-of issues",
        ),
        "guide briefings and supplier escalation guides",
        "Safety requirements must come from current trip dossiers.",
        "Website and WhatsApp for pre-trip FAQs.",
        ("travel-agencies", "hotels", "airlines"),
    ),
    VerticalSpec(
        "vacation-rentals",
        "Vacation Rentals",
        "guests",
        "vacation rental portfolio",
        (
            "What is the check-in process?",
            "Is parking included?",
            "How do I request early check-in?",
        ),
        (
            "Fetch reservation details via your PMS API",
            "Create a guest-services ticket",
            "Share house manuals with citations",
        ),
        "turnover checklists and vendor SOPs",
        "House rules and local guidance should be property-specific knowledge bases.",
        "Listing-site chat and WhatsApp for guests.",
        ("hotels", "property-management", "real-estate"),
    ),
    VerticalSpec(
        "wholesale",
        "Wholesale Distributors",
        "retail buyers",
        "wholesale distributor",
        (
            "What are MOQ rules?",
            "Where is my B2B order?",
            "Do you have a dealer price list?",
        ),
        (
            "Fetch B2B order status from ERP APIs",
            "Share published catalog PDFs with citations",
            "Create an account-manager ticket",
        ),
        "warehouse SOPs and credit procedures",
        "Price lists may be workspace-gated for authenticated dealers only.",
        "Dealer portal widget with identity forwarding.",
        ("manufacturing", "retail", "logistics"),
    ),
    VerticalSpec(
        "industrial-supplies",
        "Industrial Supplies",
        "procurement teams",
        "industrial supplier",
        (
            "Do you stock this SKU?",
            "What is the cut-off for same-day ship?",
            "Where are SDS sheets?",
        ),
        (
            "Check inventory via your ERP/API",
            "Share SDS PDFs with citations",
            "Create a quotes or inside-sales ticket",
        ),
        "safety data procedures and warehouse manuals",
        "SDS and hazmat answers must cite current documents — no improvisation.",
        "Buyer portal chat; staff Internal Portal.",
        ("manufacturing", "wholesale", "logistics"),
    ),
    VerticalSpec(
        "edtech",
        "EdTech Companies",
        "teachers and students",
        "education technology product",
        (
            "How do I reset a student password?",
            "Where are LMS integration docs?",
            "What is your data privacy policy?",
        ),
        (
            "Create a support ticket with school context",
            "Cite help-center articles and privacy docs",
            "Use identify() for authenticated admin users",
        ),
        "CS escalation playbooks and status-page macros",
        "Student data stays out of public bots; use authenticated workspaces and your APIs.",
        "In-product widget; Internal Portal for CS.",
        ("saas", "schools", "universities"),
    ),
    VerticalSpec(
        "daycare",
        "Daycare & Childcare",
        "parents",
        "childcare center",
        (
            "What are your tuition rates?",
            "What is your illness policy?",
            "How do waitlists work?",
        ),
        (
            "Capture enrollment leads",
            "Cite handbook policies with sources",
            "Create a director callback ticket",
        ),
        "classroom SOPs and emergency procedures",
        "Child safety procedures must come from approved handbooks with human escalation.",
        "Website widget for parents; private staff portal.",
        ("schools", "healthcare-practices", "gyms"),
    ),
    VerticalSpec(
        "pet-stores",
        "Pet Stores",
        "pet owners",
        "pet retail",
        (
            "Do you groom on weekends?",
            "What is your return policy on food?",
            "Do you carry this brand?",
        ),
        (
            "Capture grooming appointment leads",
            "Cite return policies from current docs",
            "Create a special-order ticket",
        ),
        "store ops and animal-care SOPs",
        "Health advice for pets should stay educational and escalate to vets when needed.",
        "Store site chat + WhatsApp.",
        ("veterinary-clinics", "retail", "ecommerce"),
    ),
    VerticalSpec(
        "cafes",
        "Cafes & Coffee Shops",
        "guests",
        "cafe group",
        (
            "Do you have oat milk?",
            "What are catering minimums?",
            "Where is Wi-Fi info?",
        ),
        (
            "Capture catering leads",
            "Share allergen menus with citations",
            "Create a store-manager ticket for complaints",
        ),
        "barista SOPs and opening checklists",
        "Allergen info must track current menu documents.",
        "Website widget; WhatsApp for catering.",
        ("restaurants", "retail", "hotels"),
    ),
    VerticalSpec(
        "facilities",
        "Facilities Management",
        "occupants and vendors",
        "facilities organization",
        (
            "How do I report a building issue?",
            "What are loading-dock hours?",
            "How do visitor badges work?",
        ),
        (
            "Create a work order via your CMMS API",
            "Cite building handbook pages",
            "Capture vendor access requests",
        ),
        "EHS procedures and vendor manuals",
        "Safety incidents need approved scripts and immediate human escalation paths.",
        "Occupant portal chat; staff Internal Portal.",
        ("property-management", "manufacturing", "utilities"),
    ),
)


def _slug(key: str) -> str:
    return f"ai-customer-support-for-{key}"


def _build_landing(spec: VerticalSpec, all_keys: dict[str, VerticalSpec]) -> Landing:
    related: list[tuple[str, str]] = [
        ("ai-customer-support", "AI customer support"),
        ("whatsapp-ai-agent", "WhatsApp AI agent"),
        ("website-ai-chat", "Website AI chat"),
    ]
    for key in spec.related_keys:
        other = all_keys.get(key)
        if other:
            related.append((_slug(key), f"AI support for {other.label}"))
    related.append(("security", "Security"))

    q1, q2, q3 = spec.top_questions
    a1, a2, a3 = spec.actions
    label = spec.label
    audience = spec.audience
    setting = spec.setting

    paragraphs = (
        f"AI customer support for {label.lower()} helps {audience} get fast, accurate answers "
        f"about your {setting} — without hiring a 24/7 team for every repetitive question.",
        f"Typical questions include “{q1}”, “{q2}”, and “{q3}”. Qefro grounds replies in your "
        f"uploaded policies, crawled site pages, and handbooks, with source citations and refusal "
        f"when nothing relevant exists.",
        f"When chat must do more than answer, connect your systems: {a1.lower()}; {a2.lower()}; "
        f"{a3.lower()}. Credentials stay encrypted; actions can use end-user identity via identify().",
        f"Staff get a branded Internal Portal for {spec.staff_workspace}, while Customer AI stays "
        f"on the channels you enable. {spec.channel_note}",
        f"{spec.trust_note} Review our <a href=\"/security\">security overview</a> and "
        f"<a href=\"/pricing\">pricing</a> when you are ready to trial.",
    )

    # paragraphs currently have HTML in last one - Landing paragraphs are escaped in generator!
    # Need plain text only in paragraphs - put links in template instead.
    paragraphs = (
        f"AI customer support for {label.lower()} helps {audience} get fast, accurate answers "
        f"about your {setting} — without hiring a 24/7 team for every repetitive question.",
        f"Typical questions include “{q1}”, “{q2}”, and “{q3}”. Qefro grounds replies in your "
        f"uploaded policies, crawled site pages, and handbooks, with source citations and refusal "
        f"when nothing relevant exists.",
        f"When chat must do more than answer, connect your systems: {a1.lower()}; {a2.lower()}; "
        f"{a3.lower()}. Credentials stay encrypted; actions can use end-user identity via identify().",
        f"Staff get a branded Internal Portal for {spec.staff_workspace}, while Customer AI stays "
        f"on the channels you enable. {spec.channel_note}",
        f"{spec.trust_note} Start with a 14-day free trial, then scale workspaces as locations grow.",
    )

    bullets = (
        f"Grounded FAQs for {audience}",
        "Website widget and optional WhatsApp",
        "Business actions through your APIs",
        f"Internal Portal for {spec.staff_workspace.split(',')[0]}",
        "Workspace isolation and RBAC",
        "Citations and safe refusal behavior",
    )

    faqs = (
        (
            f"Is Qefro built for {label.lower()}?",
            f"Yes. Teams configure knowledge and channels for a {setting}, then deploy Customer AI "
            f"for {audience} and Employee AI for staff — without building RAG infrastructure.",
        ),
        (
            "Can it connect to our scheduling or order systems?",
            "Yes. Import OpenAPI or configure REST Business Tools, or use the Backend SDK for "
            "authenticated workflows in your stack.",
        ),
        (
            "How fast can we launch?",
            "Most teams embed the website widget in minutes, then upload policies or crawl the site. "
            "API actions depend on your integration readiness.",
        ),
    )

    return Landing(
        slug=_slug(spec.key),
        kind="vertical",
        h1=f"AI Customer Support for {label}",
        title=f"AI Customer Support for {label} | Qefro",
        description=(
            f"AI customer support for {label.lower()} with Qefro — grounded answers for {audience}, "
            f"website and WhatsApp chat, secure API actions, and an Internal Portal for staff."
        ),
        answer=(
            f"<p><strong>Qefro</strong> provides AI customer support for {label.lower()}: "
            f"cited answers for {audience}, optional WhatsApp, secure business actions, and "
            f"staff assistants in one AI Workspace Platform.</p>"
        ),
        paragraphs=paragraphs,
        bullets=bullets,
        related=tuple(related[:6]),
        faqs=faqs,
        badge="Vertical",
    )


def build_vertical_landings() -> tuple[Landing, ...]:
    by_key = {s.key: s for s in VERTICAL_SPECS}
    return tuple(_build_landing(s, by_key) for s in VERTICAL_SPECS)


VERTICAL_LANDINGS: tuple[Landing, ...] = build_vertical_landings()


def vertical_link_grid() -> list[tuple[str, str]]:
    return [(L.slug, L.h1) for L in VERTICAL_LANDINGS]
