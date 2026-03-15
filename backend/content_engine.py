"""
KV Systems — Content Engine
Handles all AI content generation beyond basic posting:
- Viral / high-engagement posts
- Lead generation posts
- 30-day content calendars
- AI comment reply suggestions
- Industry-specific content types
"""

import random
from openai import OpenAI
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMP = float(os.getenv("OPENAI_TEMPERATURE", "0.85"))


# =============================================================================
# INDUSTRY PILLARS
# =============================================================================

INDUSTRY_PILLARS = {
    "trading": [
        "discipline over emotion",
        "risk management and position sizing",
        "reading market structure",
        "psychology of losing trades",
        "patience as a trading edge",
        "the myth of predicting markets",
        "journaling and reviewing performance",
        "systems vs intuition in trading",
        "macro awareness and context",
        "separating outcome from process",
    ],
    "systems": [
        "automation saves time and reduces errors",
        "building systems before you need them",
        "why most manual processes fail at scale",
        "integrating tools for a seamless workflow",
        "the cost of doing it manually",
        "digital infrastructure for small business",
        "AI tools that actually work",
        "custom vs off-the-shelf solutions",
        "cybersecurity basics every business needs",
        "how to evaluate a tech vendor",
    ],
    "lawn": [
        "seasonal lawn care timing",
        "mowing height and frequency",
        "watering deeply vs watering often",
        "fertilization schedules by grass type",
        "weed prevention before it starts",
        "aeration and overseeding benefits",
        "signs your lawn is stressed",
        "common lawn care mistakes homeowners make",
        "soil health and pH balance",
        "choosing the right grass type for your region",
    ],
    "restaurant": [
        "daily specials and limited-time offers",
        "behind-the-scenes kitchen stories",
        "ingredients sourced locally",
        "staff highlights and team culture",
        "customer favorites and nostalgia",
        "seasonal menu changes",
        "food safety and quality commitment",
        "catering and event dining options",
        "online ordering and convenience",
        "community involvement and local support",
    ],
    "fitness": [
        "form over weight every time",
        "consistency beats intensity",
        "nutrition fundamentals for everyday people",
        "rest and recovery as part of training",
        "mindset shifts for long-term results",
        "beginner mistakes to avoid",
        "why most diets fail",
        "building sustainable habits",
        "tracking progress without obsession",
        "community and accountability",
    ],
    "realestate": [
        "buying vs renting in today's market",
        "how to price your home correctly",
        "what buyers notice on first walkthrough",
        "negotiation tactics that work",
        "the real cost of waiting to buy",
        "staging and curb appeal for faster sales",
        "understanding mortgage rates and timing",
        "neighborhood trends and investment value",
        "common seller mistakes",
        "first-time homebuyer guidance",
    ],
    "local": [
        "why local businesses outperform chains on service",
        "the value of knowing your customers by name",
        "community involvement and giving back",
        "consistency as a brand promise",
        "referrals and word-of-mouth growth",
        "responding to reviews professionally",
        "the story behind the business",
        "what sets us apart from the competition",
        "seasonal promotions and special offers",
        "transparent pricing and no-surprise billing",
    ],
    "tax": [
        "year-round tax planning vs last-minute scrambling",
        "deductions most small business owners miss",
        "quarterly estimated taxes explained",
        "bookkeeping basics that save money at tax time",
        "what triggers an IRS audit",
        "how to choose the right business structure",
        "tax advantages of retirement accounts",
        "home office deduction rules",
        "self-employment tax planning",
        "working with a CPA vs DIY tax software",
    ],
}


# =============================================================================
# INDUSTRY VOICE
# =============================================================================

