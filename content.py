"""
content.py — Game content for Venture Foundry: The Evidence Economy.

All the printed "cards," ladders, and lookup tables from the simulation design
live here so instructors can tune the game without touching application logic.
"""

# --------------------------------------------------------------------------- #
# Opportunity territories (teams get a territory, not a product)
# --------------------------------------------------------------------------- #
OPPORTUNITY_TERRITORIES = [
    "Supporting aging adults living independently",
    "Reducing food waste",
    "Improving student financial well-being",
    "Helping small local retailers",
    "Increasing access to outdoor recreation",
    "Improving employee scheduling",
    "Supporting independent content creators",
    "Reducing household energy use",
    "Improving pet care",
    "Reducing administrative work for professionals",
]

# --------------------------------------------------------------------------- #
# Founder cards — capabilities and constraints
# --------------------------------------------------------------------------- #
FOUNDER_CARDS = [
    {
        "name": "Design & Social Founders",
        "skills": "Strong design and social-media skills; no programming capability",
        "networks": "University students and local retailers",
        "budget": 2000,
        "hours": 120,
        "risk": "Moderate",
        "ethics": "Will not use manipulative dark-pattern pricing",
    },
    {
        "name": "Technical Founders",
        "skills": "Full-stack development and data skills; limited sales experience",
        "networks": "Developer communities and two local startups",
        "budget": 3500,
        "hours": 100,
        "risk": "High",
        "ethics": "Strict about user data privacy",
    },
    {
        "name": "Operations Founders",
        "skills": "Logistics, operations, and supplier relationships; weak on branding",
        "networks": "Regional suppliers and small manufacturers",
        "budget": 2500,
        "hours": 140,
        "risk": "Low",
        "ethics": "Prioritizes fair supplier terms",
    },
    {
        "name": "Domain-Expert Founders",
        "skills": "Deep industry knowledge in health and aging services; no tech build skills",
        "networks": "Care facilities and community organizations",
        "budget": 1500,
        "hours": 160,
        "risk": "Low",
        "ethics": "Cautious about vulnerable populations",
    },
    {
        "name": "Growth & Sales Founders",
        "skills": "Sales, partnerships, and growth marketing; no design or engineering",
        "networks": "SMB owners and local media",
        "budget": 3000,
        "hours": 110,
        "risk": "High",
        "ethics": "Transparent advertising only",
    },
    {
        "name": "Finance-Minded Founders",
        "skills": "Financial modeling, pricing, and unit economics; limited customer network",
        "networks": "Local investors and accountants",
        "budget": 4000,
        "hours": 90,
        "risk": "Moderate",
        "ethics": "Avoids predatory lending models",
    },
]

# A neutral, well-rounded founder card used by the "balanced" quick setup so that
# no team starts with an inherent skill advantage.
BALANCED_FOUNDER_CARD = {
    "name": "Balanced Founders",
    "skills": "A rounded mix of design, technical, and commercial ability with no single "
              "dominant strength or fatal gap",
    "networks": "University community plus a few local businesses",
    "budget": 3000,
    "hours": 120,
    "risk": "Moderate",
    "ethics": "Committed to honest, privacy-respecting practices",
}

# --------------------------------------------------------------------------- #
# Difficulty levels — set the starting resources every team receives.
# Higher difficulty = leaner cash, credits, hours, and a lower market ceiling,
# so teams must be more disciplined. Every team in a cohort uses the SAME level,
# which is what keeps their odds of success equal.
# --------------------------------------------------------------------------- #
DIFFICULTY_ORDER = ["Novice", "Easy", "Standard", "Hard", "Expert"]
DIFFICULTY_LEVELS = {
    "Novice": {
        "capital": 6000, "credits": 30, "hours": 200, "market_potential": 1_500_000,
        "blurb": "Very forgiving. Generous cash, credits, and time — good for a first "
                 "run or a short course where you want teams to experiment freely.",
    },
    "Easy": {
        "capital": 4500, "credits": 20, "hours": 160, "market_potential": 1_250_000,
        "blurb": "Comfortable resources with a little pressure. Mistakes are recoverable.",
    },
    "Standard": {
        "capital": 3000, "credits": 12, "hours": 120, "market_potential": 1_000_000,
        "blurb": "The default balance. Teams must prioritize which assumptions to test.",
    },
    "Hard": {
        "capital": 2000, "credits": 8, "hours": 100, "market_potential": 800_000,
        "blurb": "Scarce resources. Every experiment purchase is a real trade-off.",
    },
    "Expert": {
        "capital": 1200, "credits": 5, "hours": 80, "market_potential": 600_000,
        "blurb": "Ruthless scarcity. Only the cheapest, highest-learning experiments "
                 "survive — best for advanced or capstone students.",
    },
}

