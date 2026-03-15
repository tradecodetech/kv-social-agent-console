import json
import sys
import time
import random
import requests
from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_TEMPERATURE,
    MAX_GENERATION_RETRIES,
    FB_GRAPH_VERSION,
    LOG_DB_PATH,
    CSV_EXPORT_PATH,
    PAGES_JSON_PATH
)

from prompt import build_prompt, PROMPT_VERSION
from logger import (
    init_db,
    is_duplicate,
    is_too_similar,
    save_post,
    log_run,
    export_csv
)

from visuals import build_visual_prompt
from weather import get_weather_summary


# =========================
# VERSION
# =========================
AGENT_VERSION = "v3.0-viral"

# Facebook error codes with human-readable meanings
FB_ERROR_MEANINGS = {
    "190": "Access token expired or invalid — regenerate in Meta Business Suite",
    "200": "Permissions error — token missing pages_manage_posts permission. Regenerate token with correct scopes.",
    "368": "Blocked due to policy violation — review post content",
    "32":  "Page request limit reached — slow down posting frequency",
    "4":   "App call limit reached — API rate limit hit",
    "100": "Invalid parameter — check page_id and token format",
    "10":  "Permission denied — re-authorize the page app",
}

# Required Facebook permissions for posting
REQUIRED_FB_PERMISSIONS = [
    "pages_manage_posts",
    "pages_read_engagement",
    "pages_show_list",
]

# =========================
# OpenAI Client
# =========================
client = OpenAI(api_key=OPENAI_API_KEY)


# =========================
# CTA ROTATION (LOCAL SERVICE)
# =========================
CTAS = [
    "Need reliable lawn care? Visit our website.",
    "Local lawn care handled with consistency.",
    "We take care of the yard so you don't have to.",
    "Dependable lawn service for your property.",
    "Book lawn care when you're ready.",
    "Reach out if you want weekly service handled.",
]

def maybe_add_cta(text: str, use_cta: bool) -> str:
    if not use_cta:
        return text
    if random.random() < 0.33:  # soft cadence — not every post
        return f"{text}\n\n{random.choice(CTAS)}"
    return text


# =========================
# Load Pages Config
# =========================
def load_pages_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# Generate Post Text (with retry)
# =========================
def generate_post_text(prompt: str, retries: int = 2) -> str:
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=OPENAI_TEMPERATURE
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            error_str = str(e).lower()
            if "billing" in error_str or "quota" in error_str or "insufficient" in error_str:
                raise  # Don't retry billing errors
            if attempt < retries:
                time.sleep(2 ** attempt)  # exponential backoff
            else:
                raise


# =========================
# Generate Image (All Industries)
# Uses DALL-E 3 with quality-optimized prompts
# =========================
def generate_lawn_image(prompt: str) -> str:
    """
    Generate a high-quality image using DALL-E 3.
    Wraps the raw prompt with quality/style directives to avoid
    generic or low-quality AI aesthetics.
    """
    enhanced_prompt = (
        f"{prompt}. "
        "Style: clean commercial photography, natural lighting, sharp focus, "
        "professional composition, realistic, high resolution, no text overlays, "
        "no watermarks, no people unless naturally posed, no cartoonish elements."
    )
    img = client.images.generate(
        model="dall-e-3",
        prompt=enhanced_prompt,
        size="1792x1024",
        quality="hd",
        style="natural",
    )
    return img.data[0].url


# =========================
# Validate Token Permissions (pre-flight API check)
# =========================
def validate_token_permissions(page_token: str, page_name: str) -> tuple[bool, str]:
    """
    Validates the page token by calling /me?fields=id,name with the page token.
    NOTE: /me/permissions does NOT work with page tokens (only user tokens).
    Calling /me/permissions with a page token returns FB error #100
    "Tried accessing nonexisting field (permissions)" which blocks all posts.
    This lightweight check confirms the token is alive and the page is reachable.
    Returns (is_valid, error_message).
    """
    try:
        url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/me"
        r = requests.get(url, params={"access_token": page_token, "fields": "id,name"}, timeout=10)
        result = r.json()

        if "error" in result:
            err = result["error"]
            code = str(err.get("code", ""))
            msg = err.get("message", "Unknown error")
            if code == "190":
                return False, f"[{code}] Token expired — regenerate in Graph API Explorer"
            return False, f"[{code}] {msg}"

        if "id" not in result:
            return False, "Token validation returned no page ID — token may be malformed"

        return True, ""

    except Exception as e:
        # Don't block posting on network errors during validation
        print(f"  ⚠  {page_name} — permission check failed (network): {e}")
        return True, ""


