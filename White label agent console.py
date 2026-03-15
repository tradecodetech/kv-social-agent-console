import random

# =========================
# VERSION TRACKING
# =========================
PROMPT_VERSION = "v1.3-operator"  # 🔥 NEW: Track for A/B testing


# =========================
# CONTENT PILLARS
# =========================

DISCIPLINE_PILLARS = [
    "discipline when nothing is happening",
    "restraint in calm environments",
    "execution without emotional reward",
    "patience that feels uncomfortable",
    "risk hiding inside stability",
    "consistency across regime shifts",
]

TRADING_PILLARS = [
    "markets rewarding bad behavior first",
    "quiet price masking structural risk",
    "waiting while others chase movement",
    "reaction outperforming prediction",
    "stories replacing probabilities",
]

SYSTEMS_PILLARS = [
    "rules replacing instinct under pressure",
    "systems built after repeated mistakes",
    "automation enforcing discipline",
    "structure removing emotional override",
    "constraints outperforming flexibility",
    "filters mattering more than signals",
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
]

# =========================
# HOOK ROTATION (ANTI-GENERIC)
# =========================

HOOK_PATTERNS = [
    "Most traders believe {belief}.",
    "The mistake traders keep repeating is {belief}.",
    "What looks like discipline is often just {belief}.",
    "Traders don't fail because of strategy — they fail because {belief}.",
    "The market isn't punishing traders. It's exposing {belief}.",
]

BELIEF_FRAGMENTS = [
    "movement equals opportunity",
    "being active equals being productive",
    "confidence means certainty",
    "waiting is wasted time",
    "more trades mean more progress",
]

def build_hook():
    pattern = random.choice(HOOK_PATTERNS)
    belief = random.choice(BELIEF_FRAGMENTS)
    return pattern.format(belief=belief)


LAWN_HOOK_PATTERNS = [
    "Most lawns don't fail from neglect — they fail from {belief}.",
    "The fastest way to ruin a lawn is {belief}.",
    "If your lawn looks worse after you mow, it's usually {belief}.",
    "A lot of 'lawn problems' are really just {belief}.",
    "The mistake I see most homeowners repeat is {belief}.",
]

LAWN_BELIEF_FRAGMENTS = [
    "cutting it too short when it's hot",
    "watering a little bit every day",
    "mowing wet grass and calling it 'fine'",
    "waiting until it's bad before doing anything",
    "changing too many things at once",
    "thinking weeds are the problem when the grass is stressed",
]

def build_lawn_hook():
    pattern = random.choice(LAWN_HOOK_PATTERNS)
    belief = random.choice(LAWN_BELIEF_FRAGMENTS)
    return pattern.format(belief=belief)

# =========================
# VIRALITY ROTATION (CONTROLLED)
# =========================

CONTENT_STYLES = {
    "standard": 0.65,
    "short_punch": 0.25,
    "emoji_minimal": 0.10,
}

STYLE_MODIFIERS = {
    "standard": "",
    "short_punch": """
Additional rules:
- 1–2 lines only
- Sharp, declarative statements
- No explanation
""",
    "emoji_minimal": """
Additional rules:
- 1 emoji MAX (⚠️ 🧠 ⏳ 📉)
- Emoji only at line start or end
- Still no hype or motivation
""",
}

def choose_content_style():
    styles = list(CONTENT_STYLES.keys())
    weights = list(CONTENT_STYLES.values())
    return random.choices(styles, weights=weights)[0]


LAWN_CONTENT_STYLES = {
    "standard": 0.60,
    "short_punch": 0.25,
    "emoji_minimal": 0.10,
    "cta_soft": 0.05,
}

