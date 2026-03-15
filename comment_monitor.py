"""
KV Systems — Social Lead Automation Engine

Monitors Facebook page comments, detects trigger keywords,
auto-replies to comments, sends DM sequences, and creates leads.

Two modes:
  1. Webhook mode  — Facebook sends real-time events to /webhook/facebook
  2. Poll mode     — /api/leads/check-comments triggers a manual scan
"""

import time
import requests
from datetime import datetime
from typing import List, Optional

FB_GRAPH = "https://graph.facebook.com/v19.0"


# =============================================================================
# COMMENT POLLING (manual / scheduled scan)
# =============================================================================

def check_page_comments(page: dict, db_path: str) -> List[dict]:
    """
    Poll the last 10 posts of a Facebook page for new comments containing
    trigger keywords. Creates leads, auto-replies, and sends DMs.

    Returns a list of result dicts (one per lead created or error encountered).
    """
    from leads import (
        get_triggers, create_lead, add_lead_message,
        lead_exists_by_comment, update_lead,
    )

    page_id    = page.get("page_id", "")
    page_token = page.get("page_token", "")
    page_name  = page.get("client_name") or page.get("name", "Unknown")

    if not page_id or not page_token:
        return [{"error": "Missing page_id or page_token", "page": page_name}]

    # ── Load trigger config ────────────────────────────────────────────────────
    triggers = get_triggers(db_path, page_name)
    if not triggers:
        return [{"skipped": "No trigger config found", "page": page_name}]

    trigger  = triggers[0]
    keywords = [k.lower().strip() for k in trigger.get("keywords", []) if k.strip()]

    if not keywords or not trigger.get("active"):
        return [{"skipped": "Triggers inactive or no keywords", "page": page_name}]

    results = []

    try:
        # ── Fetch recent posts ────────────────────────────────────────────────
        posts_resp = requests.get(
            f"{FB_GRAPH}/{page_id}/posts",
            params={
                "access_token": page_token,
                "limit": 10,
                "fields": "id,message,created_time",
            },
            timeout=15,
        )
        posts_data = posts_resp.json()

        if "error" in posts_data:
            err_msg = posts_data["error"].get("message", "Facebook API error")
            return [{"error": err_msg, "page": page_name}]

        for post in posts_data.get("data", []):
            post_id = post.get("id", "")
            results.extend(
                _process_post_comments(
                    post_id, page_id, page_name, page_token,
                    trigger, keywords, db_path,
                )
            )

    except requests.RequestException as e:
        results.append({"error": f"Network error: {e}", "page": page_name})
    except Exception as e:
        results.append({"error": str(e), "page": page_name})

    return results


def _process_post_comments(
    post_id: str,
    page_id: str,
    page_name: str,
    page_token: str,
    trigger: dict,
    keywords: list,
    db_path: str,
) -> List[dict]:
    """Fetch and process all comments on a single post."""
    from leads import (
        create_lead, add_lead_message,
        lead_exists_by_comment, update_lead,
    )

    results = []
    try:
        resp = requests.get(
            f"{FB_GRAPH}/{post_id}/comments",
            params={
                "access_token": page_token,
                "limit": 50,
                "fields": "id,message,from,created_time",
            },
            timeout=15,
        )
        data = resp.json()
        if "error" in data:
            return [{"error": data["error"].get("message"), "post_id": post_id}]

        for comment in data.get("data", []):
            result = _process_single_comment(
                comment, post_id, page_id, page_name, page_token,
                trigger, keywords, db_path,
            )
            if result:
                results.append(result)

    except Exception as e:
        results.append({"error": str(e), "post_id": post_id})

    return results