# =========================
# Facebook Posting (with retry on transient errors)
# =========================
def post_to_facebook(page_id: str, page_token: str, message: str, image_url: str = None) -> dict:
    """
    Posts to a Facebook Page feed or photos endpoint.
    Uses pages_manage_posts permission (not deprecated publish_actions).
    """
    if image_url:
        url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{page_id}/photos"
        payload = {
            "url": image_url,
            "caption": message,
            "access_token": page_token,
            "published": "true",
        }
    else:
        url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{page_id}/feed"
        payload = {
            "message": message,
            "access_token": page_token,
            "published": "true",
        }

    for attempt in range(3):
        session = requests.Session()
        try:
            r = session.post(url, data=payload, timeout=30)
            result = r.json()

            err = result.get("error", {})
            err_code = str(err.get("code", ""))

            # Error 200 = permissions — give clear guidance and don't retry
            if err_code == "200":
                err_msg = err.get("message", "")
                # Catch legacy publish_actions reference and clarify
                if "publish_actions" in err_msg:
                    result["error"]["message"] = (
                        "Token was generated without 'pages_manage_posts' permission. "
                        "Regenerate your Page Access Token in Graph API Explorer and ensure "
                        "'pages_manage_posts' is selected. Do NOT use 'publish_actions' (deprecated)."
                    )
                return result

            # Don't retry hard auth/permission/param errors
            if err_code in ("190", "368", "10", "100"):
                return result

            # Retry on transient errors (rate limit, server error)
            if "error" in result and attempt < 2:
                print(f"  ↻  Transient FB error (attempt {attempt + 1}/3), retrying...")
                time.sleep(3 * (attempt + 1))
                continue

            return result

        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(3)
            else:
                return {"error": {"message": "Request timed out after 3 attempts"}}
        except Exception as e:
            return {"error": {"message": str(e)}}
        finally:
            session.close()

    return {"error": {"message": "Max retries exceeded"}}


# =========================
# Interpret Facebook Error
# =========================
def explain_fb_error(err: dict) -> str:
    code = str(err.get("code", ""))
    msg = err.get("message", "Unknown error")
    explanation = FB_ERROR_MEANINGS.get(code, "")
    if explanation:
        return f"[{code}] {msg} → {explanation}"
    return f"[{code}] {msg}"


# =========================
# Run Posting for One Page
# =========================
def run_for_page(page: dict, posts_per_run: int = 1):
    page_name = page.get("client_name") or page.get("name", "Unnamed Page")
    page_id = page["page_id"]
    page_token = page["page_token"]

    # Feature flags
    features = page.get("features", {})
    use_visuals = features.get("visuals", False)
    use_weather = features.get("weather", False)
    use_cta = features.get("cta", False)
    auto_posting = features.get("auto_posting", True)

    if not auto_posting:
        print(f"  ⏸  {page_name} — auto posting disabled, skipping")
        return

    # Fallback to old style_tags format
    if not features:
        style_tags = page.get("style_tags", [])
        use_visuals = "visuals-enabled" in style_tags
        use_weather = "weather-aware" in style_tags
        use_cta = "cta-allowed" in style_tags
    else:
        style_tags = page.get("style_tags", [])

    mode_weights = page.get("mode_weights", {"discipline": 60, "trading": 40})

    # ── Pre-flight token permission check ────────────────────────────────────
    token_ok, token_err = validate_token_permissions(page_token, page_name)
    if not token_ok:
        print(f"  ❌ {page_name} — Token permission check failed: {token_err}")
        print(f"     → ACTION REQUIRED: Regenerate token with pages_manage_posts, pages_read_engagement, pages_show_list")
        log_run(
            LOG_DB_PATH,
            page_name=page_name,
            page_id=page_id,
            mode="",
            pillar="",
            message="",
            fb_post_id=None,
            success=False,
            error_code="PERM",
            error_message=token_err,
            prompt_version=PROMPT_VERSION
        )
        return

    for _ in range(posts_per_run):
        for _attempt in range(MAX_GENERATION_RETRIES):
            try:
                prompt, mode, pillar = build_prompt(
                    mode_weights,
                    style_tags,
                    page_name
                )

                if use_weather:
                    weather_note = get_weather_summary()
                    prompt += f"\n\nContext:\nCurrent conditions: {weather_note}."

                text = generate_post_text(prompt)
                text = maybe_add_cta(text, use_cta)

                if is_duplicate(LOG_DB_PATH, text):
                    print(f"  ↩  {page_name} — duplicate detected, regenerating...")
                    continue

                if is_too_similar(LOG_DB_PATH, text):
                    print(f"  ↩  {page_name} — too similar to recent post, regenerating...")
                    continue

                image_url = None
                if use_visuals:
                    try:
                        industry = page.get("brand", {}).get("industry", "trading")
                        image_prompt = build_visual_prompt(pillar, industry=industry)
                        image_url = generate_lawn_image(image_prompt)
                    except Exception as img_err:
                        print(f"  ⚠  {page_name} — visual generation failed: {img_err}")

                fb = post_to_facebook(page_id, page_token, text, image_url=image_url)

                if "id" in fb:
                    save_post(LOG_DB_PATH, text)
                    log_run(
                        LOG_DB_PATH,
                        page_name=page_name,
                        page_id=page_id,
                        mode=mode,
                        pillar=pillar,
                        message=text,
                        fb_post_id=fb.get("id"),
                        success=True,
                        prompt_version=PROMPT_VERSION
                    )
                    print(f"  ✅ {page_name} — posted ({fb.get('id')})")
                    _print_post_preview(text)
                    return

                # ── Handle Facebook Error ─────────────────────────────────────
                err = fb.get("error", {})
                err_code = str(err.get("code", ""))

                log_run(
                    LOG_DB_PATH,
                    page_name=page_name,
                    page_id=page_id,
                    mode=mode,
                    pillar=pillar,
                    message=text,
                    fb_post_id=None,
                    success=False,
                    error_code=err_code or None,
                    error_message=err.get("message"),
                    prompt_version=PROMPT_VERSION
                )

                print(f"  ❌ {page_name} — {explain_fb_error(err)}")

                # Token expired — no point retrying this page
                if err_code == "190":
                    print(f"     → ACTION REQUIRED: Regenerate token for '{page_name}' in Meta Business Suite")
                    return

                # Permissions error — no point retrying
                if err_code == "200":
                    print(f"     → ACTION REQUIRED: Regenerate token with pages_manage_posts permission")
                    print(f"     → Graph API Explorer → GET /me/accounts → copy id + access_token")
                    return

                return

            except Exception as e:
                error_str = str(e).lower()

                # Billing/quota — fail gracefully
                if "billing" in error_str or "quota" in error_str or "insufficient" in error_str:
                    print(f"  ⚠  {page_name} — OpenAI billing/quota error")
                    log_run(
                        LOG_DB_PATH,
                        page_name=page_name,
                        page_id=page_id,
                        mode="",
                        pillar="",
                        message="",
                        fb_post_id=None,
                        success=False,
                        error_code="BILLING",
                        error_message=str(e),
                        prompt_version=PROMPT_VERSION
                    )
                    return

                # Final attempt — log and move on
                if _attempt == MAX_GENERATION_RETRIES - 1:
                    print(f"  ❌ {page_name} — max retries hit: {e}")
                    log_run(
                        LOG_DB_PATH,
                        page_name=page_name,
                        page_id=page_id,
                        mode="",
                        pillar="",
                        message="",
                        fb_post_id=None,
                        success=False,
                        error_code="EXCEPTION",
                        error_message=str(e),
                        prompt_version=PROMPT_VERSION
                    )
                    return

                raise