INDUSTRY_VOICE = {
    "trading":    "calm authority, no hype, grounded in process, speaks like a practitioner not a salesman",
    "systems":    "builder mindset, analytical, direct, talks to business owners not developers",
    "lawn":       "local professional, practical, educational, neighborly without being folksy",
    "restaurant": "warm, local, food-passionate, inviting and community-driven",
    "fitness":    "motivating but honest, evidence-based, no toxic positivity, real talk about hard work",
    "realestate": "trusted advisor, professional, aspirational but grounded, numbers-aware",
    "local":      "community-focused, friendly, reliable, speaks like a neighbor who does great work",
    "tax":        "professional, reassuring, detail-oriented, demystifies the complex without being condescending",
}


# =============================================================================
# VIRAL FORMATS
# =============================================================================

VIRAL_FORMATS = [
    "engagement_question",
    "myth_bust",
    "hot_take",
    "poll_prompt",
    "discussion_starter",
    "fill_in_blank",
    "agree_disagree",
]


# =============================================================================
# ENGAGEMENT STARTERS
# =============================================================================

ENGAGEMENT_STARTERS = {
    "trading": [
        "What's the one trading rule you had to learn the hard way?",
        "Biggest mistake new traders make — drop it below.",
        "If you could go back and tell your first-year trading self one thing, what would it be?",
        "What's your go-to indicator for confirming a setup? (or do you not use them?)",
        "Hot take: most people lose money in the market because of psychology, not strategy. Agree or disagree?",
    ],
    "systems": [
        "What's one manual process in your business you'd automate tomorrow if you could?",
        "Best tool you've added to your workflow in the last year — what is it?",
        "How many hours a week does your team spend on tasks that could be automated?",
        "Biggest tech mistake you see small businesses make?",
        "What's holding you back from automating more of your operations?",
    ],
    "lawn": [
        "What's the one lawn care mistake you see every summer on your street?",
        "How often are you actually supposed to water your lawn — and how often do you?",
        "What grass type does your lawn have? Most homeowners don't know.",
        "Best lawn tip you ever got — what was it?",
        "When was the last time you aerated your lawn? (No judgment — most people never have.)",
    ],
    "restaurant": [
        "What's one dish you'd drive across town for?",
        "Best meal you've had at a local restaurant this year — where was it?",
        "What do you look for first when you sit down at a restaurant?",
        "Tell us your go-to order here — we want to know our regulars.",
        "What's one food you thought you'd never like until you tried it done right?",
    ],
    "fitness": [
        "What habit has had the biggest impact on your fitness — and it doesn't have to be exercise?",
        "Biggest fitness myth you used to believe?",
        "What does your warm-up routine actually look like?",
        "How long did it take before working out felt like a habit instead of a chore?",
        "What's one thing you wish someone had told you when you started training?",
    ],
    "realestate": [
        "What's the one thing you looked for in a home that you'd change now that you've lived in it?",
        "For buyers right now — are you waiting for rates to drop or moving anyway?",
        "What do sellers underestimate most about the selling process?",
        "First-time homebuyers: what's the one question you wish you'd asked before closing?",
        "What's a deal-breaker when touring a home that most buyers don't talk about?",
    ],
    "local": [
        "What do you look for in a local service business before you hire them?",
        "Biggest red flag when hiring a contractor or service provider?",
        "How do you find businesses you trust in your area?",
        "What would make you a loyal customer for life?",
        "Tell us — what's the last local business that genuinely impressed you?",
    ],
    "tax": [
        "What's your biggest question about taxes as a small business owner?",
        "Did you know this deduction was available? Most people don't.",
        "When do you usually start thinking about taxes — January or April 14th?",
        "What's one tax mistake you made early in your business that you'd warn others about?",
        "Quarterly taxes: do you have a system, or is it always a scramble?",
    ],
}


# =============================================================================
# LEAD TEMPLATES
# =============================================================================

