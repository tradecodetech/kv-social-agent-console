import random

# =========================
# VISUAL PHILOSOPHY
# =========================
# DALL-E 3 excels at: photography, abstract art, cinematic scenes, textures, light
# DALL-E 3 fails at:  text, charts, cards, infographics, logos, readable words
#
# RULE: Zero text on any image. Zero cards. Zero infographics.
# Every prompt uses one of three visual languages:
#   1. Cinematic Photography — real-world scenes, professional lighting
#   2. Abstract Art — color, form, texture, mood
#   3. Conceptual Macro — extreme close-up of objects/textures that imply meaning
#
# All prompts enforce: no text, no watermarks, no UI overlays, no people (unless
# artistically intentional), no logos, no stock-photo clichés.


# =========================
# TRADING — CINEMATIC MOODS
# =========================

TRADING_CINEMATIC = [
    # Patience / stillness
    "A lone figure standing at the edge of a glass skyscraper overlooking a vast city at dawn, "
    "fog below, absolute stillness, cinematic wide shot, cool blue and amber tones, "
    "hyperrealistic photography, no text, no logos",

    # Discipline / structure
    "Extreme close-up of a mechanical watch movement, golden gears frozen mid-tick, "
    "dark dramatic background, studio lighting, shallow depth of field, "
    "ultra-sharp detail, no text, no logos",

    # Risk / tension
    "A single chess piece — a king — standing alone on a vast dark marble board, "
    "dramatic side lighting, long shadow stretching behind it, "
    "cinematic composition, no text, no logos",

    # Waiting / calm before action
    "Storm clouds reflecting in a perfectly still lake at dusk, "
    "electric tension in the air, deep purple and steel blue palette, "
    "landscape photography, award-winning composition, no text, no logos",

    # Clarity / signal
    "Light breaking through a narrow gap between storm clouds over open ocean, "
    "single beam of golden light on dark water, "
    "cinematic photography, dramatic contrast, no text, no logos",

    # Conviction / structure
    "Aerial view of a perfectly geometric salt flat at sunrise, "
    "lone figure casting a long shadow, vast empty space, "
    "drone photography, muted earth tones, no text, no logos",
]

TRADING_ABSTRACT = [
    # Market flow
    "Abstract fluid art — deep navy and electric blue liquid forming wave patterns, "
    "metallic gold threads weaving through, high contrast, "
    "macro photography of ink in water, no text, no UI",

    # Discipline as structure
    "Minimalist abstract — thin precise lines converging at a single vanishing point "
    "on matte black canvas, cool silver and electric blue, architectural precision, "
    "fine art print quality, no text",

    # Volatility / calm
    "Abstract expressionist painting — chaotic brushstrokes in deep red and black "
    "suddenly becoming smooth and ordered in the center, "
    "gallery quality, dramatic lighting, no text",

    # Depth / patience
    "Macro photography of Japanese indigo fabric — deep wrinkles and folds creating "
    "valleys of shadow and ridges of light, abstract texture, "
    "extreme close-up, studio lighting, no text",

    # Signal vs noise
    "Abstract digital art — hundreds of faint gray lines with one sharp bright line "
    "cutting through them at a decisive angle, "
    "dark background, minimal palette, no text, no UI",
]


# =========================
# SYSTEMS / TECH — CONCEPTUAL
# =========================

SYSTEMS_CINEMATIC = [
    # Automation / structure
    "Overhead view of an intricate mechanical factory floor at night, "
    "blue and white lights, perfect geometric patterns of machinery, "
    "long exposure photography, no people, no text",

    # Constraint as power
    "A single river flowing through an impossibly narrow canyon, "
    "water forced into precise direction, aerial photography, "
    "teal and stone tones, cinematic, no text",

    # Systems thinking
    "Macro photograph of a circuit board — extreme close-up of copper traces "
    "glowing under UV light, deep teal and green, "
    "abstract industrial beauty, no text, no logos",

    # Precision
    "CNC machine carving perfect curves into dark metal, sparks frozen in time, "
    "dramatic industrial lighting, long exposure, "
    "cinematic photography, no text",

    # Discipline enforced by design
    "Aerial photograph of a perfectly pruned formal garden — geometric hedges, "
    "flawless symmetry, bird's eye view, "
    "soft morning light, no people, no text",
]

SYSTEMS_ABSTRACT = [
    "Abstract generative art — a web of precise nodes connected by glowing threads "
    "on a near-black background, electric green and white, "
    "data visualization aesthetic without actual data, no text",

    "Macro photography of carbon fiber weave — diagonal grid pattern, "
    "deep black with metallic sheen, extreme close-up texture, "
    "studio lighting, no text, no logos",

    "Abstract minimal — a single glowing dot at the intersection of two precise lines "
    "on dark background, long exposure light painting, "
    "electric blue, no text",
]


# =========================
# LAWN / LOCAL SERVICE — PHOTOGRAPHIC
# =========================

LAWN_CINEMATIC = [
    # Healthy lawn / result
    "Hyperrealistic photograph of a pristine residential lawn at golden hour, "
    "thick lush grass catching warm light, crisp mowing lines, "
    "shallow depth of field, suburban street softly blurred behind, "
    "professional photography, no text, no logos",

    # Before/after implied
    "Split-light scene — one half of a lawn dry and patchy, the other thick and green, "
    "natural daylight, photorealistic, no text, no overlays, no labels",

    # Early morning service
    "Dew on perfectly cut grass blades at dawn, extreme macro photography, "
    "each droplet refracting morning light, "
    "emerald and gold tones, no text, no logos",

    # Seasonal care
    "Residential backyard in early spring — fresh green growth emerging from dark soil, "
    "natural light, photorealistic, "
    "warm tones, professional landscape photography, no text",

    # Detail / craft
    "Close-up of a lawn mower blade cutting a perfect edge along a garden border, "
    "motion blur on blade, crisp grass detail, "
    "professional photography, no text, no logos",

    # Texture / nature
    "Macro photograph of individual grass blades after rain, "
    "water droplets catching light, deep green, "
    "extreme close-up, bokeh background, no text",
]

