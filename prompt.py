import random

# =========================
# VERSION TRACKING
# =========================
PROMPT_VERSION = "v3.1-short"  # Hard length limits + visual support all industries


# =========================
# CONTENT PILLARS — TRADING / DISCIPLINE
# =========================

DISCIPLINE_PILLARS = [
    "discipline when nothing is happening",
    "restraint in calm environments",
    "execution without emotional reward",
    "patience that feels uncomfortable",
    "risk hiding inside stability",
    "consistency across regime shifts",
    "sitting in cash while the market runs",
    "the cost of acting before confirmation",
    "boredom as a feature, not a bug",
    "protecting mental capital between setups",
]

TRADING_PILLARS = [
    "markets rewarding bad behavior first",
    "quiet price masking structural risk",
    "waiting while others chase movement",
    "reaction outperforming prediction",
    "stories replacing probabilities",
    "why most traders quit during the wrong phase",
    "the performance gap between knowing and doing",
    "how drawdowns reveal real risk tolerance",
    "why winning trades build the worst habits",
    "the difference between a bad trade and bad process",
]

SYSTEMS_PILLARS = [
    "rules replacing instinct under pressure",
    "systems built after repeated mistakes",
    "automation enforcing discipline",
    "structure removing emotional override",
    "constraints outperforming flexibility",
    "filters mattering more than signals",
    "why removing decisions is a skill",
    "the compounding effect of consistent process",
    "how one emotional override destroys a system",
    "building for the worst day, not the average one",
]

VIRAL_PILLARS = [
    "the trader who consistently loses is often doing everything 'right'",
    "why the most confident traders blow up first",
    "the uncomfortable truth about trading journals",
    "what separates a $10k account from a $1M account (it's not skill)",
    "why paper trading never prepares you for real money",
    "the one habit that kills most promising traders",
    "why your best month is your most dangerous month",
    "the counterintuitive reason profitable traders feel bored",
]

LAWN_PILLARS = [
    "seasonal mowing mistakes that damage lawns",
    "watering habits that look right but hurt grass",
    "why weeds explode after rain and warm nights",
    "how mowing height affects heat and drought stress",
    "the hidden reason patchy lawns keep coming back",
    "simple weekly routines that prevent expensive fixes",
    "why lawns decline even when you're trying",
    "what to do after a freeze or sudden temperature swing",
    "why grass color changes throughout the season",
    "the real reason your neighbor's lawn looks better",
    "what fertilizer timing actually does to your lawn",
    "how foot traffic creates dead zones over time",
]


# =========================
# HOOK ROTATION — TRADING (VIRAL-OPTIMIZED)
# =========================

HOOK_PATTERNS = [
    # Classic operator voice
    "Most traders believe {belief}.",
    "The mistake traders keep repeating is {belief}.",
    "What looks like discipline is often just {belief}.",
    "Traders don't fail because of strategy — they fail because {belief}.",
    "The market isn't punishing traders. It's exposing {belief}.",
    # Curiosity/counter-intuitive
    "Nobody talks about {belief}.",
    "The best traders I've watched all shared one thing: they stopped believing {belief}.",
    "Here's what they don't tell you about {belief}:",
    "I used to believe {belief}. Then I watched it cost someone everything.",
    "Unpopular opinion: {belief} is destroying more accounts than bad setups are.",
    # Story openers
    "I watched a trader do everything right and still blow up. The reason: {belief}.",
    "The account that goes to zero fastest isn't run by the worst trader. It's run by someone who still believes {belief}.",
    # Direct challenge
    "If you still believe {belief}, the market hasn't finished with you yet.",
    "Ask any trader who's been around 10 years. They'll all say the same thing about {belief}.",
]

BELIEF_FRAGMENTS = [
    "movement equals opportunity",
    "being active equals being productive",
    "confidence means certainty",
    "waiting is wasted time",
    "more trades mean more progress",
    "a good setup makes a trade safe",
    "you can think your way out of a losing position",
    "consistency is about winning streaks",
    "a bigger account means a better trader",
    "the next trade will fix the last one",
    "discipline is a personality trait, not a system",
    "the best traders feel sure before they enter",
]

def build_hook():
    pattern = random.choice(HOOK_PATTERNS)
    belief = random.choice(BELIEF_FRAGMENTS)
    return pattern.format(belief=belief)


# =========================
# HOOK ROTATION — LAWN (VIRAL-OPTIMIZED)
# =========================