# --------------------------------------------------------------------------- #
# Evidence-strength ladder — behavior beats opinion
# --------------------------------------------------------------------------- #
EVIDENCE_LADDER = [
    ("Founder opinion", 0),
    ("Friend or classmate opinion", 1),
    ("Customer statement about a hypothetical action", 2),
    ("Customer description of past behavior", 4),
    ("Observed customer behavior", 6),
    ("Customer provides contact info / requests follow-up", 7),
    ("Customer invests time in a trial", 8),
    ("Customer signs a letter of intent", 9),
    ("Customer pays or makes a binding commitment", 10),
]
EVIDENCE_LADDER_MAP = {label: value for label, value in EVIDENCE_LADDER}

# Evidence Credits awarded per unit of evidence strength when logged to the ledger.
CREDITS_PER_STRENGTH = 1.0

# --------------------------------------------------------------------------- #
# Value Proposition Auction
#   Each team gets a pool of Venture Tokens to allocate across its competing
#   value propositions. Allocation reveals confidence; evidence determines
#   whether that confidence is warranted.
#     alignment = tokens-weighted average evidence support (0..1)
#     Overconfidence Tax   = (1 - alignment) * OVERCONFIDENCE_TAX_MAX  credits
#     Learning Dividend    = max(0, alignment - prev_alignment) * LEARNING_DIVIDEND_MAX
#   Net Evidence Credit change = dividend - tax.
# --------------------------------------------------------------------------- #
VENTURE_TOKEN_POOL = 100
MIN_VALUE_PROPS = 3            # must field at least three competing propositions
OVERCONFIDENCE_TAX_MAX = 8.0  # max credits taxed when tokens sit on unsupported VPs
LEARNING_DIVIDEND_MAX = 8.0   # max credits earned for redirecting toward evidence

# --------------------------------------------------------------------------- #
# Value Proposition Canvas & Business Model Canvas block definitions
# --------------------------------------------------------------------------- #
CUSTOMER_PROFILE_BLOCKS = [
    ("customer_jobs", "Customer Jobs", "Functional, social, and emotional jobs the customer is trying to get done"),
    ("pains", "Pains", "Bad outcomes, risks, and obstacles the customer experiences"),
    ("gains", "Gains", "Benefits and outcomes the customer wants"),
]

VPC_BLOCKS = [
    ("products_services", "Products & Services", "What you offer"),
    ("pain_relievers", "Pain Relievers", "How your offer eases specific customer pains"),
    ("gain_creators", "Gain Creators", "How your offer produces specific customer gains"),
    ("jobs_addressed", "Customer Jobs Addressed", "Which jobs this proposition targets"),
    ("pains_reduced", "Specific Pains Reduced", "Named pains you reduce"),
    ("gains_created", "Specific Gains Created", "Named gains you create"),
]

BMC_BLOCKS = [
    ("customer_segments", "Customer Segments", "For whom are we creating value?"),
    ("value_propositions", "Value Propositions", "What value do we deliver?"),
    ("channels", "Channels", "How do we reach and deliver to customers?"),
    ("customer_relationships", "Customer Relationships", "What relationship does each segment expect?"),
    ("revenue_streams", "Revenue Streams", "For what value are customers willing to pay?"),
    ("key_resources", "Key Resources", "What assets does the model require?"),
    ("key_activities", "Key Activities", "What must we do well?"),
    ("key_partners", "Key Partners", "Who helps us?"),
    ("cost_structure", "Cost Structure", "What are the dominant costs?"),
]

# --------------------------------------------------------------------------- #
# Assumption risk types (Strategyzer testing lens)
# --------------------------------------------------------------------------- #
RISK_TYPES = ["Desirability", "Feasibility", "Viability", "Adaptability"]