LEAD_TEMPLATES = {
    "trading": [
        "Comment [KEYWORD] below and we'll send you our free [SERVICE] breakdown — no pitch, just content.",
        "Interested in learning [SERVICE]? Drop [KEYWORD] in the comments and we'll send you the guide.",
        "We're opening [SERVICE] spots this week. Comment [KEYWORD] if you want the details.",
        "Free resource: [SERVICE] framework we use. Comment [KEYWORD] and we'll DM it to you.",
        "If [SERVICE] is something you've been thinking about, comment [KEYWORD] — we'll reach out.",
    ],
    "systems": [
        "Want a free audit of your current [SERVICE]? Comment [KEYWORD] and we'll set up a call.",
        "We built a [SERVICE] for a client just like you. Comment [KEYWORD] to see the case study.",
        "Automating [SERVICE] can save 10+ hours a week. Comment [KEYWORD] and we'll show you how.",
        "Comment [KEYWORD] if you want us to walk you through what [SERVICE] could look like for your business.",
        "Free consultation on [SERVICE] this week — comment [KEYWORD] to claim a slot.",
    ],
    "lawn": [
        "Comment [KEYWORD] for a free estimate on [SERVICE] — no obligation.",
        "Want [SERVICE] before the season starts? Comment [KEYWORD] and we'll get you on the schedule.",
        "First [SERVICE] is on us this month. Comment [KEYWORD] to book yours.",
        "Curious about pricing for [SERVICE]? Comment [KEYWORD] and we'll send you a quick quote.",
        "Spots for [SERVICE] are filling fast. Comment [KEYWORD] to hold your spot.",
    ],
    "restaurant": [
        "Comment [KEYWORD] and we'll send you the details on our [SERVICE] — limited spots available.",
        "Planning an event? Comment [KEYWORD] for our [SERVICE] menu and pricing.",
        "Claim your [SERVICE] discount — just comment [KEYWORD] and mention this post when you come in.",
        "Comment [KEYWORD] to get our [SERVICE] special delivered straight to your inbox.",
        "We're offering [SERVICE] this weekend only. Comment [KEYWORD] to get on the list.",
    ],
    "fitness": [
        "Comment [KEYWORD] and we'll DM you our free [SERVICE] plan — no strings attached.",
        "Starting your [SERVICE] journey? Comment [KEYWORD] and we'll send you the beginner guide.",
        "Free [SERVICE] session this week — comment [KEYWORD] to claim yours.",
        "Want to know what [SERVICE] actually looks like for your goals? Comment [KEYWORD].",
        "Comment [KEYWORD] if you're ready to start [SERVICE] — we'll reach out with next steps.",
    ],
    "realestate": [
        "Comment [KEYWORD] for a free [SERVICE] — no obligation, no pressure.",
        "Thinking about [SERVICE]? Comment [KEYWORD] and we'll send you the current market report.",
        "Free [SERVICE] available this week. Comment [KEYWORD] to schedule yours.",
        "Comment [KEYWORD] and we'll walk you through what [SERVICE] looks like in today's market.",
        "Selling your home this year? Comment [KEYWORD] for our free [SERVICE] checklist.",
    ],
    "local": [
        "Comment [KEYWORD] for a free estimate on [SERVICE] — we respond fast.",
        "Booking [SERVICE] slots now. Comment [KEYWORD] to get yours before they fill.",
        "First-time customer? Comment [KEYWORD] and mention this post for a discount on [SERVICE].",
        "Comment [KEYWORD] and we'll send you our [SERVICE] pricing and availability.",
        "We're taking on [SERVICE] clients this month. Comment [KEYWORD] if you're interested.",
    ],
    "tax": [
        "Comment [KEYWORD] for a free [SERVICE] consultation — 20 minutes, no obligation.",
        "Worried about [SERVICE]? Comment [KEYWORD] and we'll send you the checklist.",
        "Limited spots for [SERVICE] this quarter. Comment [KEYWORD] to get on the calendar.",
        "Comment [KEYWORD] and we'll show you the [SERVICE] deductions you're probably missing.",
        "Free [SERVICE] review for new clients this month — comment [KEYWORD] to claim.",
    ],
}