LAWN_STYLE_MODIFIERS = {
    "standard": "",
    "short_punch": """
Additional rules:
- 1–2 lines only
- Blunt, practical statements
- No explanation
""",
    "emoji_minimal": """
Additional rules:
- 1 emoji MAX (🌱 ☀️ 💧 ⚠️)
- Emoji only at line start or end
- No hype
""",
    "cta_soft": """
Additional rules:
- Include ONE soft local CTA on the last line (no hype).
- CTA should be informational, not salesy.
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
]

# =========================
# GLOBAL VOICE & AUTHORITY RULES (TRADING/SYSTEMS)
# =========================

TONE_RULES = """
Write as a calm market operator with real responsibility experience.
No hype. No bravado. No promises.
Educate through observation, not instruction.
Assume the reader is intelligent but misinformed by surface-level trading content.
"""

VOICE_GUIDELINES = """
- Speak from lived exposure, not theory
- Never sell outcomes or guarantees
- Prefer insight over motivation
- Avoid emotional language
- Avoid hashtags
- Avoid calls to action
"""

CONTENT_FILTERS = """
Allowed themes:
- trader psychology
- outcome lag vs competence
- drawdowns and timing
- risk-first thinking
- process over optics
- lessons learned from responsibility

Disallowed themes:
- lifestyle flexing
- profit promises
- daily PnL focus
- signal selling language
- influencer-style encouragement
"""

STYLE_CONSTRAINTS = """
- Short paragraphs (1–4 lines depending on style)
- Declarative statements
- No hashtags
- No over-explaining
"""

CLOSING_RULE = """
End with an observation, not advice.
Do not tell the reader what to do.
Let the insight stand on its own.
"""

AUDIENCE_LAYERING = """
Primary reader: active day trader seeking consistency.
Secondary reader: capital-aware operator focused on longevity.

The post should:
- Look tactical on the surface
- Signal discipline and risk control underneath
- Avoid hype or selling
"""

# LAWN VOICE
LAWN_TONE_RULES = """
Write like a local lawn care pro who does this weekly.
Practical, calm, straightforward.
No hype. No exaggeration. No 'guru' energy.
Educate through cause-and-effect and timing.
"""

LAWN_STYLE_CONSTRAINTS = """
- 2–4 lines (unless short_punch)
- Plain language
- No hashtags
- No over-explaining
- No aggressive selling
"""

LAWN_CLOSING_RULE = """
End with a practical observation (not a lecture).
If CTA is included, keep it soft and local.
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

You are an experienced market operator.

Write ONE Facebook post.
Tone: calm authority, observant, precise.

STRICT RULES:
- Do NOT give trade signals
- Do NOT mention entries, exits, or prices
- No hype or motivation

STRUCTURE RULES:
- Open with the provided hook
- Focus on behavior before price
- Every line must add information
- Leave the tension unresolved

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

You are a trader who built systems because discretion failed under pressure.

Write ONE Facebook post.
Tone: analytical, grounded, quietly assertive.

STRICT RULES:
- No tech buzzwords
- Do NOT mention tools, platforms, or languages
- Do NOT give trade signals

STRUCTURE RULES:
- Open with the provided hook
- Contrast instinct vs structure
- Frame systems as behavioral protection
- Imply structure isn't for everyone

Opening hook:
{hook}

Theme: {pillar}

{style_modifier}
"""

CONTEE_LAWN_PROMPT = """
{tone}
{style}
{closing}

You are Contee's Lawn Care.

Write ONE Facebook post.
Tone: practical, calm, professional.
Goal: helpful lawn tip that makes homeowners go "oh… that's why."

STRICT RULES:
- No hashtags
- No exaggerated claims
- No fear-mongering
- Avoid technical overload

STRUCTURE RULES:
- Open with the provided hook
- Explain cause → effect in plain language
- Keep it local/seasonal in spirit (no need to name a city)
- End with a practical observation

Opening hook:
{hook}

Theme: {pillar}

{style_modifier}

{optional_cta}
"""

# =========================
# MODE SELECTION (TRADING/SYSTEMS)
# =========================

def choose_mode(mode_weights: dict) -> str:
    d = int(mode_weights.get("discipline", 60))
    t = int(mode_weights.get("trading", 40))
    return random.choices(["discipline", "trading"], weights=[d, t])[0]

def choose_pillar(mode: str, is_systems_page: bool) -> str:
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
    🔥 PRODUCTION-READY prompt builder.
    
    Handles:
    - Trading pages (KV)
    - Systems pages (TradeCodeTech)
    - Lawn care pages (Contee's)
    - Hook rotation
    - Style variation
    - CTA logic
    
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

    # LAWN FLOW
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
            hook=hook,
            pillar=pillar,
            style_modifier=style_modifier,
            optional_cta=optional_cta
        )

        return prompt, "lawn", pillar

    # TRADING/SYSTEMS FLOW
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
        hook=hook,
        pillar=pillar,
        style_modifier=style_modifier
    )

    if is_systems_page:
        prompt = TRADE_CODE_TECH_PROMPT.format(**base_args)
    else:
        prompt = KV_TRADING_PROMPT.format(**base_args)

    return prompt, mode, pillar