LAWN_HOOK_PATTERNS = [
    "Most lawns don't fail from neglect — they fail from {belief}.",
    "The fastest way to ruin a lawn is {belief}.",
    "If your lawn looks worse after you mow, it's usually {belief}.",
    "A lot of 'lawn problems' are really just {belief}.",
    "The mistake I see most homeowners repeat is {belief}.",
    "Nobody tells you this when you buy a house, but {belief} kills more lawns than drought does.",
    "Your neighbor's lawn isn't healthier because they work harder. It's because they stopped {belief}.",
    "I've seen lawns bounce back from disease, drought, and freeze. The ones that don't bounce back? {belief}.",
    "If you've been trying everything and your lawn still struggles, it's probably {belief}.",
]

LAWN_BELIEF_FRAGMENTS = [
    "cutting it too short when it's hot",
    "watering a little bit every day",
    "mowing wet grass and calling it 'fine'",
    "waiting until it's bad before doing anything",
    "changing too many things at once",
    "thinking weeds are the problem when the grass is stressed",
    "mowing on the same schedule regardless of growth",
    "skipping aeration because the lawn looks fine",
    "fertilizing during a drought",
    "ignoring thatch buildup until it's too late",
]

def build_lawn_hook():
    pattern = random.choice(LAWN_HOOK_PATTERNS)
    belief = random.choice(LAWN_BELIEF_FRAGMENTS)
    return pattern.format(belief=belief)


# =========================
# CONTENT STYLES — TRADING (VIRAL-REBALANCED)
# =========================

CONTENT_STYLES = {
    "viral_punch":   0.45,   # Counter-intuitive 1-3 lines, shareable
    "short_punch":   0.35,   # Sharp declarative, no explanation
    "standard":      0.10,   # Full developed thought (rare)
    "thread_style":  0.05,   # Numbered points format (rare)
    "emoji_minimal": 0.05,   # Single emoji, restrained
}

STYLE_MODIFIERS = {
    "standard": """
Additional rules:
- HARD LIMIT: 4 lines maximum. If it's longer, cut it.
- No intro sentence. Start with the insight.
- Every line must be necessary — if removing it changes nothing, cut it.
""",

    "short_punch": """
Additional rules:
- HARD LIMIT: 1–2 lines. That's it.
- Sharp, declarative. One statement.
- No explanation, no follow-up, no softening.
- If you write a third line, delete it.
""",

    "viral_punch": """
Additional rules:
- HARD LIMIT: 1–3 lines MAXIMUM. Non-negotiable.
- One counter-intuitive insight. Drop it. Stop writing.
- It must make someone think "I never thought of it that way" or "nobody says this."
- Zero setup. Zero follow-up. Zero explanation.
- If you feel the urge to add another line — don't.
""",

    "thread_style": """
Additional rules:
- HARD LIMIT: Hook + 3 numbered points + 1 closing line. Nothing more.
- Each numbered point: ONE sentence, max 10 words.
- No fluff between points.
""",

    "emoji_minimal": """
Additional rules:
- HARD LIMIT: 1–2 lines.
- 1 emoji MAX (⚠️ 🧠 ⏳ 📉 🔇). At start or end only.
- No hype, no motivation.
""",
}

def choose_content_style():
    styles = list(CONTENT_STYLES.keys())
    weights = list(CONTENT_STYLES.values())
    return random.choices(styles, weights=weights)[0]


# =========================
# CONTENT STYLES — LAWN (VIRAL-REBALANCED)
# =========================

LAWN_CONTENT_STYLES = {
    "viral_punch":   0.40,
    "short_punch":   0.35,
    "standard":      0.10,
    "emoji_minimal": 0.05,
    "cta_soft":      0.10,
}

LAWN_STYLE_MODIFIERS = {
    "standard": """
Additional rules:
- HARD LIMIT: 3–4 lines maximum.
- Start with the cause. End with the effect. Nothing in between that isn't necessary.
""",

    "short_punch": """
Additional rules:
- HARD LIMIT: 1–2 lines. One blunt practical statement.
- No explanation. If someone has to ask "why?" — good.
""",

    "viral_punch": """
Additional rules:
- HARD LIMIT: 1–3 lines MAXIMUM.
- One lawn fact that makes a homeowner say "wait, I've been doing that wrong."
- Shareable — the kind of thing someone texts their neighbor.
- Drop the insight. Stop writing. Do not add another line.
""",

    "emoji_minimal": """
Additional rules:
- HARD LIMIT: 1–2 lines.
- 1 emoji MAX (🌱 ☀️ 💧 ⚠️ ✂️). At start or end only.
""",

    "cta_soft": """
Additional rules:
- HARD LIMIT: 2–3 lines + 1 CTA line.
- CTA is the last line only. Soft, local, not salesy.
""",
}

def choose_lawn_content_style():
    styles = list(LAWN_CONTENT_STYLES.keys())
    weights = list(LAWN_CONTENT_STYLES.values())
    return random.choices(styles, weights=weights)[0]