# =============================================================================
# OPTIMAL TIMES
# =============================================================================

OPTIMAL_TIMES = {
    "trading": {
        "best_days": ["Tue", "Wed", "Thu"],
        "best_times": ["7am-9am", "12pm-1pm", "8pm-10pm"],
        "rationale": "Traders are most active pre-market and after close. Midweek engagement is highest. Avoid Monday open chaos and Friday wind-down.",
    },
    "systems": {
        "best_days": ["Tue", "Wed", "Thu"],
        "best_times": ["8am-10am", "12pm-2pm", "5pm-7pm"],
        "rationale": "Business owners browse LinkedIn and Facebook during business hours and early evening. Midweek is peak decision-making time.",
    },
    "lawn": {
        "best_days": ["Tue", "Thu", "Sat"],
        "best_times": ["7am-9am", "11am-1pm", "6pm-8pm"],
        "rationale": "Homeowners think about their lawn before work and on weekends. Saturday morning is prime engagement before yard work begins.",
    },
    "restaurant": {
        "best_days": ["Wed", "Thu", "Fri", "Sat"],
        "best_times": ["11am-1pm", "4pm-6pm", "7pm-9pm"],
        "rationale": "People plan meals at lunch and early evening. Thursday and Friday are peak restaurant decision-making days. Weekend lunch captures brunch crowds.",
    },
    "fitness": {
        "best_days": ["Mon", "Wed", "Fri"],
        "best_times": ["6am-8am", "12pm-1pm", "6pm-8pm"],
        "rationale": "Fitness motivation peaks Monday (fresh start), midweek maintenance, and Friday (weekend prep). Early morning and evening gym-goer windows are highest engagement.",
    },
    "realestate": {
        "best_days": ["Tue", "Thu", "Sat", "Sun"],
        "best_times": ["8am-10am", "12pm-2pm", "5pm-8pm"],
        "rationale": "Buyers browse listings during lunch and evenings. Weekend open house traffic drives weekend engagement. Avoid Mondays when buyer activity dips.",
    },
    "local": {
        "best_days": ["Mon", "Wed", "Fri"],
        "best_times": ["8am-10am", "12pm-1pm", "5pm-7pm"],
        "rationale": "Local service buyers decide during business hours. Monday resets planning for the week. Friday drives last-minute booking for weekend services.",
    },
    "tax": {
        "best_days": ["Mon", "Tue", "Wed"],
        "best_times": ["8am-10am", "12pm-1pm", "7pm-9pm"],
        "rationale": "Tax concerns arise at the start of the week and during business hours. Evening posts catch self-employed people reviewing finances after hours.",
    },
}


# =============================================================================
# WEEK STRUCTURE (30-day calendar template)
# =============================================================================