def _print_post_preview(text: str):
    """Print a short preview of the posted content."""
    preview = text[:120].replace("\n", " ")
    if len(text) > 120:
        preview += "..."
    print(f'     → "{preview}"')


# =========================
# Token Health Check
# =========================
def check_token_health(pages: list) -> None:
    """
    Quick pre-flight check — flags pages with obviously bad tokens.
    Does NOT make API calls; just checks for empty/placeholder tokens.
    """
    for page in pages:
        name = page.get("client_name") or page.get("name", "Unnamed")
        token = page.get("page_token", "")
        pid = page.get("page_id", "")

        if not token or token in ("", "YOUR_TOKEN_HERE", "EAARghOXjjyw..."):
            print(f"  ⚠  TOKEN WARNING: '{name}' has no valid token configured")

        if not pid or pid == "0":
            print(f"  ⚠  PAGE ID WARNING: '{name}' has no valid page_id configured")


# =========================
# Main Entrypoint
# =========================
def main():
    print(f"\n{'='*52}")
    print(f"  KV Systems Agent {AGENT_VERSION}")
    print(f"  Prompt: {PROMPT_VERSION}")
    print(f"{'='*52}\n")

    init_db(LOG_DB_PATH)

    cfg = load_pages_config(PAGES_JSON_PATH)
    default_posts_per_run = int(
        cfg.get("default_schedule", {}).get("posts_per_run", 1)
    )

    pages = cfg.get("pages", [])
    if not pages:
        raise RuntimeError("No pages found in pages.json")

    print(f"  Clients configured: {len(pages)}\n")
    check_token_health(pages)
    print()

    for page in pages:
        name = page.get("client_name") or page.get("name", "Unnamed")
        print(f"  ── {name}")

        ppr = int(page.get("posts_per_run", default_posts_per_run))
        if "cadence" in page:
            ppr = int(page["cadence"].get("posts_per_run", ppr))

        run_for_page(page, posts_per_run=ppr)

    print(f"\n  Exporting analytics → {CSV_EXPORT_PATH}")
    export_csv(LOG_DB_PATH, CSV_EXPORT_PATH)
    print(f"\n{'='*52}")
    print(f"  Run complete")
    print(f"{'='*52}\n")


# =========================
# HARD EXIT (TASK SCHEDULER SAFE)
# =========================
if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL] {e}")
        sys.exit(1)