# --------------------------------------------------------------------------- #
# Experiment marketplace
# Each card: cost in money, founder-hours, Evidence Credits; evidence strength;
# suitable assumption/risk types; bias to watch; minimum sample.
# --------------------------------------------------------------------------- #
EXPERIMENT_CARDS = [
    {"name": "Customer interview", "money": 0, "hours": 6, "credits": 1, "strength": 4,
     "suits": "Desirability", "bias": "Leading questions, confirmation bias", "sample": "5+ interviews"},
    {"name": "Observation", "money": 0, "hours": 5, "credits": 1, "strength": 6,
     "suits": "Desirability", "bias": "Hawthorne effect", "sample": "5+ observations"},
    {"name": "Expert interview", "money": 50, "hours": 3, "credits": 1, "strength": 3,
     "suits": "Feasibility", "bias": "Expert may not be the customer", "sample": "2+ experts"},
    {"name": "Search trend analysis", "money": 0, "hours": 2, "credits": 1, "strength": 3,
     "suits": "Desirability", "bias": "Correlation not intent", "sample": "N/A"},
    {"name": "Clickable prototype", "money": 100, "hours": 12, "credits": 3, "strength": 6,
     "suits": "Desirability", "bias": "Novelty effect", "sample": "10+ users"},
    {"name": "Paper prototype", "money": 20, "hours": 6, "credits": 2, "strength": 4,
     "suits": "Desirability", "bias": "Imagination gap", "sample": "8+ users"},
    {"name": "Concierge experiment", "money": 150, "hours": 20, "credits": 4, "strength": 7,
     "suits": "Desirability", "bias": "Not scalable, founder effort masks flaws", "sample": "3+ customers"},
    {"name": "Wizard-of-Oz experiment", "money": 200, "hours": 18, "credits": 4, "strength": 7,
     "suits": "Feasibility", "bias": "Manual work hides real cost", "sample": "5+ customers"},
    {"name": "Landing-page test", "money": 120, "hours": 8, "credits": 3, "strength": 6,
     "suits": "Desirability", "bias": "Traffic quality varies", "sample": "100+ visitors"},
    {"name": "Advertisement test", "money": 250, "hours": 6, "credits": 3, "strength": 6,
     "suits": "Desirability", "bias": "Ad fatigue, audience mismatch", "sample": "1000+ impressions"},
    {"name": "Email-response test", "money": 30, "hours": 4, "credits": 2, "strength": 5,
     "suits": "Desirability", "bias": "List bias", "sample": "50+ recipients"},
    {"name": "Preorder", "money": 100, "hours": 10, "credits": 4, "strength": 9,
     "suits": "Viability", "bias": "Refund expectations", "sample": "10+ prospects"},
    {"name": "Letter of intent", "money": 0, "hours": 8, "credits": 3, "strength": 9,
     "suits": "Viability", "bias": "Non-binding optimism", "sample": "3+ signers"},
    {"name": "Price-sensitivity test", "money": 60, "hours": 6, "credits": 3, "strength": 6,
     "suits": "Viability", "bias": "Stated vs. actual willingness to pay", "sample": "20+ respondents"},
    {"name": "Sales conversation", "money": 0, "hours": 8, "credits": 2, "strength": 7,
     "suits": "Viability", "bias": "Relationship bias", "sample": "8+ conversations"},
    {"name": "Technical feasibility test", "money": 300, "hours": 25, "credits": 4, "strength": 6,
     "suits": "Feasibility", "bias": "Prototype not production", "sample": "N/A"},
    {"name": "Partner interview", "money": 0, "hours": 5, "credits": 1, "strength": 4,
     "suits": "Feasibility", "bias": "Politeness, non-commitment", "sample": "3+ partners"},
    {"name": "Cost quotation", "money": 0, "hours": 4, "credits": 2, "strength": 5,
     "suits": "Viability", "bias": "Quotes change at scale", "sample": "3+ quotes"},
    {"name": "Channel test", "money": 180, "hours": 10, "credits": 3, "strength": 6,
     "suits": "Adaptability", "bias": "Channel saturation", "sample": "2+ channels"},
]
EXPERIMENT_CARD_MAP = {c["name"]: c for c in EXPERIMENT_CARDS}

# --------------------------------------------------------------------------- #
# Market events by category. Each event exposes an embedded assumption.
# --------------------------------------------------------------------------- #
MARKET_EVENTS = {
    "Customer": [
        ("Customers value convenience but distrust data collection.", "Customers will trust the proposed data use."),
        ("The assumed user is not the buyer.", "The user and the buyer are the same person."),
        ("An underserved customer segment appears.", "Your chosen segment is the best entry point."),
        ("Customers use the product differently than expected.", "Customers adopt the intended primary job."),
        ("Customers like the solution but will not change current behavior.", "Customers will switch from the status quo."),
    ],
    "Competitive": [
        ("A competitor launches a free version.", "Customers will pay for your core value."),
        ("A large platform copies the primary feature.", "Your key feature is defensible."),
        ("A substitute becomes more attractive.", "Your value proposition beats substitutes."),
        ("A competitor secures an exclusive partner.", "Your key partner will remain available."),
        ("A low-cost competitor enters the market.", "Customers are not primarily price-driven."),
    ],
    "Operational": [
        ("Supplier prices increase by 25%.", "Your cost structure is stable."),
        ("A key partner withdraws.", "Partners will agree to participate."),
        ("Delivery time doubles.", "You can deliver within the promised time."),
        ("Technical reliability declines.", "The technology can hit required reliability."),
        ("Demand exceeds available capacity.", "You can scale delivery with demand."),
    ],
    "Regulatory & Ethical": [
        ("New privacy requirements limit data collection.", "Regulations permit the proposed data use."),
        ("An algorithm creates unequal outcomes.", "Your solution treats users fairly."),
        ("A customer asks for an ethically questionable feature.", "Growth will not require ethical compromise."),
        ("A partner requests ownership of customer data.", "You retain control of customer relationships."),
        ("Investors pressure the venture to use manipulative pricing.", "You can grow without dark patterns."),
    ],
    "Financial": [
        ("Customer acquisition cost increases.", "CAC stays below your target."),
        ("Investors reduce available funding.", "Capital will remain available on demand."),
        ("Customers demand a free trial.", "Customers commit without heavy free usage."),
        ("Payment processing costs rise.", "Your margin absorbs transaction costs."),
        ("Revenue arrives later than expected.", "Your cash flow timing is viable."),
    ],
}