WEEK_STRUCTURE = [
    # Week 1
    [
        {"day": 1,  "type": "educational",   "description": "Teach a core concept in your industry"},
        {"day": 2,  "type": "engagement",    "description": "Ask a question your audience cares about"},
        {"day": 3,  "type": "educational",   "description": "Bust a common myth in your niche"},
        {"day": 4,  "type": "promotional",   "description": "Soft sell — highlight a service with value framing"},
        {"day": 5,  "type": "viral",         "description": "One counter-intuitive insight designed for shares"},
        {"day": 6,  "type": "testimonial",   "description": "Client result or social proof story"},
        {"day": 7,  "type": "rest",          "description": "No post — let the week breathe"},
    ],
    # Week 2
    [
        {"day": 8,  "type": "lead_gen",      "description": "Comment-to-DM lead gen post with keyword CTA"},
        {"day": 9,  "type": "educational",   "description": "Step-by-step how-to post"},
        {"day": 10, "type": "engagement",    "description": "Poll or agree/disagree prompt"},
        {"day": 11, "type": "educational",   "description": "Industry trend or news take"},
        {"day": 12, "type": "promotional",   "description": "Limited availability or seasonal offer"},
        {"day": 13, "type": "viral",         "description": "Hot take or fill-in-the-blank post"},
        {"day": 14, "type": "rest",          "description": "No post — strategic silence"},
    ],
    # Week 3
    [
        {"day": 15, "type": "educational",   "description": "Deep-dive on a pain point your audience has"},
        {"day": 16, "type": "engagement",    "description": "Discussion starter — get comments flowing"},
        {"day": 17, "type": "testimonial",   "description": "Before and after or transformation story"},
        {"day": 18, "type": "lead_gen",      "description": "Free resource or consultation offer"},
        {"day": 19, "type": "educational",   "description": "Common mistake post — what not to do"},
        {"day": 20, "type": "viral",         "description": "Contrarian take — challenge conventional wisdom"},
        {"day": 21, "type": "rest",          "description": "No post — mid-month reset"},
    ],
    # Week 4
    [
        {"day": 22, "type": "promotional",   "description": "Direct offer — clear CTA for a service"},
        {"day": 23, "type": "educational",   "description": "Quick tip post — one actionable takeaway"},
        {"day": 24, "type": "engagement",    "description": "Community-building question"},
        {"day": 25, "type": "lead_gen",      "description": "End-of-month push — comment to claim"},
        {"day": 26, "type": "educational",   "description": "Seasonal or timely content"},
        {"day": 27, "type": "viral",         "description": "Share-worthy insight or punchy statement"},
        {"day": 28, "type": "testimonial",   "description": "Month-close social proof"},
        {"day": 29, "type": "promotional",   "description": "Bonus post — upcoming month preview or offer"},
        {"day": 30, "type": "engagement",    "description": "Reflection question — wrap up the month"},
    ],
]


# =============================================================================
# FUNCTIONS
# =============================================================================

def generate_viral_post(industry: str, page_name: str, custom_topic: str = None) -> dict:
    """
    Generate a high-engagement post designed for comments and shares.
    Returns {"text": str, "format": str, "pillar": str}
    """
    try:
        pillars = INDUSTRY_PILLARS.get(industry, INDUSTRY_PILLARS["local"])
        pillar = custom_topic or random.choice(pillars)
        fmt = random.choice(VIRAL_FORMATS)
        voice = INDUSTRY_VOICE.get(industry, INDUSTRY_VOICE["local"])

        format_instructions = {
            "engagement_question": "End the post with a direct question that invites the audience to share their own experience or opinion. The question must be the last line.",
            "myth_bust": "Open with a common belief stated as fact, then immediately contradict it. No hedging — be direct.",
            "hot_take": "Lead with an opinion that most people in the industry would push back on. State it plainly, defend it briefly.",
            "poll_prompt": "Present two options and ask the audience to pick one in the comments — Option A vs Option B format.",
            "discussion_starter": "Raise a debatable point without giving a definitive answer. Let the audience argue it out.",
            "fill_in_blank": "Write a sentence with a blank (___) and ask people to fill it in. Make the blank meaningful.",
            "agree_disagree": "State an opinion and ask people to reply with 'Agree' or 'Disagree' in the comments.",
        }

        prompt = f"""You write Facebook posts for {page_name}, a {industry} brand.
Voice and tone: {voice}.
Content pillar: {pillar}
Format: {fmt}
Format instructions: {format_instructions[fmt]}

Write a single Facebook post designed for maximum engagement — comments, shares, and saves.
Rules:
- Do NOT use generic motivational fluff or empty inspirational quotes
- No emojis unless they serve the message
- No hashtags
- No "Follow us for more" or similar self-promotional lines
- Write in the voice described — not in generic marketing voice
- The post must feel like a real person wrote it, not an ad agency
- Maximum 200 words
- Output only the post text — no title, no explanation, no quotes around the text

Topic: {pillar}"""

        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMP,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content.strip()
        return {"text": text, "format": fmt, "pillar": pillar}

    except Exception as e:
        return {"error": str(e), "text": "", "format": "", "pillar": ""}