LAWN_CTAS = [
    "If you want consistent care, we handle weekly maintenance and cleanups.",
    "If you're local and want help, Contee's Lawn Care does weekly service + cleanups.",
    "Most fixes are timing + consistency — that's what we manage for homeowners.",
    "If you want a quote, check the website or DM 'LAWN'.",
    "We service this area weekly. Reach out if you want consistent lawn care handled.",
]


# =========================
# GLOBAL VOICE & AUTHORITY RULES — TRADING/SYSTEMS
# =========================

TONE_RULES = """
Write as a calm, experienced market operator with real risk responsibility.
No hype. No bravado. No promises.
Educate through sharp observation — not instruction or motivation.
Assume the reader is intelligent but shaped by surface-level trading content.
"""

VOICE_GUIDELINES = """
- Speak from lived exposure, not theory
- Never sell outcomes or guarantees
- Prefer insight over motivation
- Avoid emotional language
- Avoid hashtags
- Avoid calls to action unless the style explicitly asks for one
- Write the kind of post that makes a real trader nod, not clap
"""

CONTENT_FILTERS = """
Allowed themes:
- trader psychology and behavioral patterns
- outcome lag vs actual competence
- drawdowns, timing, and sequence risk
- risk-first thinking
- process over optics
- lessons visible only from years of exposure
- the counterintuitive mechanics of markets
- what separates traders who survive from those who don't

Disallowed themes:
- lifestyle flexing or wealth signaling
- profit promises or performance claims
- daily PnL focus
- signal selling language
- influencer-style encouragement
- generic motivation ("stay consistent", "trust the process")
"""

STYLE_CONSTRAINTS = """
- Follow the style's HARD LIMIT on length — this is not optional
- Declarative statements only
- No hashtags
- No over-explaining
- No intro sentences ("In the world of trading..." / "When it comes to...")
- Every line must earn its place — if it doesn't add new information, delete it
- When in doubt, write less
"""

CLOSING_RULE = """
End with an observation, not advice.
Do not tell the reader what to do.
Do not moralize or wrap it up neatly.
Let the insight sit with them.
The best ending leaves a slight tension unresolved.
"""

VIRALITY_RULES = """
Virality comes from truth, not noise.
The post should make someone think "nobody says this out loud."
Counter-intuitive > conventional wisdom.
Specific > general.
Observational > prescriptive.
One strong insight shared well > three weak ones listed.
"""

AUDIENCE_LAYERING = """
Primary reader: active trader trying to become consistent.
Secondary reader: systems-aware operator focused on longevity.

The post should:
- Look tactical on the surface
- Signal deep discipline underneath
- Avoid anything that sounds like a course ad
- Be something a real trader would screenshot and send to another trader
"""


# =========================
# LAWN VOICE
# =========================

LAWN_TONE_RULES = """
Write like a local lawn care pro who does this work every week.
Practical, calm, straight to the point.
No hype. No exaggeration. No 'guru' energy.
Educate through cause-and-effect and timing.
Sound like someone who's seen every lawn problem — not impressed, just informed.
"""

LAWN_STYLE_CONSTRAINTS = """
- 2–4 lines (unless short_punch or viral_punch)
- Plain language — no jargon
- No hashtags
- No over-explaining
- No aggressive selling
- If it's something a homeowner could tell a neighbor, it's the right length
"""

LAWN_CLOSING_RULE = """
End with a practical observation (not a lecture).
The reader should feel like they got a useful tip, not a sales pitch.
If CTA is included, keep it soft, local, and last.
"""

LAWN_VIRALITY_RULES = """
Virality for local service = word-of-mouth triggers.
Make the tip so useful or specific that a homeowner shares it with their neighbor.
The "aha" moment: they've been doing something wrong without knowing it.
Seasonal specificity beats generic advice every time.
"""


# =========================
# PROMPT TEMPLATES
# =========================

KV_TRADING_PROMPT = """
{tone}
{voice}
{filters}
{style}
{closing}
{audience}
{virality}

You are an experienced market operator writing for a trading audience on Facebook.

Write ONE Facebook post.
Tone: calm authority, observant, precise.

STRICT RULES:
- Do NOT give trade signals
- Do NOT mention entries, exits, or prices
- No hype or motivation
- No hashtags

STRUCTURE RULES:
- Open with the provided hook
- Focus on behavior before price
- Every line must add information
- Leave the tension unresolved at the end
- Write something a serious trader would screenshot

Opening hook:
{hook}

Theme: {pillar}

{style_modifier}
"""

