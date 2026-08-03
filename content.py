"""
content.py — Game content for Venture Foundry: From hunch to hard evidence.

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
# `hours` is the founder's WEEKLY hours (raw, 40–80). Founders work long weeks, but
# productivity drops past 40 hours, so effective time grows more slowly (see
# logic.productive_hours). Each round the available time RESETS to this budget —
# unused hours are lost, they never accumulate. Time is split between running the
# business (experiments/canvases), training, and managing any hires.
# --------------------------------------------------------------------------- #
DIFFICULTY_ORDER = ["Novice", "Easy", "Standard", "Hard", "Expert"]
DIFFICULTY_LEVELS = {
    "Novice": {
        "capital": 6000, "credits": 30, "hours": 80, "market_potential": 1_500_000,
        "blurb": "Very forgiving. Generous cash and an 80-hour founder week.",
    },
    "Easy": {
        "capital": 4500, "credits": 20, "hours": 70, "market_potential": 1_250_000,
        "blurb": "Comfortable resources with a little pressure. ~70-hour week.",
    },
    "Standard": {
        "capital": 3000, "credits": 12, "hours": 60, "market_potential": 1_000_000,
        "blurb": "The default balance. A 60-hour founder week to build, train, and manage.",
    },
    "Hard": {
        "capital": 2000, "credits": 8, "hours": 50, "market_potential": 800_000,
        "blurb": "Scarce resources. ~50-hour week — every choice is a trade-off.",
    },
    "Expert": {
        "capital": 1200, "credits": 5, "hours": 42, "market_potential": 600_000,
        "blurb": "Ruthless scarcity. ~42-hour week; build or train, rarely both.",
    },
}

# Hours model constants.
FULL_PRODUCTIVITY_HOURS = 40   # hours up to this are fully productive
OVERWORK_PRODUCTIVITY = 0.5    # each hour beyond 40 counts as this much
MAX_WEEKLY_HOURS = 80
DEFAULT_HOURS_PER_WEEK = 60

# Skill progress (XP) is measured in EFFECTIVE hours. A level costs
# logic.skill_train_cost(level) effective hours; investing time or completing rounds
# banks progress toward it (partial effort is never wasted).
# Effective hours a founder banks toward the round's focus skills by completing it:
LEARNING_HOURS_PER_ROUND = 4

# --------------------------------------------------------------------------- #
# Founder / team skills — structured capabilities the team holds and can grow.
# Each skill has a DEFINITION (what it means to have it) and an EFFECT (what it
# does in the simulation). A team's starting levels come from its founder card;
# teams can train skills up over the semester by investing founder-hours.
# --------------------------------------------------------------------------- #
SKILL_MAX = 5

FOUNDER_SKILLS = [
    {"key": "customer_research", "name": "Customer Research", "dimension": "Customer Insight",
     "definition": "Finding, interviewing, and interpreting customers to uncover their real "
                   "jobs, pains, and gains — and telling behavior from opinion.",
     "effect": "Raises your Customer Insight and the credibility of interview evidence."},
    {"key": "design", "name": "Design & Prototyping", "dimension": "Value Proposition Fit",
     "definition": "Shaping offers and building prototypes that clearly communicate a value "
                   "proposition to customers.",
     "effect": "Raises Value Proposition Fit and makes prototype experiments more convincing."},
    {"key": "technical", "name": "Technical / Engineering", "dimension": "Business-Model Coherence",
     "definition": "Building the product and judging whether the technology can actually work "
                   "and be delivered reliably.",
     "effect": "Supports feasibility claims and strengthens business-model coherence."},
    {"key": "sales", "name": "Sales & Growth", "dimension": "Value Proposition Fit",
     "definition": "Reaching customers through channels and turning interest into real "
                   "commitments (trials, LOIs, preorders).",
     "effect": "Strengthens channel/sales experiments and willingness-to-pay evidence."},
    {"key": "finance", "name": "Finance & Unit Economics", "dimension": "Financial Viability",
     "definition": "Modeling pricing, costs, margins, and cash so the venture can capture "
                   "value and stay solvent.",
     "effect": "Raises Financial Viability and sharpens pricing-test interpretation."},
    {"key": "operations", "name": "Operations", "dimension": "Experiment Efficiency",
     "definition": "Running experiments and delivering reliably within limited time and budget.",
     "effect": "Improves Experiment Efficiency and delivery reliability."},
    {"key": "responsible", "name": "Responsible Innovation", "dimension": "Responsible Innovation",
     "definition": "Spotting privacy, fairness, trust, and stakeholder risks early and "
                   "addressing them responsibly.",
     "effect": "Raises Responsible Innovation and softens ethical/regulatory event penalties."},
]
FOUNDER_SKILL_KEYS = [s["key"] for s in FOUNDER_SKILLS]
FOUNDER_SKILL_BY_KEY = {s["key"]: s for s in FOUNDER_SKILLS}

# Starting skill levels (0–5) by founder-card archetype. Unlisted skills default to 1.
FOUNDER_CARD_SKILLS = {
    "Design & Social Founders": {"design": 4, "sales": 3, "customer_research": 2, "technical": 0},
    "Technical Founders": {"technical": 4, "operations": 3, "sales": 1, "customer_research": 1},
    "Operations Founders": {"operations": 4, "finance": 2, "technical": 2, "design": 1},
    "Domain-Expert Founders": {"customer_research": 4, "responsible": 3, "technical": 0, "finance": 1},
    "Growth & Sales Founders": {"sales": 4, "customer_research": 2, "design": 2, "finance": 1},
    "Finance-Minded Founders": {"finance": 4, "operations": 2, "customer_research": 1},
    "Balanced Founders": {k: 2 for k in FOUNDER_SKILL_KEYS},
}


def card_skill_levels(card_name):
    """Starting skill levels for a founder card (defaults to 1 for unlisted skills)."""
    overrides = FOUNDER_CARD_SKILLS.get(card_name, {})
    return {k: int(overrides.get(k, 1)) for k in FOUNDER_SKILL_KEYS}


# --------------------------------------------------------------------------- #
# Hiring — founders rarely have every skill. When a skill the venture needs is
# weak, teams can HIRE a specialist (part-time or full-time). A hire raises the
# team's EFFECTIVE level in that skill (founder level + hire boost, capped at 5).
#   • Part-time: cheaper upfront, small ongoing cost, modest boost.
#   • Full-time: bigger boost, higher upfront + a real salary each round (burn).
# Firing stops the ongoing cost and removes the boost.
# --------------------------------------------------------------------------- #
SPECIALIST_ROLES = {
    "customer_research": "Customer Researcher",
    "design": "Product Designer",
    "technical": "Software Engineer",
    "sales": "Sales & Growth Lead",
    "finance": "Finance Analyst",
    "operations": "Operations Manager",
    "responsible": "Ethics & Privacy Advisor",
}

# Hiring costs money AND the founder's time: `recruit_hours` (one-time, to find and
# onboard) and `manage_hours` (every round, to manage the person). Managing people
# is real founder time that then can't go to building or training.
HIRE_OPTIONS = {
    "part_time": {"label": "Part-time", "boost": 2, "upfront": 150, "per_round": 80,
                  "recruit_hours": 5, "manage_hours": 4, "work_hours": 20},
    "full_time": {"label": "Full-time", "boost": 3, "upfront": 400, "per_round": 200,
                  "recruit_hours": 10, "manage_hours": 8, "work_hours": 40},
}
HIRE_SKILL_CAP = 5   # effective skill (founder + hires) can't exceed this

# Founder effort model. Effort (total committed hours) = admin + managing + business
# dev + training + hiring, hard-capped at MAX_WEEKLY_HOURS and colour-coded by zone.
ADMIN_BASE_HOURS = 8       # unavoidable admin in round 1
ADMIN_MAX_HOURS = 18       # admin grows with rounds but caps here
EFFORT_GREEN = 40          # 0–40h: sustainable (green)
EFFORT_YELLOW = 60         # 40–60h: stretched (yellow); 60–80h: overwork (red)
ADMIN_OVERHEAD_PCT = 0.20  # (legacy; retained for compatibility)

# Which founder skills each stage/topic leans on most (drives hiring hints).
TOPIC_SKILL_NEEDS = {
    "founder_formation": [],
    "opportunity_framing": ["customer_research"],
    "customer_discovery": ["customer_research"],
    "customer_evidence": ["customer_research"],
    "value_creation": ["design"],
    "value_prop_fit": ["design", "customer_research"],
    "bmc_architecture": ["technical", "finance"],
    "assumption_testing": ["operations"],
    "experiment_design": ["operations", "technical"],
    "market_testing": ["operations"],
    "pivot_decisions": ["customer_research"],
    "business_economics": ["finance"],
    "scaling": ["sales", "operations"],
    "investment_readiness": ["finance", "sales"],
    "venture_market": ["sales", "responsible"],
}


# What each founder-card attribute MEANS and how it shapes play (shown on the "?").
FOUNDER_ATTR_HELP = {
    "skills": "**What your team is good at.** Skills that match your venture make experiments "
              "cheaper and your evidence more credible; gaps are risks to plan around. You can "
              "grow specific skills on the **Founder Skills** page.",
    "networks": "**Who you can already reach.** A strong, relevant network gets you interviews, "
                "pilots, and channel access faster — often your biggest head start on evidence. "
                "Start customer discovery with the people you can already contact.",
    "budget": "**The money you can afford to LOSE** (affordable loss), not a forecast of profit. "
              "Every experiment and pivot spends from here, so always look for the cheapest way "
              "to learn before committing more.",
    "hours": "**Founder-time you can invest this term.** Experiments and skill training cost "
             "hours as well as money. Spend them where the learning per hour is highest.",
    "risk": "**How much uncertainty your team will take on.** It shapes which bets fit you — a "
            "low-risk team favors many cheap tests; a high-risk team may run bigger ones. Neither "
            "is 'right'; be deliberate.",
    "ethics": "**A line you will not cross.** Some market events will tempt you to break it for "
              "growth. Holding the line protects your Responsible Innovation score and long-term "
              "trust; crossing it may cost you both.",
}

# Starter guidance for each opportunity territory — enough to get a team moving.
TERRITORY_GUIDE = {
    "Supporting aging adults living independently":
        "**Likely customers:** older adults living alone, plus their adult children and "
        "caregivers (often the buyer isn't the user). **Common pains:** safety fears, isolation, "
        "medication and appointment management, mobility. **Where to find them:** senior centers, "
        "community groups, care facilities, family caregivers you know. **Start by:** interviewing "
        "2–3 caregivers about the last time something went wrong at home.",
    "Reducing food waste":
        "**Likely customers:** households, restaurants/cafés, grocers, campus dining. "
        "**Common pains:** over-buying, spoilage, unsold stock, no easy way to redistribute. "
        "**Where to find them:** local cafés and grocers, dining halls, food banks. "
        "**Start by:** asking a café manager how much they throw out each day and why.",
    "Improving student financial well-being":
        "**Likely customers:** students (and sometimes parents or the university). **Common "
        "pains:** budgeting, surprise fees, debt anxiety, low financial literacy. **Where to "
        "find them:** classmates, student orgs, financial-aid offices. **Start by:** asking five "
        "students to walk you through their last money stress.",
    "Helping small local retailers":
        "**Likely customers:** independent shop owners and their staff. **Common pains:** "
        "footfall, online competition, inventory, marketing time, payments. **Where to find "
        "them:** main-street shops, local business associations. **Start by:** asking two owners "
        "what ate the most of their time last week.",
    "Increasing access to outdoor recreation":
        "**Likely customers:** would-be participants, families, and program/park providers. "
        "**Common pains:** cost, gear, know-how, safety, transport, time. **Where to find them:** "
        "outdoor clubs, rental shops, park programs. **Start by:** asking people who *want* to go "
        "outdoors more what stops them.",
    "Improving employee scheduling":
        "**Likely customers:** shift managers and hourly workers (buyer vs. user differ). "
        "**Common pains:** last-minute changes, understaffing, availability conflicts, "
        "compliance. **Where to find them:** cafés, retail, clinics, gig platforms. **Start by:** "
        "shadowing a manager building next week's schedule.",
    "Supporting independent content creators":
        "**Likely customers:** creators (video, audio, writing, art) at different scales. "
        "**Common pains:** inconsistent income, admin/editing time, discovery, burnout. **Where "
        "to find them:** creator communities, local meetups, classmates who post. **Start by:** "
        "asking three creators where their time actually goes.",
    "Reducing household energy use":
        "**Likely customers:** homeowners and renters (renters often can't change hardware). "
        "**Common pains:** high bills, no visibility, hassle of changing habits, upfront cost. "
        "**Where to find them:** neighbors, housing groups, utility programs. **Start by:** "
        "asking households what they've already tried and why it stuck or didn't.",
    "Improving pet care":
        "**Likely customers:** pet owners, plus vets, sitters, and shelters. **Common pains:** "
        "cost, time, health worries, travel/coverage, training. **Where to find them:** dog "
        "parks, vet clinics, pet-owner groups. **Start by:** asking owners about the last time "
        "their pet's care was stressful or expensive.",
    "Reducing administrative work for professionals":
        "**Likely customers:** busy professionals (clinicians, lawyers, teachers, tradespeople). "
        "**Common pains:** paperwork, scheduling, billing, compliance, repetitive data entry. "
        "**Where to find them:** professionals you know, local practices, associations. **Start "
        "by:** asking one professional to list the admin tasks they resent most.",
}


def territory_guide(territory):
    return TERRITORY_GUIDE.get(territory)


# Subtle "how to do well" hints per curriculum topic, woven into each round's email.
ROUND_HINTS = {
    "founder_formation":
        "Play to your founder card's strengths and be honest about its gaps — the strongest "
        "ventures fit who you are. Skim the tools, but this week just confirm your review and set "
        "a sustainable time allocation (green effort beats burning out).",
    "opportunity_framing":
        "Don't fall for the first idea. Generate several and compare them on customer importance "
        "AND founder-fit — how easily you can reach customers and afford to test matters as much "
        "as how exciting the idea sounds.",
    "customer_discovery":
        "Ask people about the last time they faced the problem, not what they'd hypothetically do. "
        "Log what they actually DID — behavioral evidence is worth far more than 'sounds good.'",
    "customer_evidence":
        "Look for patterns across your interviews and revise the Customer Profile from real "
        "findings. Flag the beliefs you still can't support — those are your riskiest spots.",
    "value_creation":
        "Sketch more than one value proposition and tie each pain reliever / gain creator to a "
        "specific customer pain or gain. Avoid marrying your first solution.",
    "value_prop_fit":
        "In the auction, back the proposition your evidence supports — not the one you love most. "
        "Redirecting toward evidence earns you a learning dividend; over-betting on a hunch is taxed.",
    "bmc_architecture":
        "Fill all nine blocks and check they reinforce each other. When a market event breaks one "
        "block, adjust the others so the model stays coherent.",
    "assumption_testing":
        "Rank assumptions by importance × how little evidence you have, and mark the ones that "
        "could kill the venture. An untested high-risk assumption is the fastest way to lose ground.",
    "experiment_design":
        "Write success and failure thresholds BEFORE you run a test, and spend on the cheapest "
        "experiment that yields the strongest evidence — learning per dollar is what counts.",
    "market_testing":
        "Run the test, record honest results, and update each assumption to Supported or Refuted — "
        "then log the resulting evidence to earn credits.",
    "pivot_decisions":
        "A pivot is a disciplined response to evidence, not frustration. If the evidence warrants "
        "it, file a clear pivot petition and save a new BMC version; if not, persevere on purpose.",
    "business_economics":
        "Test willingness to pay with real behavior — a preorder or letter of intent beats a "
        "survey — and check the per-customer math (price, cost, margin) actually works.",
    "scaling":
        "Shore up your channels, partners, and defensibility, and scan the environment (trends and "
        "disruptive forces) for what could threaten the model as you grow.",
    "investment_readiness":
        "Assemble a tight evidence narrative: what you know, how you know it, and what's still an "
        "assumption. Investors probe the gaps, so name them before they do.",
    "venture_market":
        "Lead with your single strongest piece of evidence, be honest about remaining uncertainty, "
        "and propose the next experiment you'd run — that candor builds investor confidence.",
}


def round_hint(topic_key):
    return ROUND_HINTS.get(topic_key, "")


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

# Business Model Environment Canvas (the UNITE / Strategyzer environment scan):
# the trends and forces that shape and disrupt the business model.
ENVIRONMENT_BLOCKS = [
    ("customer_trends", "Customer Trends", "Individualization, new experiences, behavioral "
     "shifts, refocus on purpose, digitalization of everything"),
    ("technology_trends", "Technology Trends", "AI, AR/VR, blockchain, IoT, automation & "
     "robotics, cloud, sensors, data rights & privacy"),
    ("mega_trends", "Dynamic Mega Trends", "Sustainability, next-gen workforce, wealth "
     "distribution, (de-)urbanization, climate change, cyber risk"),
    ("macro_forces", "Macro-Economic Forces", "Global market & trade, regulation, demographics, "
     "economic cycle, political forces, currency & price volatility"),
    ("market_forces", "Market Forces", "Supply & demand, market issues, switching costs, "
     "revenue attractiveness, globalization/deglobalization"),
    ("industry_forces", "Industry Forces", "Stakeholders & partners, suppliers, competitors "
     "(incumbents), new entrants, substitute products/services"),
    ("disruptive_forces", "Disruptive / Competitive Forces", "The five forces at the centre: "
     "new competitors, suppliers, customers, substitutes, and industry rivalry"),
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

# --------------------------------------------------------------------------- #
# Curriculum topics — the simulation builds in complexity as new concepts are
# introduced. Each topic: concepts taught in the FIRST class session, then the
# SECOND session is the simulation round applying them.
#
# Topics are an ORDERED LIST (not tied to fixed week numbers) so the Director can
# reorder them, change how many rounds the simulation runs, and schedule when each
# round advances. Each topic declares:
#   key         — stable identifier
#   introduces  — student tools first unlocked when this topic is reached
#   canvas      — which canvas is the focus this round (customer_profile/vpc/bmc/None)
#
# The three canvases are deliberately STAGED across several rounds so no single
# round is overloaded:
#   • Customer Profile — introduced at "Customer discovery", refined at "Customer evidence"
#   • Value Proposition Canvas — introduced at "Value creation", refined at "Value proposition fit"
#   • Business Model Canvas — introduced at "Business-model architecture", revised at Pivot & Scaling
# --------------------------------------------------------------------------- #

# Tools available from the very first round regardless of topic order.
BASE_TOOLS = ["Round Briefing", "Inbox", "Concept Check", "Dashboard",
              "Founder & Opportunity", "Founder & Team", "AI Assist Log", "Decision Journal"]

CURRICULUM_TOPICS = [
    {
        "key": "founder_formation",
        "title": "Founder formation",
        "concepts": ["Entrepreneurial opportunity vs. idea", "Founder means & constraints",
                     "Effectuation: bird-in-hand", "Founder & team time allocation"],
        "objectives": ["Inventory your team's means (who you are, what you know, whom you know).",
                        "Distinguish an opportunity territory from a product idea.",
                        "Plan how the founder's weekly time is split across activities."],
        "class_focus": "What an entrepreneurial opportunity is, why means come before ideas, and "
                       "how founders spend a finite week across running the business, learning, "
                       "and managing people.",
        "sim_task": "Review your founder card & territory, and set your founder time allocation.",
        "tool": "Founder & Opportunity", "introduces": ["Founder & Opportunity"], "canvas": None,
    },
    {
        "key": "opportunity_framing",
        "title": "Opportunity framing",
        "concepts": ["Opportunity portfolio", "Customer segment hypotheses", "Opportunity scoring"],
        "objectives": ["Generate at least three candidate ventures inside your territory.",
                        "Score options on importance, fit, access, evidence, and affordability.",
                        "Choose deliberately rather than committing to the first idea."],
        "class_focus": "Comparing multiple opportunities before committing.",
        "sim_task": "Add and score 3+ candidate ventures on the Founder & Opportunity page.",
        "tool": "Founder & Opportunity", "introduces": [], "canvas": None,
    },
    {
        "key": "customer_discovery",
        "title": "Customer discovery",
        "concepts": ["Customer jobs, pains, gains", "Problem interviews", "Behavior vs. opinion"],
        "objectives": ["Build a first Customer Profile (jobs/pains/gains).",
                        "Run problem interviews that surface behavior, not opinions.",
                        "Log interview evidence on the ladder."],
        "class_focus": "The customer side of the Value Proposition Canvas; interview technique.",
        "sim_task": "Create Customer Profile v1; log interview evidence.",
        "tool": "Canvases", "introduces": ["Canvases", "Evidence Ledger"], "canvas": "customer_profile",
    },
    {
        "key": "customer_evidence",
        "title": "Customer evidence",
        "concepts": ["Evidence quality & strength", "Pattern vs. contradiction", "Unsupported beliefs"],
        "objectives": ["Separate strong behavioral evidence from weak opinion.",
                        "Revise the Customer Profile from real findings.",
                        "Flag beliefs you still cannot support."],
        "class_focus": "What counts as credible customer evidence.",
        "sim_task": "Save Customer Profile v2 driven by evidence; grow the Evidence Ledger.",
        "tool": "Evidence Ledger", "introduces": [], "canvas": "customer_profile",
    },
    {
        "key": "value_creation",
        "title": "Value creation",
        "concepts": ["Products & services", "Pain relievers", "Gain creators"],
        "objectives": ["Draft the value-map side of the VPC.",
                        "Create at least three competing value propositions.",
                        "Tie each reliever/creator to a specific pain/gain."],
        "class_focus": "The value-map side of the Value Proposition Canvas.",
        "sim_task": "Build VPC v1 and add 3+ propositions to the VP Auction.",
        "tool": "Canvases", "introduces": ["VP Auction"], "canvas": "vpc",
    },
    {
        "key": "value_prop_fit",
        "title": "Value proposition fit",
        "concepts": ["Problem–solution fit", "Prioritization", "Confidence vs. evidence"],
        "objectives": ["Assess fit between value map and customer profile.",
                        "Allocate Venture Tokens to reveal confidence.",
                        "Redirect toward evidence to avoid the overconfidence tax."],
        "class_focus": "Judging fit and prioritizing the most important elements.",
        "sim_task": "Run a VP Auction round; record a fit assessment.",
        "tool": "VP Auction", "introduces": [], "canvas": "vpc",
    },
    {
        "key": "bmc_architecture",
        "title": "Business-model architecture",
        "concepts": ["Nine BMC blocks", "Block interdependence", "Value capture"],
        "objectives": ["Construct a complete Business Model Canvas.",
                        "Trace dependencies between blocks.",
                        "Respond coherently to a market event that breaks one block."],
        "class_focus": "The nine blocks of the Business Model Canvas and how they connect.",
        "sim_task": "Build BMC v1; respond to your first market event.",
        "tool": "Canvases", "introduces": ["Market Events"], "canvas": "bmc",
    },
    {
        "key": "assumption_testing",
        "title": "Assumption testing",
        "concepts": ["Desirability, feasibility, viability, adaptability",
                     "Assumption mapping", "Importance × evidence"],
        "objectives": ["Convert canvas elements into ranked assumptions.",
                        "Identify the assumptions that could destroy the venture.",
                        "Decide what to test and what to defer, with consequences."],
        "class_focus": "The four risk types and prioritizing what to test.",
        "sim_task": "Build the Assumption Map; mark the riskiest untested beliefs.",
        "tool": "Assumption Map", "introduces": ["Assumption Map"], "canvas": None,
    },
    {
        "key": "experiment_design",
        "title": "Experiment design",
        "concepts": ["Hypotheses & metrics", "Success/failure thresholds",
                     "Decision rules", "Experiment cost"],
        "objectives": ["Design experiments with pre-set thresholds.",
                        "Match experiment type to assumption and risk type.",
                        "Spend limited resources on the highest-learning tests."],
        "class_focus": "Turning assumptions into falsifiable experiments.",
        "sim_task": "Purchase and design experiment cards for your top assumptions.",
        "tool": "Experiment Marketplace", "introduces": ["Experiment Marketplace"], "canvas": None,
    },
    {
        "key": "market_testing",
        "title": "Market testing",
        "concepts": ["Minimum viable experiments", "Evidence strength", "Learning per dollar"],
        "objectives": ["Execute experiments and record honest results.",
                        "Update assumptions to Supported/Refuted.",
                        "Measure learning efficiency."],
        "class_focus": "Running MVEs and interpreting evidence.",
        "sim_task": "Record experiment results; log resulting evidence.",
        "tool": "Experiment Marketplace", "introduces": [], "canvas": None,
    },
    {
        "key": "pivot_decisions",
        "title": "Pivot decisions",
        "concepts": ["Pivot, persevere, or stop", "Evidence-based change", "Sunk-cost discipline"],
        "objectives": ["Decide whether contradictory evidence warrants a pivot.",
                        "File a disciplined pivot petition.",
                        "Rebuild the canvas while keeping it coherent (BMC v2)."],
        "class_focus": "What makes a pivot disciplined rather than random.",
        "sim_task": "Submit a Pivot Petition; save BMC v2 if approved.",
        "tool": "Pivot Petition", "introduces": ["Pivot Petition"], "canvas": "bmc",
    },
    {
        "key": "business_economics",
        "title": "Business economics",
        "concepts": ["Revenue & cost structure", "Pricing", "Unit economics", "Contribution margin"],
        "objectives": ["Test pricing and willingness to pay.",
                        "Compute contribution economics.",
                        "Judge whether the model can be viable."],
        "class_focus": "Revenue, costs, pricing, channels, and unit economics.",
        "sim_task": "Run a pricing test; capture an economic viability model in the BMC.",
        "tool": "Experiment Marketplace", "introduces": [], "canvas": "bmc",
    },
    {
        "key": "scaling",
        "title": "Scaling and competition",
        "concepts": ["Channels & partners", "Key resources/activities", "Defensibility",
                     "Environment scanning (trends & forces)"],
        "objectives": ["Respond to competitor moves and capacity limits.",
                        "Scan the environment — trends and disruptive forces around the model.",
                        "Articulate why the model is defensible."],
        "class_focus": "Scaling and defending the model; scanning the business-model environment.",
        "sim_task": "Update the BMC into a scaling plan and complete the Environment Canvas.",
        "tool": "Canvases", "introduces": [], "canvas": "bmc",
        "canvases": ["bmc", "environment"],
    },
    {
        "key": "investment_readiness",
        "title": "Investment readiness",
        "concepts": ["Evidence narrative", "Business-model coherence", "Due diligence"],
        "objectives": ["Assemble a coherent evidence narrative.",
                        "Anticipate adversarial investor questions.",
                        "Draft an investment memorandum."],
        "class_focus": "Building an evidence-based investment case.",
        "sim_task": "Prepare your investment memo; stress-test coherence.",
        "tool": "Dashboard", "introduces": [], "canvas": None,
    },
    {
        "key": "venture_market",
        "title": "Venture market (Evidence Exchange)",
        "concepts": ["Business-model defense", "Remaining uncertainty", "Next experiment"],
        "objectives": ["Defend the model with evidence, not advocacy.",
                        "State honestly what remains an assumption.",
                        "Propose the next most valuable experiment."],
        "class_focus": "The final defense: what you know, how you know it, what's next.",
        "sim_task": "Assemble the final evidence portfolio; present at the Evidence Exchange.",
        "tool": "Dashboard", "introduces": [], "canvas": None,
    },
]

CURRICULUM_BY_KEY = {t["key"]: t for t in CURRICULUM_TOPICS}
DEFAULT_TOPIC_ORDER = [t["key"] for t in CURRICULUM_TOPICS]
DEFAULT_TOTAL_ROUNDS = len(CURRICULUM_TOPICS)
CANVAS_TYPES = ["customer_profile", "vpc", "bmc", "environment"]

# --------------------------------------------------------------------------- #
# Round deliverables — the concrete things a team must complete to finish a round.
# Each has a `check` id the app evaluates against the team's saved work, the `tool`
# where it's done, and `must_update` (True = a new/changed artifact is required
# this round; False = informational).
# --------------------------------------------------------------------------- #
TOPIC_DELIVERABLES = {
    "founder_formation": [
        {"label": "Review your founder card & territory, then mark it reviewed",
         "check": "ack_founder_review", "tool": "Founder & Opportunity", "must_update": True},
        {"label": "Set your founder time allocation for the week",
         "check": "time_plan_set", "tool": "Founder & Team", "must_update": True},
    ],
    "opportunity_framing": [
        {"label": "Add and score at least 3 candidate ventures",
         "check": "ventures_ge_3", "tool": "Founder & Opportunity", "must_update": True},
    ],
    "customer_discovery": [
        {"label": "Save Customer Profile v1 (jobs / pains / gains)",
         "check": "cp_ge_1", "tool": "Canvases", "must_update": True},
        {"label": "Log at least 2 pieces of customer evidence",
         "check": "evidence_ge_2", "tool": "Evidence Ledger", "must_update": True},
    ],
    "customer_evidence": [
        {"label": "Revise the Customer Profile to v2 from real evidence",
         "check": "cp_ge_2", "tool": "Canvases", "must_update": True},
        {"label": "Grow the Evidence Ledger to at least 4 items",
         "check": "evidence_ge_4", "tool": "Evidence Ledger", "must_update": True},
    ],
    "value_creation": [
        {"label": "Save Value Proposition Canvas v1",
         "check": "vpc_ge_1", "tool": "Canvases", "must_update": True},
        {"label": "Add at least 3 competing value propositions",
         "check": "vps_ge_3", "tool": "VP Auction", "must_update": True},
    ],
    "value_prop_fit": [
        {"label": "Run a VP Auction round (allocate your tokens)",
         "check": "vp_results_ge_1", "tool": "VP Auction", "must_update": True},
    ],
    "bmc_architecture": [
        {"label": "Build Business Model Canvas v1 (fill all 9 blocks)",
         "check": "bmc_ge_1", "tool": "Canvases", "must_update": True},
    ],
    "assumption_testing": [
        {"label": "Map at least 5 assumptions and flag the riskiest",
         "check": "assumptions_ge_5", "tool": "Assumption Map", "must_update": True},
    ],
    "experiment_design": [
        {"label": "Design at least 2 experiments with pre-set thresholds",
         "check": "experiments_ge_2", "tool": "Experiment Marketplace", "must_update": True},
    ],
    "market_testing": [
        {"label": "Record results for at least 1 experiment",
         "check": "experiment_results_ge_1", "tool": "Experiment Marketplace", "must_update": True},
    ],
    "pivot_decisions": [
        {"label": "Submit a Pivot Petition (or justify persevering)",
         "check": "pivots_ge_1", "tool": "Pivot Petition", "must_update": True},
        {"label": "Save Business Model Canvas v2",
         "check": "bmc_ge_2", "tool": "Canvases", "must_update": True},
    ],
    "business_economics": [
        {"label": "Run a pricing or preorder test",
         "check": "pricing_exp", "tool": "Experiment Marketplace", "must_update": True},
    ],
    "scaling": [
        {"label": "Update the BMC into a scaling plan (new version)",
         "check": "bmc_ge_3", "tool": "Canvases", "must_update": True},
        {"label": "Complete the Business Model Environment Canvas (trends & forces)",
         "check": "env_ge_1", "tool": "Canvases", "must_update": True},
    ],
    "investment_readiness": [
        {"label": "Draft your investment memo (as this round's reflection)",
         "check": "reflection_this_round", "tool": "Decision Journal", "must_update": True},
    ],
    "venture_market": [
        {"label": "Assemble your final evidence portfolio (as this round's reflection)",
         "check": "reflection_this_round", "tool": "Decision Journal", "must_update": True},
    ],
}

# --------------------------------------------------------------------------- #
# Concept → decision mapping. A concept is "covered" the moment the team performs
# the decision that demonstrates it — no written answer needed. Only concepts that
# require judgment/reflection (not in this map) are checked with an open-ended
# question on the Concept Check page.
# --------------------------------------------------------------------------- #
CONCEPT_CHECKS = {
    # founder_formation
    "Founder means & constraints": "ack_founder_review",
    "Founder & team time allocation": "time_plan_set",
    # opportunity_framing
    "Opportunity portfolio": "ventures_ge_3",
    "Opportunity scoring": "ventures_ge_3",
    # customer_discovery
    "Customer jobs, pains, gains": "cp_ge_1",
    "Problem interviews": "evidence_ge_2",
    # customer_evidence
    "Evidence quality & strength": "evidence_ge_4",
    # value_creation
    "Products & services": "vpc_ge_1",
    "Pain relievers": "vpc_ge_1",
    "Gain creators": "vpc_ge_1",
    # value_prop_fit
    "Prioritization": "vp_results_ge_1",
    # bmc_architecture
    "Nine BMC blocks": "bmc_ge_1",
    # assumption_testing
    "Desirability, feasibility, viability, adaptability": "assumptions_ge_5",
    "Assumption mapping": "assumptions_ge_5",
    "Importance × evidence": "assumptions_ge_5",
    # experiment_design
    "Hypotheses & metrics": "experiments_ge_2",
    "Success/failure thresholds": "experiments_ge_2",
    "Decision rules": "experiments_ge_2",
    "Experiment cost": "experiments_ge_2",
    # market_testing
    "Minimum viable experiments": "experiment_results_ge_1",
    "Evidence strength": "experiment_results_ge_1",
    # pivot_decisions
    "Pivot, persevere, or stop": "pivots_ge_1",
    "Evidence-based change": "pivots_ge_1",
    # business_economics
    "Pricing": "pricing_exp",
    # scaling
    "Channels & partners": "bmc_ge_3",
    "Key resources/activities": "bmc_ge_3",
    "Environment scanning (trends & forces)": "env_ge_1",
    # investment_readiness
    "Evidence narrative": "reflection_this_round",
    # venture_market
    "Business-model defense": "reflection_this_round",
}


# --------------------------------------------------------------------------- #
# Concept quiz — a quick true/false understanding check for each concept that
# needs a written answer. Correct answers gate coverage alongside the applied
# answer, so teams show they GET the concept, not just that they typed something.
# --------------------------------------------------------------------------- #
CONCEPT_QUIZ = {
    "Entrepreneurial opportunity vs. idea": [
        ("An opportunity is a real, important customer problem worth solving — not just a "
         "product you imagine.", True)],
    "Effectuation: bird-in-hand": [
        ("Effectuation means starting from a fixed goal and predicting returns before you act.",
         False)],
    "Customer segment hypotheses": [
        ("A good customer-segment hypothesis is specific enough that you could go find five of "
         "those customers.", True)],
    "Behavior vs. opinion": [
        ("What a customer actually did is stronger evidence than what they said they might do.",
         True)],
    "Pattern vs. contradiction": [
        ("If new evidence contradicts your belief, the disciplined response is to ignore it and "
         "keep going.", False)],
    "Unsupported beliefs": [
        ("An untested assumption should be treated as fact if it feels obviously true.", False)],
    "Problem–solution fit": [
        ("Problem–solution fit means your offer relieves pains and creates gains the customer "
         "actually cares about.", True)],
    "Confidence vs. evidence": [
        ("Betting heavily on an idea your evidence doesn't support is rewarded in this "
         "simulation.", False)],
    "Block interdependence": [
        ("Changing one block of the Business Model Canvas can force changes in the others.",
         True)],
    "Value capture": [
        ("Value capture is about how the business earns revenue and sustains itself, not only "
         "the value it creates for customers.", True)],
    "Learning per dollar": [
        ("The best experiment is always the most expensive and thorough one.", False)],
    "Sunk-cost discipline": [
        ("Money and time already spent should decide whether you keep pursuing a failing idea.",
         False)],
    "Revenue & cost structure": [
        ("A business model needs both how it earns money and what it costs to deliver.", True)],
    "Unit economics": [
        ("Unit economics ask whether a single sale earns more than it costs to serve.", True)],
    "Contribution margin": [
        ("Contribution margin is revenue per unit minus the variable cost of that unit.", True)],
    "Defensibility": [
        ("Defensibility is about why competitors can't easily copy or undercut your model.",
         True)],
    "Business-model coherence": [
        ("A coherent business model has blocks that reinforce each other and are backed by "
         "evidence.", True)],
    "Due diligence": [
        ("Investors accept a founder's claims at face value without checking the evidence.",
         False)],
    "Remaining uncertainty": [
        ("A strong final pitch honestly states what is still an untested assumption.", True)],
    "Next experiment": [
        ("Once you have a business model, there's no value in identifying the next experiment.",
         False)],
}

# Domain vocabulary used to check that a written answer actually engages with the
# simulation's concepts (not generic filler).
_SIM_VOCAB_BASE = {
    "customer", "customers", "segment", "segments", "evidence", "assumption", "assumptions",
    "pivot", "persevere", "value", "proposition", "propositions", "pain", "pains", "gain",
    "gains", "job", "jobs", "experiment", "experiments", "hypothesis", "metric", "threshold",
    "market", "price", "pricing", "cost", "costs", "revenue", "margin", "channel", "channels",
    "behavior", "behaviour", "opinion", "willingness", "interview", "interviews", "test",
    "tested", "testing", "preorder", "prototype", "canvas", "risk", "desirability", "feasibility",
    "viability", "adaptability", "founder", "opportunity", "business", "model", "fit",
    "commitment", "signal", "learning", "defensibility", "unit", "economics", "investor",
    "coherence", "uncertainty", "verify", "validate", "data", "survey", "pilot", "trial",
}


_SIM_VOCAB_CACHE = None


def sim_vocab():
    """Simulation concept vocabulary: curated domain terms + words from every concept name."""
    global _SIM_VOCAB_CACHE
    if _SIM_VOCAB_CACHE is None:
        vocab = set(_SIM_VOCAB_BASE)
        for topic in CURRICULUM_TOPICS:
            for c in topic.get("concepts", []):
                for w in c.lower().replace("/", " ").replace("–", " ").split():
                    w = "".join(ch for ch in w if ch.isalpha())
                    if len(w) >= 4:
                        vocab.add(w)
        _SIM_VOCAB_CACHE = vocab
    return _SIM_VOCAB_CACHE


# Applies to every round in addition to the topic deliverables.
UNIVERSAL_DELIVERABLE = {
    "label": "Each member submits a Decision Journal reflection",
    "check": "reflection_this_round", "tool": "Decision Journal", "must_update": True,
}

# Tools that are always editable regardless of the round's focus.
ALWAYS_ACTIVE_TOOLS = ["Round Briefing", "Inbox", "Concept Check", "Dashboard",
                       "Founder & Team", "Decision Journal", "AI Assist Log"]

# --------------------------------------------------------------------------- #
# Concept library — a short definition and an "explore it" prompt for every
# concept in the curriculum, so students have something to learn from before
# they answer the concept check.
# --------------------------------------------------------------------------- #
CONCEPT_LIBRARY = {
    "Entrepreneurial opportunity vs. idea":
        ("An idea is a product you imagine; an opportunity is a real, important customer problem "
         "worth solving. Founders chase opportunities, not just ideas.",
         "Name the opportunity behind one idea you have — whose problem is it, and why does it matter?"),
    "Founder means & constraints":
        ("Effectuation's 'bird in hand': you start from who you are, what you know, and whom you "
         "know — plus your limits on money, time, and skills.",
         "List your team's means and your hard limits (budget you can lose, hours, skills)."),
    "Effectuation: bird-in-hand":
        ("Expert entrepreneurs start with available means and affordable loss rather than a fixed "
         "goal and predicted returns.",
         "What could you start testing this week using only what you already have?"),
    "Founder & team time allocation":
        ("A founder's week is finite. Beyond unavoidable admin/coordination and time spent "
         "managing any hires, the rest is split between RUNNING the business (customer discovery, "
         "experiments, canvases) and LEARNING (training + learning by doing). Allocating that "
         "time deliberately — and re-allocating as you learn — is a core founder skill.",
         "For this week, roughly what share of the founder's time should go to building vs. "
         "learning, and why?"),
    "Opportunity portfolio":
        ("Holding several possible ventures at once, instead of committing to the first idea, so "
         "you can compare them.",
         "Sketch three different ventures inside your territory."),
    "Customer segment hypotheses":
        ("A guess about which specific group of customers you'll serve first — stated so it can be "
         "checked.",
         "Who exactly is your first customer? Be specific enough to go find five of them."),
    "Opportunity scoring":
        ("Comparing options on importance, founder fit, access, evidence availability, and "
         "affordability instead of gut feel.",
         "Score your candidate ventures on those five factors and see which leads."),
    "Customer jobs, pains, gains":
        ("Jobs = what the customer is trying to get done; pains = bad outcomes/obstacles; gains = "
         "wanted benefits. The customer side of the VPC.",
         "For your segment, write two jobs, two pains, and two gains from real observation."),
    "Problem interviews":
        ("Conversations that explore the customer's world and past behavior — not a pitch of your "
         "solution.",
         "Draft three behavior-focused questions ('tell me about the last time…')."),
    "Behavior vs. opinion":
        ("What people DO predicts far better than what they SAY they would do. Behavioral evidence "
         "outranks opinion.",
         "Which of your findings are behavior, and which are just opinions?"),
    "Evidence quality & strength":
        ("Evidence sits on a ladder from founder opinion (weak) to paying customers (strong). "
         "Weight it accordingly.",
         "Rate your strongest and weakest piece of evidence on the ladder."),
    "Pattern vs. contradiction":
        ("Look for repeated signals across customers (patterns) and for findings that contradict "
         "your beliefs.",
         "What pattern have you seen 3+ times? What evidence contradicts a belief you held?"),
    "Unsupported beliefs":
        ("Claims you are treating as true but have no evidence for yet — the riskiest part of a "
         "plan.",
         "List two things you currently believe but cannot yet support."),
    "Products & services":
        ("The concrete things you offer that help customers get a job done — the value-map side of "
         "the VPC.",
         "List the products/services in your value proposition."),
    "Pain relievers":
        ("How your offer removes or reduces a specific customer pain.",
         "Match each pain reliever to an actual customer pain."),
    "Gain creators":
        ("How your offer produces a specific gain the customer wants.",
         "Match each gain creator to an actual customer gain."),
    "Problem–solution fit":
        ("Evidence that customers have the problem AND that your proposition addresses it — before "
         "you scale.",
         "What would convince a skeptic you have problem–solution fit?"),
    "Prioritization":
        ("Focusing scarce time/money on the few elements that matter most.",
         "Which single element of your value proposition matters most to test first?"),
    "Confidence vs. evidence":
        ("Feeling sure is not the same as being right. Bets should follow evidence, not enthusiasm.",
         "Where is your confidence highest but your evidence weakest?"),
    "Nine BMC blocks":
        ("Segments, value propositions, channels, relationships, revenue, resources, activities, "
         "partners, costs — the whole business on one page.",
         "Fill each block with your current best hypothesis."),
    "Block interdependence":
        ("The nine blocks depend on each other — change one and others must change to stay coherent.",
         "If your main channel doubled in cost, which other blocks change?"),
    "Value capture":
        ("Creating value isn't enough; the model must also capture some of it as revenue.",
         "How does your model capture value, and is it defensible?"),
    "Desirability, feasibility, viability, adaptability":
        ("The four risk lenses: do they want it (desirability), can we build it (feasibility), does "
         "the money work (viability), will it last (adaptability)?",
         "Name your biggest risk in each of the four categories."),
    "Assumption mapping":
        ("Turning every part of the model into a testable assumption and ranking them by importance "
         "and evidence.",
         "What assumption, if false, would collapse the whole venture?"),
    "Importance × evidence":
        ("Test first what is most important AND least supported by evidence.",
         "Which assumption scores highest on importance × (lack of) evidence?"),
    "Hypotheses & metrics":
        ("A hypothesis is a specific, falsifiable prediction; a metric is the number you'll measure "
         "to judge it.",
         "Write one hypothesis with the exact metric you'd measure."),
    "Success/failure thresholds":
        ("The result lines that define success vs. failure — set BEFORE running the test so you "
         "can't move the goalposts.",
         "Set a success and a failure threshold for your next test."),
    "Decision rules":
        ("What you'll actually DO for each outcome: persevere, pivot, or stop.",
         "Write the decision rule for your next experiment."),
    "Experiment cost":
        ("Every test costs money, time, and credits — spend on the highest learning per dollar.",
         "Which cheap test would teach you the most right now?"),
    "Minimum viable experiments":
        ("The smallest test that still produces credible evidence about an assumption.",
         "What's the smallest test that could disprove your riskiest assumption?"),
    "Evidence strength":
        ("Behavioral, committed evidence (trials, LOIs, payment) beats stated intent.",
         "How would you upgrade one weak piece of evidence to a stronger kind?"),
    "Learning per dollar":
        ("Judge experiments by how much uncertainty they remove per unit of money and time.",
         "Which experiment gave you the most learning per dollar so far?"),
    "Pivot, persevere, or stop":
        ("Three honest responses to evidence: keep going, change direction, or stop.",
         "Given your evidence, which of the three is warranted — and why?"),
    "Evidence-based change":
        ("A pivot is a disciplined change justified by evidence, not a reaction to frustration.",
         "What evidence would justify a pivot for you?"),
    "Sunk-cost discipline":
        ("Past effort already spent should not keep you in a losing direction.",
         "Is any belief you hold propped up mainly by effort you've already invested?"),
    "Revenue & cost structure":
        ("Where money comes from and where it goes — the financial backbone of the model.",
         "List your main revenue streams and your dominant costs."),
    "Pricing":
        ("What customers are willing to pay, tested with real behavior, not guesses.",
         "How could you test willingness to pay this round?"),
    "Unit economics":
        ("The per-customer math: revenue minus the cost to serve and acquire them.",
         "Estimate revenue and cost for one customer."),
    "Contribution margin":
        ("What's left from a sale after variable costs — it must eventually cover fixed costs.",
         "Roughly, what's your contribution margin per sale?"),
    "Channels & partners":
        ("How you reach and deliver to customers, and who helps you do it.",
         "Which channel and which partner is your model most dependent on?"),
    "Key resources/activities":
        ("The assets and the things you must do well for the model to work.",
         "What one resource or activity is most critical — and most at risk?"),
    "Defensibility":
        ("Why a competitor can't easily copy or undercut you.",
         "What makes your position hard to copy?"),
    "Environment scanning (trends & forces)":
        ("Your model lives in an environment of customer/technology/mega trends and of market, "
         "industry, macro-economic and competitive forces. Scanning them reveals threats and "
         "opportunities before they hit.",
         "Which trend or force could most disrupt your model in the next two years?"),
    "Evidence narrative":
        ("A clear story of what you know, how you know it, and what's still assumption.",
         "In three sentences, what do you know and how do you know it?"),
    "Business-model coherence":
        ("All nine blocks reinforce each other and the evidence, with no contradictions.",
         "Where is your model still internally inconsistent?"),
    "Due diligence":
        ("The adversarial questioning investors use to probe your claims.",
         "What's the hardest question an investor could ask you?"),
    "Business-model defense":
        ("Defending the model with evidence rather than persuasion.",
         "What's your single strongest piece of evidence to lead with?"),
    "Remaining uncertainty":
        ("Honestly stating what you still don't know.",
         "What is the biggest thing you still don't know?"),
    "Next experiment":
        ("The single most valuable test you would run next.",
         "What would you test next, and what result would change your mind?"),
}


def concept_help(concept):
    """(definition, explore_prompt) for a concept, with a generic fallback."""
    return CONCEPT_LIBRARY.get(
        concept,
        ("A concept introduced this round.",
         f"In a sentence or two, how does '{concept}' apply to your venture?"))

# --------------------------------------------------------------------------- #
# Generative-AI assist + verification methodology
#
# Students are expected to use generative AI every round. AI output is treated as
# founder OPINION (evidence strength 0) until it survives the AUDIT check and is
# translated into real-world evidence. This keeps the "evidence over advocacy"
# principle intact even when AI produces fluent, confident text.
# --------------------------------------------------------------------------- #
AI_AUDIT_STEPS = [
    ("A", "Assumptions surfaced",
     "What must be TRUE for this AI suggestion to hold? List the hidden assumptions."),
    ("U", "Unsupported claims flagged",
     "Which parts are asserted as fact but have no evidence? Mark confident-but-unproven claims."),
    ("D", "Data & sources checked",
     "Did the AI cite verifiable sources? Check for hallucinated facts, outdated data, and bias."),
    ("I", "Independent test designed",
     "What is the cheapest real-world test (interview, prototype, landing page) to verify it?"),
    ("T", "Translate to evidence",
     "After testing, what evidence strength (0–10) resulted? Update the ledger accordingly."),
]

AI_STATUS_OPTIONS = ["Unverified", "Verified", "Rejected", "Modified"]

AI_TOOL_AREAS = [
    "Customer Profile", "Value Proposition", "Business Model", "Assumptions",
    "Experiment design", "Pricing / economics", "Pivot reasoning", "Investor narrative", "Other",
]

# Structured, one-tap AUDIT picks — faster and more honest than free text.
AI_CLAIM_TYPES = ["Fact (says it's true)", "Prediction (says it will happen)",
                  "Opinion / suggestion"]
AI_DATA_SOURCES = ["No source given", "Cited a source but I haven't checked it",
                   "I checked the source myself"]

# How the AI was used (an indication of the kind of help).
AI_USE_TYPES = [
    "Brainstorm / generate options", "Draft or write text", "Summarize / explain",
    "Critique or check our work", "Analyze data / numbers", "Plan an experiment", "Other",
]

# AUDIT answered mostly by dropdown; text notes optional.
AI_AUDIT_ASSUMPTIONS = ["Not checked yet", "Some identified", "Listed the key assumptions"]
AI_AUDIT_UNSUPPORTED = ["Not checked yet", "None spotted", "A few unsupported claims",
                        "Mostly unsupported"]
AI_VERIFY_METHODS = ["Not planned yet", "Ask or observe real customers", "Run an experiment",
                     "Use evidence we already have", "Other"]

# Worked examples shown beside the two required quick-log fields.
AI_CLAIM_EXAMPLE = "e.g. 'Coffee shops will pay $49/mo for automated inventory forecasting.'"
AI_VERIFY_EXAMPLE = ("e.g. 'Ask 5 real shop owners for a paid pre-order — not the AI — and see "
                     "if ≥2 commit.'")

# --------------------------------------------------------------------------- #
# Decision Journal — a short, round-adaptive reflection. Three core prompts are
# always asked; one focus prompt changes with the round's topic; the rest are
# optional. Stems lower the blank-page cost.
# --------------------------------------------------------------------------- #
JOURNAL_CORE = [
    ("expected", "What did you expect to happen this round?", "We expected that…"),
    ("occurred", "What actually happened?", "What actually happened was…"),
    ("differently", "What will you do differently next round?", "Next round we'll…"),
]
# Round 1 has no prior round to assess ("how did you do?" is unanswerable), so the
# first round's core prompts are forward- and plan-oriented instead of retrospective.
JOURNAL_CORE_FIRST = [
    ("expected", "Going in, what do you expect to be the hardest part?",
     "The hardest part will be…"),
    ("occurred", "What did you actually do this round?", "This round we…"),
    ("differently", "What's your first move next round?", "Next round we'll start by…"),
]


def journal_core(round_no):
    """Round-aware core prompts — forward-looking in round 1, retrospective after."""
    return JOURNAL_CORE_FIRST if round_no <= 1 else JOURNAL_CORE
JOURNAL_OPTIONAL = [
    ("assumption", "Which assumption most shaped your decision? (optional)",
     "Our decision hinged on…"),
    ("overlooked", "What evidence did you overlook or discount? (optional)",
     "We may have ignored…"),
    ("contribution", "What did YOU personally contribute? (optional)", "I personally…"),
]
JOURNAL_FOCUS_BY_TOPIC = {
    "founder_formation": "How did your team's real skills and constraints shape your choices this round?",
    "opportunity_framing": "Why did you pick this opportunity over the others you considered?",
    "customer_discovery": "What surprised you most when you talked to real customers?",
    "customer_evidence": "What did behavioral evidence tell you that opinions didn't?",
    "value_creation": "Which customer pain or gain turned out to matter most — and how do you know?",
    "value_prop_fit": "Where did your value proposition NOT fit the customer, and what will you change?",
    "bmc_architecture": "Which business-model block is your weakest link right now, and why?",
    "assumption_testing": "Which assumption, if false, would break your venture — and did you test it?",
    "experiment_design": "Was your experiment cheap and decisive? What would make the next one sharper?",
    "market_testing": "What did the market actually show you (uptake, price, channel)?",
    "pivot_decisions": "Did the evidence say persevere or pivot — and did you listen?",
    "business_economics": "Do your unit economics work yet? Which number are you least sure about?",
    "scaling": "What has to be true for this to scale beyond your first customers?",
    "investment_readiness": "If an investor asked for your single strongest piece of evidence, what would you show?",
    "venture_market": "Across the whole venture, what's the transferable lesson you'll keep?",
}
JOURNAL_FOCUS_DEFAULT = "What did you learn this round that changes what you'll do next?"


def journal_focus(topic_key):
    return JOURNAL_FOCUS_BY_TOPIC.get(topic_key, JOURNAL_FOCUS_DEFAULT)


AI_PROTOCOL_SUMMARY = (
    "**Generative AI is allowed every round — but AI output is not evidence.** Treat any AI "
    "suggestion as founder opinion (strength 0) until it passes the **AUDIT** check and you "
    "translate it into real-world evidence:\n\n"
    "- **A — Assumptions surfaced**: what must be true for this to hold?\n"
    "- **U — Unsupported claims flagged**: which parts are confident but unproven?\n"
    "- **D — Data & sources checked**: hallucinations, stale data, bias?\n"
    "- **I — Independent test designed**: cheapest way to verify with real customers?\n"
    "- **T — Translate to evidence**: what strength did the real test produce?\n\n"
    "Log every AI use on the **AI Assist Log** page and mark it Verified only after a real test."
)

# --------------------------------------------------------------------------- #
# Engagement: team identity, badges, and the narrative arc
# --------------------------------------------------------------------------- #
TEAM_MASCOTS = ["🚀", "🦊", "🦉", "🐝", "🐙", "🦁", "🐢", "🦄", "🐉", "🦈",
                "🐬", "🦅", "🐺", "🐧", "🦖", "🌟", "⚡", "🔥", "🌱", "🧭"]
TEAM_COLORS = [
    ("Indigo", "#4f46e5"), ("Teal", "#0d9488"), ("Amber", "#d97706"), ("Rose", "#e11d48"),
    ("Emerald", "#059669"), ("Violet", "#7c3aed"), ("Sky", "#0284c7"), ("Slate", "#475569"),
    ("Fuchsia", "#c026d3"), ("Orange", "#ea580c"),
]
DEFAULT_TEAM_COLOR = "#4f46e5"
DEFAULT_TEAM_MASCOT = "🚀"

# Behavioral achievements — reward the habits we want, not just the score.
# (code, name, emoji, description)
BADGES = [
    ("first_evidence", "First Evidence", "🔍", "Logged your first piece of real evidence."),
    ("paying_customer", "First Paying Customer", "💳",
     "Logged a binding commitment — a customer paid, pre-ordered, or signed."),
    ("behavior_beats_opinion", "Behavior Beats Opinion", "👣",
     "Most of your evidence is behavioral (what customers did), not opinion."),
    ("killed_assumption", "Killed a Bad Assumption", "🎯",
     "Refuted an important assumption — productive failure is progress."),
    ("well_calibrated", "Well-Calibrated", "🎚️",
     "Your stated confidence matched how often you were actually right."),
    ("model_builder", "Model Builder", "🧩",
     "Built the core canvases of your business model."),
    ("course_corrector", "Course Corrector", "🔄",
     "Logged an evidence-based course correction (a mini-pivot)."),
    ("ai_auditor", "AI Auditor", "🤖",
     "Verified your AI use instead of trusting it — information literacy."),
    ("on_a_roll", "On a Roll", "🔥",
     "Committed your round on time three rounds in a row."),
    ("evidence_machine", "Evidence Machine", "📚",
     "Reached strong evidence coverage of your venture (60%+)."),
]
BADGE_BY_CODE = {b[0]: {"name": b[1], "emoji": b[2], "desc": b[3]} for b in BADGES}

# The investor persona who narrates the journey.
INVESTOR = {
    "name": "Vera Sloan",
    "title": "Managing Partner, Foundry Capital",
    "sign": "— Vera Sloan, Foundry Capital",
}

# The venture journey, told in phases. (name, emoji, one-line theme)
NARRATIVE_PHASES = [
    ("Seed", "🌱", "Every venture starts as a hunch. Find a real problem worth solving."),
    ("Discovery", "🔎", "Get out of the building — turn opinions into evidence."),
    ("Build", "🛠️", "Shape an offer that fits what customers actually do."),
    ("Traction", "📈", "Test the risky bets; let evidence, not love for the idea, steer you."),
    ("Pitch", "🎤", "Assemble the case — defend the model with proof, not persuasion."),
]

# Vera's in-character lines, chosen by how a team is doing.
INVESTOR_LINES = {
    "no_evidence": "I've read the pitch. Now show me a customer who did something about it — "
                   "opinions don't move me.",
    "opinion_heavy": "Lots of people 'love the idea.' Love is cheap. Find me behavior — someone "
                     "who paid, signed, or showed up.",
    "good_evidence": "Now we're talking. Real behavior beats a beautiful deck every time — keep "
                     "stacking evidence.",
    "risky_untested": "You're sitting on a bet that could sink this. Test the assumption that "
                      "scares you most, and do it cheaply.",
    "pivoted": "Changing your mind on evidence isn't failure — it's the job. Good.",
    "pitch_ready": "This is starting to look investable. Tighten the story: what you know, how "
                   "you know it, and what's still a bet.",
}

# Story-styled market-event openers by category (the event still names the assumption).
EVENT_STORY_INTRO = {
    "Customer": "Word from the field:",
    "Competitive": "A rival makes a move:",
    "Operational": "Reality intrudes:",
    "Regulatory & Ethical": "The rules shift:",
    "Financial": "The money side bites:",
}


def narrative_phase(rnd, total_rounds):
    """(index, name, emoji, theme) for the current round's story phase."""
    total = max(1, int(total_rounds))
    idx = min(len(NARRATIVE_PHASES) - 1, int((int(rnd) - 1) / total * len(NARRATIVE_PHASES)))
    name, emoji, theme = NARRATIVE_PHASES[idx]
    return idx, name, emoji, theme