def generate_lead_gen_post(industry: str, page_name: str, keyword: str = None, service: str = None) -> dict:
    """
    Generate a lead generation post with a specific CTA.
    Returns {"text": str, "keyword": str, "cta_type": str}
    """
    try:
        voice = INDUSTRY_VOICE.get(industry, INDUSTRY_VOICE["local"])
        pillars = INDUSTRY_PILLARS.get(industry, INDUSTRY_PILLARS["local"])
        templates = LEAD_TEMPLATES.get(industry, LEAD_TEMPLATES["local"])

        kw = keyword or random.choice(["INFO", "QUOTE", "FREE", "START", "YES"])
        svc = service or random.choice(pillars)
        template = random.choice(templates)
        cta_line = template.replace("[KEYWORD]", kw).replace("[SERVICE]", svc)

        prompt = f"""You write Facebook posts for {page_name}, a {industry} brand.
Voice and tone: {voice}.

Write a lead generation post that:
1. Opens by addressing a real pain point or desire your audience has related to: {svc}
2. Builds credibility briefly — one or two lines showing you understand their situation
3. Transitions naturally into an offer
4. Ends with this exact CTA line: {cta_line}

Rules:
- Do NOT use hype, excessive exclamation points, or salesy language
- Write in the voice described — grounded and credible
- No emojis unless they serve the message
- No hashtags
- The CTA line must appear verbatim at the end
- Maximum 180 words total
- Output only the post text — no title, no explanation, no quotes

Service/topic: {svc}"""

        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMP,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content.strip()
        return {"text": text, "keyword": kw, "cta_type": cta_line}

    except Exception as e:
        return {"error": str(e), "text": "", "keyword": "", "cta_type": ""}


def generate_calendar(industry: str, page_name: str, month_name: str = None) -> dict:
    """
    Generate a 30-day content calendar.
    Returns {"month": str, "days": [{"day": int, "type": str, "topic": str, "hook": str, "post_text": str}]}
    """
    try:
        from datetime import datetime
        month = month_name or datetime.now().strftime("%B %Y")
        pillars = INDUSTRY_PILLARS.get(industry, INDUSTRY_PILLARS["local"])
        voice = INDUSTRY_VOICE.get(industry, INDUSTRY_VOICE["local"])

        # Flatten week structure into a flat 30-day plan
        flat_days = []
        for week in WEEK_STRUCTURE:
            for day_entry in week:
                flat_days.append(day_entry)

        # Build the prompt asking for all 30 days at once in JSON
        pillar_list = "\n".join(f"- {p}" for p in pillars)

        prompt = f"""You are creating a 30-day Facebook content calendar for {page_name}, a {industry} brand.
Voice and tone: {voice}.
Month: {month}

Content pillars to draw from:
{pillar_list}

Generate exactly 30 days of content. For each day, return:
- day: the day number (1-30)
- type: one of educational, promotional, engagement, testimonial, lead_gen, viral, rest
- topic: a specific topic (not generic — be concrete, 5-10 words)
- hook: the first sentence of the post (attention-grabbing, 10-20 words)
- post_text: the full post text (50-180 words for non-rest days; "No post today." for rest days)

Day schedule and types:
{chr(10).join(f"Day {d['day']}: {d['type']} — {d['description']}" for week in WEEK_STRUCTURE for d in week)}

Return ONLY a valid JSON array of 30 objects with the keys: day, type, topic, hook, post_text.
No extra text, no markdown, no code blocks — just the raw JSON array."""

        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.75,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=6000,
        )

        raw = response.choices[0].message.content.strip()

        # Strip any accidental markdown
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        import json
        days = json.loads(raw)

        return {"month": month, "days": days}

    except Exception as e:
        return {"error": str(e), "month": month_name or "", "days": []}