LAWN_ABSTRACT = [
    "Abstract overhead view of a freshly cut lawn — geometric mowing pattern "
    "creating diagonal stripes of light and dark green, "
    "drone photography, graphic composition, no text",

    "Macro photography of green grass texture — individual blades in sharp focus, "
    "soft earth below, natural daylight, "
    "minimal abstract quality, no text, no logos",
]


# =========================
# REAL ESTATE
# =========================

REALESTATE_CINEMATIC = [
    "Golden hour light falling across the facade of a clean modern home, "
    "manicured front yard, long shadows on the path, "
    "architectural photography, warm tones, no text, no logos",

    "Interior of an empty bright living room — tall windows, afternoon light pooling "
    "on hardwood floors, minimal furniture, "
    "architectural photography, clean composition, no text",

    "Aerial drone view of a quiet suburban neighborhood at sunrise, "
    "tree-lined streets, warm light, "
    "cinematic photography, no text, no logos",
]


# =========================
# FITNESS / HEALTH
# =========================

FITNESS_CINEMATIC = [
    "Empty professional gym at dawn — weight racks in perfect order, "
    "shafts of early light through high windows, "
    "cinematic photography, motivating atmosphere, no people, no text",

    "Macro photography of worn athletic shoe laces against concrete track, "
    "morning light, extreme close-up, "
    "minimal composition, no text, no logos",

    "Abstract motion blur of athletic training — implied speed and power, "
    "dark background, single light source, "
    "cinematic, no identifiable person, no text",
]


# =========================
# RESTAURANT / FOOD
# =========================

RESTAURANT_CINEMATIC = [
    "Professional food photography — artfully plated dish, natural window light, "
    "dark wooden table, shallow depth of field, "
    "editorial quality, no text, no logos",

    "Overhead flat-lay of fresh ingredients on dark marble, "
    "perfect composition, studio lighting, "
    "food editorial style, no text, no logos",

    "Steam rising from a bowl of food in warm amber light, "
    "dark moody background, cinematic, "
    "professional photography, no text",
]


# =========================
# SHARED STYLE SUFFIX
# All prompts get this appended to enforce quality
# =========================

QUALITY_SUFFIX = (
    " Ultra high resolution, professional photography or fine art quality. "
    "No text overlays. No watermarks. No UI elements. No logos. "
    "No stock photo clichés. Cinematic lighting."
)


# =========================
# MOOD MODIFIERS
# Randomly injected to add variety within a category
# =========================

MOOD_MODIFIERS = [
    "Shot on Hasselblad medium format.",
    "Leica cinematic aesthetic.",
    "Anamorphic lens flare.",
    "Long exposure, tripod-still.",
    "Golden hour directional light.",
    "Overcast diffused lighting, no harsh shadows.",
    "High contrast black and white conversion.",
    "Fujifilm Velvia color profile.",
    "Tack sharp foreground, creamy bokeh background.",
    "Moody desaturated tones with one saturated accent color.",
]

def _mood():
    return random.choice(MOOD_MODIFIERS)


# =========================
# UNIVERSAL BUILDER
# =========================

def build_visual_prompt(pillar: str, industry: str = "trading") -> str:
    """
    Build a DALL-E 3 image prompt appropriate for the page industry.

    Design principles:
    - ZERO text on images (DALL-E cannot render readable text)
    - ZERO cards, quote cards, infographics
    - Cinematic photography or fine art abstraction only
    - Every prompt ends with the quality suffix

    Args:
        pillar:   The content pillar/theme of the post (used for mood context only)
        industry: One of: trading, systems, tech, lawn, local, tax, realestate, fitness, restaurant

    Returns:
        A DALL-E 3 prompt string optimized for HD generation
    """
    ind = (industry or "trading").lower()

    # ── LAWN ──────────────────────────────────────────────────────────────────
    if any(x in ind for x in ["lawn", "landscap", "garden", "local"]):
        pool = LAWN_CINEMATIC + LAWN_ABSTRACT
        base = random.choice(pool)

    # ── SYSTEMS / TECH ────────────────────────────────────────────────────────
    elif any(x in ind for x in ["system", "tech", "code", "software", "automat"]):
        pool = SYSTEMS_CINEMATIC + SYSTEMS_ABSTRACT
        base = random.choice(pool)

    # ── REAL ESTATE ───────────────────────────────────────────────────────────
    elif any(x in ind for x in ["real", "estate", "realt", "propert", "house"]):
        base = random.choice(REALESTATE_CINEMATIC)

    # ── FITNESS ───────────────────────────────────────────────────────────────
    elif any(x in ind for x in ["fit", "health", "gym", "wellness", "sport"]):
        base = random.choice(FITNESS_CINEMATIC)

    # ── RESTAURANT / FOOD ─────────────────────────────────────────────────────
    elif any(x in ind for x in ["food", "restaur", "cafe", "kitchen", "dining"]):
        base = random.choice(RESTAURANT_CINEMATIC)

    # ── TRADING / FINANCE (default) ───────────────────────────────────────────
    else:
        pool = TRADING_CINEMATIC + TRADING_ABSTRACT
        base = random.choice(pool)

    return base + f" {_mood()}" + QUALITY_SUFFIX


# =========================
# Legacy alias
# =========================
def build_lawn_visual_prompt(pillar: str) -> str:
    return build_visual_prompt(pillar, industry="lawn")