TRADE_CODE_TECH_PROMPT = """
{tone}
{voice}
{filters}
{style}
{closing}
{audience}
{virality}

You are a trader who built systems because discretion failed under pressure.

Write ONE Facebook post.
Tone: analytical, grounded, quietly assertive.

STRICT RULES:
- No tech buzzwords
- Do NOT mention tools, platforms, or languages
- Do NOT give trade signals
- No hashtags

STRUCTURE RULES:
- Open with the provided hook
- Contrast instinct vs structure
- Frame systems as behavioral protection, not optimization
- Imply that systems aren't for everyone — only for those who've hit the wall
- Write something a builder-mindset operator would share

Opening hook:
{hook}

Theme: {pillar}

{style_modifier}
"""

CONTEE_LAWN_PROMPT = """
{tone}
{style}
{closing}
{virality}

You are Contee's Lawn Care — a local lawn service with weekly hands-on experience.

Write ONE Facebook post.
Tone: practical, calm, professional.
Goal: a lawn tip so useful the homeowner shares it with their neighbor.

STRICT RULES:
- No hashtags
- No exaggerated claims
- No fear-mongering
- Avoid technical overload
- Sound like advice from a neighbor who does this for a living

STRUCTURE RULES:
- Open with the provided hook
- Explain cause → effect in plain language
- Keep it local and seasonal in spirit
- End with a practical observation (not a lecture)

Opening hook:
{hook}

Theme: {pillar}

{style_modifier}

{optional_cta}
"""


# =========================
# MODE SELECTION
# =========================

def choose_mode(mode_weights: dict) -> str:
    d = int(mode_weights.get("discipline", 60))
    t = int(mode_weights.get("trading", 40))
    return random.choices(["discipline", "trading"], weights=[d, t])[0]


def choose_pillar(mode: str, is_systems_page: bool) -> str:
    # 20% chance of pulling from viral pillars for higher shareability
    if random.random() < 0.20:
        return random.choice(VIRAL_PILLARS)
    if is_systems_page:
        return random.choice(SYSTEMS_PILLARS)
    if mode == "trading":
        return random.choice(TRADING_PILLARS)
    return random.choice(DISCIPLINE_PILLARS)


# =========================
# PROMPT BUILDER
# =========================

def build_prompt(mode_weights: dict, style_tags: list[str], page_name: str):
    """
    v3.0-viral prompt builder.

    Handles:
    - Trading pages (KV)
    - Systems pages (TradeCodeTech)
    - Lawn care pages (Contee's)
    - Hook rotation (expanded, virality-optimized)
    - Style variation (new viral_punch + thread_style)
    - Virality rules injected into every prompt

    Returns:
        (prompt, mode, pillar) tuple
    """
    name = (page_name or "").lower()
    tags = " ".join(style_tags or []).lower()

    is_systems_page = (
        "systems" in tags
        or "tech" in name
        or "code" in name
    )

    is_lawn_page = (
        "lawn" in name
        or "landscap" in name
        or "contee" in name
    )

    # ── LAWN FLOW ──────────────────────────────────────────────────────────────
    if is_lawn_page:
        pillar = random.choice(LAWN_PILLARS)
        hook = build_lawn_hook()

        content_style = choose_lawn_content_style()
        style_modifier = LAWN_STYLE_MODIFIERS[content_style]

        optional_cta = ""
        if content_style == "cta_soft":
            optional_cta = f"\nOptional last line (include once):\n{random.choice(LAWN_CTAS)}"
        else:
            optional_cta = "No CTA."

        prompt = CONTEE_LAWN_PROMPT.format(
            tone=LAWN_TONE_RULES,
            style=LAWN_STYLE_CONSTRAINTS,
            closing=LAWN_CLOSING_RULE,
            virality=LAWN_VIRALITY_RULES,
            hook=hook,
            pillar=pillar,
            style_modifier=style_modifier,
            optional_cta=optional_cta
        )

        return prompt, "lawn", pillar

    # ── TRADING / SYSTEMS FLOW ─────────────────────────────────────────────────
    mode = choose_mode(mode_weights)
    pillar = choose_pillar(mode, is_systems_page)
    hook = build_hook()

    content_style = choose_content_style()
    style_modifier = STYLE_MODIFIERS[content_style]

    base_args = dict(
        tone=TONE_RULES,
        voice=VOICE_GUIDELINES,
        filters=CONTENT_FILTERS,
        style=STYLE_CONSTRAINTS,
        closing=CLOSING_RULE,
        audience=AUDIENCE_LAYERING,
        virality=VIRALITY_RULES,
        hook=hook,
        pillar=pillar,
        style_modifier=style_modifier
    )

    if is_systems_page:
        prompt = TRADE_CODE_TECH_PROMPT.format(**base_args)
    else:
        prompt = KV_TRADING_PROMPT.format(**base_args)

    return prompt, mode, pillar