def suggest_comment_reply(industry: str, page_name: str, comment: str, post_context: str = "") -> dict:
    """
    Suggest 3 AI-generated replies to a customer comment.
    Returns {"replies": [{"tone": str, "text": str}], "comment": str}
    Tones: professional, friendly, direct
    """
    try:
        voice = INDUSTRY_VOICE.get(industry, INDUSTRY_VOICE["local"])
        context_line = f"\nOriginal post context: {post_context}" if post_context else ""

        prompt = f"""You manage the Facebook page for {page_name}, a {industry} brand.
Brand voice: {voice}.{context_line}

A customer left this comment:
"{comment}"

Write 3 different reply options to this comment. Each reply should have a different tone:
1. Professional — measured, credible, informative
2. Friendly — warm, personal, conversational
3. Direct — concise, to the point, no fluff

Rules for all replies:
- Reply directly to the comment — acknowledge what they said
- Do not use generic phrases like "Thank you for your comment!" as the opener
- Do not use emojis unless the brand voice calls for it
- Keep each reply under 80 words
- Sound like a real person, not a PR department

Return ONLY a valid JSON array with exactly 3 objects, each with keys "tone" and "text".
Example format: [{"tone": "professional", "text": "..."}, ...]
No markdown, no explanation — just the JSON array."""

        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        import json
        replies = json.loads(raw)

        return {"replies": replies, "comment": comment}

    except Exception as e:
        return {"error": str(e), "replies": [], "comment": comment}


def generate_post_by_type(industry: str, page_name: str, content_type: str, topic: str = None) -> dict:
    """
    Generate a post of a specific type: educational, promotional, testimonial, seasonal, engagement_question
    Returns {"text": str, "type": str}
    """
    try:
        pillars = INDUSTRY_PILLARS.get(industry, INDUSTRY_PILLARS["local"])
        voice = INDUSTRY_VOICE.get(industry, INDUSTRY_VOICE["local"])
        chosen_topic = topic or random.choice(pillars)

        type_instructions = {
            "educational": (
                "Write an educational post that teaches the audience something concrete. "
                "Open with a hook that challenges a common assumption. Deliver one clear insight "
                "with specific detail. Close with an implication or takeaway — not a CTA. "
                "Length: 100-180 words."
            ),
            "promotional": (
                "Write a promotional post that leads with value before mentioning the service. "
                "First half: address a real problem or desire. Second half: introduce how your service helps. "
                "Close with a single clear CTA. Do not sound desperate or salesy. "
                "Length: 80-150 words."
            ),
            "testimonial": (
                "Write a client testimonial or social proof post. Frame it as a real outcome story — "
                "describe the situation before, what changed, and the result. "
                "Make it specific and credible, not vague. "
                "Length: 80-140 words."
            ),
            "seasonal": (
                "Write a post tied to the current season, time of year, or a relevant event. "
                "Connect seasonal context to a useful insight or offer relevant to the industry. "
                "Should feel timely and specific, not generic. "
                "Length: 80-150 words."
            ),
            "engagement_question": (
                "Write a post designed to generate comments. "
                "Share a brief perspective or observation, then end with a direct, specific question "
                "that invites the audience to share their experience or opinion. "
                "The question must be the final line. "
                "Length: 60-120 words."
            ),
        }

        instruction = type_instructions.get(content_type, type_instructions["educational"])

        prompt = f"""You write Facebook posts for {page_name}, a {industry} brand.
Voice and tone: {voice}.
Topic: {chosen_topic}
Content type: {content_type}

Instructions: {instruction}

Additional rules:
- No hashtags
- No generic marketing phrases
- No emojis unless the brand voice specifically calls for it
- Sound like a real person, not an ad agency
- Output only the post text — no title, no explanation, no quotes around the text"""

        response = client.chat.completions.create(
            model=MODEL,
            temperature=TEMP,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content.strip()
        return {"text": text, "type": content_type}

    except Exception as e:
        return {"error": str(e), "text": "", "type": content_type}