def _process_single_comment(
    comment: dict,
    post_id: str,
    page_id: str,
    page_name: str,
    page_token: str,
    trigger: dict,
    keywords: list,
    db_path: str,
) -> Optional[dict]:
    """
    Evaluate one comment. If a trigger keyword is found:
      1. Create lead
      2. Auto-reply to comment
      3. Send DM sequence
    Returns a result dict or None if no action taken.
    """
    from leads import (
        create_lead, add_lead_message,
        lead_exists_by_comment, update_lead,
    )

    comment_id   = comment.get("id", "")
    comment_text = comment.get("message", "")
    sender       = comment.get("from", {})
    commenter_name = sender.get("name", "Unknown")
    commenter_id   = sender.get("id")

    # Already processed?
    if lead_exists_by_comment(db_path, comment_id):
        return None

    # Detect trigger keyword
    lower_text = comment_text.lower()
    detected_keyword = next((k for k in keywords if k in lower_text), None)
    if not detected_keyword:
        return None

    # ── Create lead ────────────────────────────────────────────────────────────
    lead_id = create_lead(db_path, {
        "page_name":      page_name,
        "page_id":        page_id,
        "commenter_name": commenter_name,
        "commenter_id":   commenter_id,
        "trigger_keyword": detected_keyword,
        "source_post_id": post_id,
        "comment_text":   comment_text,
        "comment_id":     comment_id,
    })

    if lead_id < 0:
        return None  # Duplicate was caught in DB

    add_lead_message(db_path, lead_id, "inbound", "comment", comment_text)

    result = {
        "lead_id":   lead_id,
        "page":      page_name,
        "commenter": commenter_name,
        "keyword":   detected_keyword,
        "comment":   comment_text[:120],
        "actions":   [],
    }

    # ── Auto-reply to comment ──────────────────────────────────────────────────
    auto_reply_text = trigger.get("auto_reply_text", "").strip()
    if auto_reply_text:
        replied = reply_to_comment(comment_id, auto_reply_text, page_token)
        if replied:
            update_lead(db_path, lead_id, {"auto_replied": 1})
            add_lead_message(db_path, lead_id, "outbound", "comment", auto_reply_text)
            result["actions"].append("comment_reply")
        else:
            result["actions"].append("comment_reply_failed")

    # ── Send DM sequence ───────────────────────────────────────────────────────
    dm_sequence = trigger.get("dm_sequence", [])
    if dm_sequence and commenter_id:
        # Personalise first message with commenter name
        personalised = []
        for msg in dm_sequence:
            personalised.append(msg.replace("{name}", commenter_name))

        dm_ok = send_dm_sequence(page_id, commenter_id, personalised, page_token)
        if dm_ok:
            update_lead(db_path, lead_id, {"dm_sent": 1})
            for msg in personalised:
                add_lead_message(db_path, lead_id, "outbound", "dm", msg)
            result["actions"].append("dm_sent")
        else:
            result["actions"].append("dm_failed")

    return result


# =============================================================================
# WEBHOOK EVENT PROCESSOR (real-time)
# =============================================================================

def process_webhook_event(webhook_data: dict, db_path: str, pages_config: dict) -> List[dict]:
    """
    Handle a Facebook webhook POST payload.
    Called by the /webhook/facebook route in server.py.
    """
    from leads import (
        get_triggers, create_lead, add_lead_message,
        lead_exists_by_comment, update_lead,
    )

    results = []

    try:
        for entry in webhook_data.get("entry", []):
            page_id = entry.get("id", "")

            # Find matching page config
            page = next(
                (p for p in pages_config.get("pages", []) if p.get("page_id") == page_id),
                None,
            )
            if not page:
                continue

            page_name  = page.get("client_name") or page.get("name", "Unknown")
            page_token = page.get("page_token", "")
            triggers   = get_triggers(db_path, page_name)
            if not triggers:
                continue

            trigger  = triggers[0]
            keywords = [k.lower().strip() for k in trigger.get("keywords", []) if k.strip()]
            if not keywords or not trigger.get("active"):
                continue

            for change in entry.get("changes", []):
                if change.get("field") != "feed":
                    continue
                value = change.get("value", {})
                if value.get("item") != "comment" or value.get("verb") != "add":
                    continue

                comment_id   = value.get("comment_id", "")
                comment_text = value.get("message", "")
                post_id      = value.get("post_id", "")
                sender       = value.get("from", {})

                result = _process_single_comment(
                    {"id": comment_id, "message": comment_text, "from": sender},
                    post_id, page_id, page_name, page_token,
                    trigger, keywords, db_path,
                )
                if result:
                    results.append(result)

    except Exception as e:
        results.append({"error": str(e)})

    return results


# =============================================================================
# FACEBOOK API HELPERS
# =============================================================================

def reply_to_comment(comment_id: str, reply_text: str, page_token: str) -> bool:
    """Post a public reply to a Facebook comment."""
    try:
        resp = requests.post(
            f"{FB_GRAPH}/{comment_id}/comments",
            params={"access_token": page_token},
            json={"message": reply_text},
            timeout=10,
        )
        return "id" in resp.json()
    except Exception:
        return False


def send_dm_sequence(
    page_id: str,
    recipient_id: str,
    messages: List[str],
    page_token: str,
    delay_seconds: float = 1.0,
) -> bool:
    """
    Send a sequence of messages via the Facebook Messenger API.
    Returns True if all messages were sent successfully.
    """
    url = f"{FB_GRAPH}/{page_id}/messages"
    success = True
    for i, message in enumerate(messages):
        if i > 0:
            time.sleep(delay_seconds)
        try:
            resp = requests.post(
                url,
                params={"access_token": page_token},
                json={
                    "recipient":      {"id": recipient_id},
                    "message":        {"text": message},
                    "messaging_type": "RESPONSE",
                },
                timeout=10,
            )
            data = resp.json()
            if "error" in data:
                success = False
        except Exception:
            success = False
    return success


def send_manual_dm(
    page_id: str,
    recipient_id: str,
    message: str,
    page_token: str,
) -> bool:
    """Send a single manual DM reply from the Lead Inbox."""
    return send_dm_sequence(page_id, recipient_id, [message], page_token, delay_seconds=0)