# --------------------------------------------------------------------------- #
# Performance dashboard dimensions
# --------------------------------------------------------------------------- #
DASHBOARD_DIMENSIONS = [
    ("Customer Insight", "Quality and specificity of customer understanding"),
    ("Value Proposition Fit", "Alignment among jobs, pains, gains, relievers, and creators"),
    ("Evidence Strength", "Quality of evidence supporting critical assumptions"),
    ("Business-Model Coherence", "Alignment among the nine BMC elements"),
    ("Experiment Efficiency", "Learning generated per dollar and founder-hour"),
    ("Financial Viability", "Revenue, cost, margin, acquisition, and retention logic"),
    ("Adaptability", "Ability to revise the model appropriately"),
    ("Responsible Innovation", "Management of ethical and stakeholder risks"),
    ("Team Execution", "Preparation, role fulfillment, and decision quality"),
    ("Investor Confidence", "Overall credibility of the venture"),
]
DIMENSION_NAMES = [d[0] for d in DASHBOARD_DIMENSIONS]

# --------------------------------------------------------------------------- #
# Team roles (rotate every 2–3 weeks)
# --------------------------------------------------------------------------- #
TEAM_ROLES = [
    ("Venture Architect", "Maintains the Business Model Canvas and identifies inconsistencies."),
    ("Customer Advocate", "Challenges claims that lack customer evidence."),
    ("Experiment Lead", "Designs tests and protects experiment validity."),
    ("Financial Skeptic", "Tests pricing, costs, revenue, and unit economics."),
    ("Evidence Auditor", "Evaluates the quality of information and documents learning."),
    ("Responsible Innovation Officer", "Identifies privacy, fairness, trust, and stakeholder risks."),
]

# --------------------------------------------------------------------------- #
# Semester structure (15 weeks)
# --------------------------------------------------------------------------- #
SEMESTER = [
    (1, "Founder formation", "Entrepreneurial opportunity and design", "Founder means inventory"),
    (2, "Opportunity framing", "Initial business idea and customer segment", "Opportunity portfolio"),
    (3, "Customer discovery", "Customer jobs, pains, and gains", "Interview records"),
    (4, "Customer evidence", "Customer profile and evidence quality", "Revised customer profile"),
    (5, "Value creation", "Products/services, pain relievers, gain creators", "Value Proposition Canvas"),
    (6, "Value proposition fit", "Problem–solution fit and prioritization", "Fit assessment"),
    (7, "Business-model architecture", "Nine Business Model Canvas blocks", "BMC Version 1"),
    (8, "Assumption testing", "Desirability, feasibility, viability, adaptability", "Assumption map"),
    (9, "Experiment design", "Hypotheses, experiments, metrics, thresholds", "Experiment cards"),
    (10, "Market testing", "Evidence strength and learning", "Evidence reports"),
    (11, "Pivot decisions", "Pivot, persevere, or stop", "BMC Version 2"),
    (12, "Business economics", "Revenue, costs, pricing, channels, unit economics", "Economic viability model"),
    (13, "Scaling and competition", "Channels, resources, activities, partners, defensibility", "Scaling plan"),
    (14, "Investment readiness", "Evidence narrative and business-model coherence", "Investment memorandum"),
    (15, "Venture market", "Final business-model defense", "Final evidence portfolio"),
]

VENTURE_STAGES = [
    "Opportunity formation",
    "Customer understanding",
    "Value proposition design",
    "Business-model development",
    "Evidence generation",
    "Venture launch and investment defense",
]

PIVOT_DECISIONS = [
    "Approved",
    "Conditional",
    "NeedsEvidence",
    "Rejected",
    "RandomChange",
]
