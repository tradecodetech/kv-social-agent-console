"""
KV Systems — Lead Capture Module (Merged)
==========================================
Combines:
  - Original KV lead schema, CRUD, and trigger configs
  - Facebook comment keyword scanner
  - Facebook reaction scanner
  - Auto DM via Messenger API
  - Telegram alert on new lead detection
  - Manual DM sender for Lead Inbox reply box

Environment variables required for new features:
  TELEGRAM_BOT_TOKEN   — from @BotFather
  TELEGRAM_CHAT_ID     — your chat ID (message bot, then GET /getUpdates)
  FB_GRAPH_VERSION     — already in .env (e.g. v19.0)
"""

import os
import sqlite3
import json
import requests
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import FB_GRAPH_VERSION, LOG_DB_PATH

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID", "")


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_leads_db(db_path: str = LOG_DB_PATH):
    """Initialize lead-related tables in the SQLite database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            ts                TEXT,
            page_name         TEXT,
            page_id           TEXT,
            commenter_name    TEXT,
            commenter_id      TEXT,
            trigger_keyword   TEXT,
            trigger_type      TEXT DEFAULT 'keyword',
            source_post_id    TEXT,
            comment_text      TEXT,
            comment_id        TEXT UNIQUE,
            status            TEXT DEFAULT 'new',
            service_requested TEXT,
            location          TEXT,
            phone             TEXT,
            email             TEXT,
            notes             TEXT,
            dm_sent           INTEGER DEFAULT 0,
            auto_replied      INTEGER DEFAULT 0,
            created_at        TEXT,
            updated_at        TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS lead_messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id   INTEGER,
            direction TEXT,
            channel   TEXT,
            message   TEXT,
            ts        TEXT,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS comment_triggers (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            page_name       TEXT UNIQUE,
            keywords        TEXT,
            auto_reply_text TEXT,
            dm_sequence     TEXT,
            active          INTEGER DEFAULT 1,
            created_at      TEXT
        )
    """)

    # Track scanned posts to avoid rescanning
    c.execute("""
        CREATE TABLE IF NOT EXISTS scanned_posts (
            post_id    TEXT PRIMARY KEY,
            page_name  TEXT,
            scanned_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# =============================================================================
# LEADS CRUD (original)
# =============================================================================

def create_lead(db_path: str, data: dict) -> int:
    """Create a new lead and return its ID."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        c.execute("""
            INSERT INTO leads (
                ts, page_name, page_id, commenter_name, commenter_id,
                trigger_keyword, trigger_type, source_post_id, comment_text, comment_id,
                status, dm_sent, auto_replied, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', 0, 0, ?, ?)
        """, (
            now,
            data.get("page_name"),
            data.get("page_id"),
            data.get("commenter_name", "Unknown"),
            data.get("commenter_id"),
            data.get("trigger_keyword"),
            data.get("trigger_type", "keyword"),
            data.get("source_post_id"),
            data.get("comment_text"),
            data.get("comment_id"),
            now, now,
        ))
        lead_id = c.lastrowid
        conn.commit()
    except sqlite3.IntegrityError:
        # comment_id already exists — return existing lead id
        c.execute("SELECT id FROM leads WHERE comment_id = ?", (data.get("comment_id"),))
        row = c.fetchone()
        lead_id = row[0] if row else -1
    finally:
        conn.close()
    return lead_id


def add_lead_message(db_path: str, lead_id: int, direction: str, channel: str, message: str):
    """Add a message to a lead conversation history."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO lead_messages (lead_id, direction, channel, message, ts) VALUES (?, ?, ?, ?, ?)",
        (lead_id, direction, channel, message, now),
    )
    conn.commit()
    conn.close()


def update_lead(db_path: str, lead_id: int, updates: dict):
    """Update arbitrary fields on a lead."""
    if not updates:
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    safe_fields = {
        "status", "service_requested", "location", "phone", "email",
        "notes", "dm_sent", "auto_replied",
    }
    fields, values = [], []
    for k, v in updates.items():
        if k in safe_fields:
            fields.append(f"{k} = ?")
            values.append(v)
    if not fields:
        conn.close()
        return
    fields.append("updated_at = ?")
    values.append(now)
    values.append(lead_id)
    c.execute(f"UPDATE leads SET {', '.join(fields)} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_leads(
    db_path: str = LOG_DB_PATH,
    page_name: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> List[dict]:
    """Return leads, optionally filtered by page and/or status."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    conditions, params = [], []
    if page_name:
        conditions.append("page_name = ?")
        params.append(page_name)
    if status and status != "all":
        conditions.append("status = ?")
        params.append(status)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    c.execute(f"SELECT * FROM leads {where} ORDER BY created_at DESC LIMIT ?", params + [limit])
    cols = [d[0] for d in c.description]
    rows = [dict(zip(cols, r)) for r in c.fetchall()]
    conn.close()
    return rows


def get_lead_detail(db_path: str = LOG_DB_PATH, lead_id: int = 0) -> Optional[dict]:
    """Return a single lead with full conversation history."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    cols = [d[0] for d in c.description]
    lead = dict(zip(cols, row))
    c.execute("SELECT * FROM lead_messages WHERE lead_id = ? ORDER BY ts ASC", (lead_id,))
    msg_cols = [d[0] for d in c.description]
    lead["messages"] = [dict(zip(msg_cols, r)) for r in c.fetchall()]
    conn.close()
    return lead


def get_leads_stats(db_path: str = LOG_DB_PATH) -> dict:
    """Return aggregate lead statistics for the dashboard."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM leads")
    total = c.fetchone()[0]
    c.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    by_status = dict(c.fetchall())
    c.execute("SELECT COUNT(*) FROM leads WHERE created_at >= date('now', '-7 days')")
    this_week = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leads WHERE dm_sent = 1")
    dm_sent = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM leads WHERE auto_replied = 1")
    auto_replied = c.fetchone()[0]
    c.execute("""
        SELECT page_name, COUNT(*) as cnt FROM leads
        GROUP BY page_name ORDER BY cnt DESC
    """)
    by_page = [{"page": r[0], "count": r[1]} for r in c.fetchall()]
    c.execute("""
        SELECT trigger_keyword, COUNT(*) as cnt FROM leads
        WHERE trigger_keyword IS NOT NULL
        GROUP BY trigger_keyword ORDER BY cnt DESC LIMIT 10
    """)
    top_keywords = [{"keyword": r[0], "count": r[1]} for r in c.fetchall()]
    conn.close()
    return {
        "total":           total,
        "total_leads":     total,
        "this_week":       this_week,
        "dm_sent":         dm_sent,
        "auto_replied":    auto_replied,
        "by_status":       by_status,
        "by_page":         by_page,
        "top_keywords":    top_keywords,
        "conversion_rate": round(by_status.get("converted", 0) / max(1, total) * 100, 1),
    }


def lead_exists_by_comment(db_path: str, comment_id: str) -> bool:
    """Return True if a lead already exists for this comment ID."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id FROM leads WHERE comment_id = ?", (comment_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


# =============================================================================
# TRIGGER CONFIGURATIONS (original)
# =============================================================================

DEFAULT_KEYWORDS     = ["quote", "price", "interested", "info", "estimate", "yes", "dm", "how much", "details"]
DEFAULT_AUTO_REPLY   = "Thanks for reaching out! Check your DMs — we'll get you taken care of. 🙌"
DEFAULT_DM_SEQUENCE  = [
    "Hey {name}! Thanks for your interest. We'd love to help.",
    "Can you tell us a little about what service or product you're looking for?",
    "What's the best way to reach you — phone, email, or just reply here?",
]


def get_triggers(db_path: str, page_name: Optional[str] = None) -> List[dict]:
    """Return comment trigger configurations."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if page_name:
        c.execute("SELECT * FROM comment_triggers WHERE page_name = ?", (page_name,))
    else:
        c.execute("SELECT * FROM comment_triggers ORDER BY id DESC")
    cols = [d[0] for d in c.description]
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(zip(cols, row))
        try:    d["keywords"]    = json.loads(d["keywords"])
        except: d["keywords"]    = []
        try:    d["dm_sequence"] = json.loads(d["dm_sequence"])
        except: d["dm_sequence"] = []
        result.append(d)
    return result


def upsert_trigger(
    db_path: str,
    page_name: str,
    keywords: list,
    auto_reply: str,
    dm_sequence: list,
    active: bool = True,
) -> int:
    """Create or update a trigger config for a page."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("SELECT id FROM comment_triggers WHERE page_name = ?", (page_name,))
    existing = c.fetchone()
    if existing:
        c.execute("""
            UPDATE comment_triggers
            SET keywords=?, auto_reply_text=?, dm_sequence=?, active=?
            WHERE page_name=?
        """, (json.dumps(keywords), auto_reply, json.dumps(dm_sequence), int(active), page_name))
        trigger_id = existing[0]
    else:
        c.execute("""
            INSERT INTO comment_triggers (page_name, keywords, auto_reply_text, dm_sequence, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (page_name, json.dumps(keywords), auto_reply, json.dumps(dm_sequence), int(active), now))
        trigger_id = c.lastrowid
    conn.commit()
    conn.close()
    return trigger_id


# =============================================================================
# TELEGRAM ALERT
# =============================================================================

def send_telegram_alert(lead: dict, trigger_type: str = "keyword") -> bool:
    """
    Send a Telegram notification when a new lead is detected.
    Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to your .env file.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  ⚠  Telegram not configured — add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
        return False

    emoji  = "💬" if trigger_type == "keyword" else "❤️"
    name   = lead.get("commenter_name", "Unknown")
    page   = lead.get("page_name", "")
    kw     = lead.get("trigger_keyword", "")
    text   = (lead.get("comment_text") or "")[:120]
    ts     = lead.get("created_at", lead.get("ts", ""))

    msg = (
        f"{emoji} *New Lead — {trigger_type.upper()}*\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Name:* {name}\n"
        f"📄 *Page:* {page}\n"
        f"🔑 *Trigger:* `{kw}`\n"
        f"💬 *Comment:* _{text}_\n"
        f"🕐 *Time:* {ts}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"➡️ Open KV Console → Lead Inbox"
    )

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       msg,
            "parse_mode": "Markdown",
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"  ⚠  Telegram alert failed: {e}")
        return False


# =============================================================================
# FACEBOOK DM SENDER
# =============================================================================

def send_facebook_dm(recipient_id: str, message: str, page_token: str) -> dict:
    """
    Send a DM via the Facebook Messenger Send API.
    Requires pages_messaging permission on the page token.
    recipient_id = commenter Facebook PSID.
    """
    url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/me/messages"
    payload = {
        "recipient":    {"id": recipient_id},
        "message":      {"text": message},
        "access_token": page_token,
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": {"message": str(e)}}


def build_dm_from_sequence(
    page_name: str,
    commenter_name: str,
    trigger_keyword: str,
    dm_sequence: list,
) -> str:
    """
    Build the first DM message from the page trigger sequence.
    Falls back to a sensible default if sequence is empty.
    """
    if dm_sequence:
        msg = dm_sequence[0]
    else:
        msg = "Hey {name}! Thanks for your interest. We'd love to help. We'll be in touch shortly."

    return msg.replace("{name}", commenter_name.split()[0] if commenter_name else "there")


# =============================================================================
# FACEBOOK COMMENT + REACTION SCANNER
# =============================================================================

def _get_recent_posts(page_id: str, page_token: str, limit: int = 15) -> List[dict]:
    """Fetch recent posts from a Facebook page."""
    url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{page_id}/posts"
    params = {
        "access_token": page_token,
        "fields":       "id,message,created_time",
        "limit":        limit,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json().get("data", [])
    except Exception as e:
        print(f"  ⚠  Could not fetch posts: {e}")
        return []


def _get_post_comments(post_id: str, page_token: str) -> List[dict]:
    """Fetch comments on a post."""
    url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{post_id}/comments"
    params = {
        "access_token": page_token,
        "fields":       "id,message,from,created_time",
        "limit":        100,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json().get("data", [])
    except Exception as e:
        print(f"  ⚠  Could not fetch comments for {post_id}: {e}")
        return []


def _get_post_reactions(post_id: str, page_token: str) -> List[dict]:
    """Fetch reactions on a post."""
    url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{post_id}/reactions"
    params = {
        "access_token": page_token,
        "fields":       "id,name,type",
        "limit":        100,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json().get("data", [])
    except Exception as e:
        print(f"  ⚠  Could not fetch reactions for {post_id}: {e}")
        return []


def _get_page_conversations(page_token: str, limit: int = 50) -> list:
    """Fetch recent conversations (people who messaged the page) with real PSIDs."""
    url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/me/conversations"
    params = {
        "access_token": page_token,
        "fields":       "id,participants,updated_time",
        "limit":        limit,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        return r.json().get("data", [])
    except Exception as e:
        print(f"  Could not fetch conversations: {e}")
        return []


def _mark_post_scanned(post_id: str, page_name: str, db_path: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO scanned_posts (post_id, page_name) VALUES (?,?)",
        (post_id, page_name)
    )
    conn.commit()
    conn.close()


def scan_page_for_leads(
    page: dict,
    keywords: Optional[List[str]] = None,
    scan_reactions: bool = True,
    db_path: str = LOG_DB_PATH,
) -> List[dict]:
    """
    Scan a page's recent posts for keyword comments and reactions.
    Uses trigger config from DB if keywords not passed directly.
    Creates leads, sends DMs, fires Telegram alerts.

    Args:
        page:            Page config dict from pages.json
        keywords:        Override keywords (else uses comment_triggers table)
        scan_reactions:  Whether to capture reactors as leads
        db_path:         SQLite DB path

    Returns:
        List of newly created lead dicts
    """
    page_name  = page.get("client_name") or page.get("name", "Unnamed")
    page_id    = page.get("page_id", "")
    page_token = page.get("page_token", "")

    # Feature flag check
    if not page.get("features", {}).get("lead_capture", False):
        print(f"  ⏸  {page_name} — lead_capture disabled, skipping")
        return []

    if not page_token or not page_id:
        print(f"  ⚠  {page_name} — missing token or page_id")
        return []

    init_leads_db(db_path)

    # Resolve keywords — use passed list, else pull from trigger config, else defaults
    if not keywords:
        triggers = get_triggers(db_path, page_name)
        if triggers and triggers[0].get("keywords"):
            keywords = triggers[0]["keywords"]
            dm_sequence  = triggers[0].get("dm_sequence", DEFAULT_DM_SEQUENCE)
            auto_reply   = triggers[0].get("auto_reply_text", DEFAULT_AUTO_REPLY)
        else:
            keywords    = DEFAULT_KEYWORDS
            dm_sequence = DEFAULT_DM_SEQUENCE
            auto_reply  = DEFAULT_AUTO_REPLY
    else:
        dm_sequence = DEFAULT_DM_SEQUENCE
        auto_reply  = DEFAULT_AUTO_REPLY

    # Also check page-level lead_keywords field
    page_kw = page.get("lead_keywords", [])
    if page_kw:
        keywords = list(set(keywords + [k.lower() for k in page_kw]))

    kw_lower  = [k.strip().lower() for k in keywords if k.strip()]
    new_leads = []

    posts = _get_recent_posts(page_id, page_token, limit=15)
    print(f"  🔍 {page_name} — scanning {len(posts)} posts | keywords: {kw_lower}")

    for post in posts:
        post_id = post.get("id", "")

        # ── KEYWORD COMMENTS ──────────────────────────────────────────────────
        for comment in _get_post_comments(post_id, page_token):
            comment_id     = comment.get("id", "")
            from_info      = comment.get("from", {})
            commenter_id   = from_info.get("id", "")
            commenter_name = from_info.get("name", "Unknown")
            comment_text   = comment.get("message", "")

            # If from is null (Dev Mode restriction), use comment_id as synthetic user id
            if not commenter_id:
                commenter_id   = f"unknown_{comment_id}"
                commenter_name = "Facebook User"

            if not comment_id:
                continue

            # Duplicate check using comment_id (unique constraint in DB)
            if lead_exists_by_comment(db_path, comment_id):
                continue

            matched_kw = next(
                (kw.upper() for kw in kw_lower if kw in comment_text.lower()), None
            )
            if not matched_kw:
                continue

            lead_id = create_lead(db_path, {
                "page_name":     page_name,
                "page_id":       page_id,
                "commenter_name": commenter_name,
                "commenter_id":  commenter_id,
                "trigger_keyword": matched_kw,
                "trigger_type":  "keyword",
                "source_post_id": post_id,
                "comment_text":  comment_text,
                "comment_id":    comment_id,
            })

            if lead_id < 0:
                continue

            lead = get_lead_detail(db_path, lead_id)
            new_leads.append(lead)
            add_lead_message(db_path, lead_id, "inbound", "comment", comment_text)
            print(f"  ✅ Keyword lead: {commenter_name} → '{matched_kw}' on {page_name}")

            # DM
            dm_text = build_dm_from_sequence(page_name, commenter_name, matched_kw, dm_sequence)
            dm_result = send_facebook_dm(commenter_id, dm_text, page_token)
            if "error" not in dm_result:
                update_lead(db_path, lead_id, {"dm_sent": 1, "auto_replied": 1})
                add_lead_message(db_path, lead_id, "outbound", "dm", dm_text)
                print(f"     📨 DM sent to {commenter_name}")
            else:
                err = dm_result.get("error", {}).get("message", "")
                print(f"     ⚠  DM failed ({commenter_name}): {err}")

            # Telegram
            send_telegram_alert(lead, "keyword")

        # ── REACTIONS ─────────────────────────────────────────────────────────
        if scan_reactions:
            for reaction in _get_post_reactions(post_id, page_token):
                reactor_id   = reaction.get("id", "")
                reactor_name = reaction.get("name", "Unknown")
                react_type   = reaction.get("type", "LIKE")

                if not reactor_id:
                    continue

                # Use post_id + reactor_id as synthetic comment_id for dedup
                synthetic_id = f"reaction_{post_id}_{reactor_id}"
                if lead_exists_by_comment(db_path, synthetic_id):
                    continue

                lead_id = create_lead(db_path, {
                    "page_name":      page_name,
                    "page_id":        page_id,
                    "commenter_name": reactor_name,
                    "commenter_id":   reactor_id,
                    "trigger_keyword": react_type,
                    "trigger_type":   "reaction",
                    "source_post_id": post_id,
                    "comment_text":   f"Reacted: {react_type}",
                    "comment_id":     synthetic_id,
                })

                if lead_id < 0:
                    continue

                lead = get_lead_detail(db_path, lead_id)
                new_leads.append(lead)
                add_lead_message(db_path, lead_id, "inbound", "comment", f"Reacted: {react_type}")
                print(f"  ✅ Reaction lead: {reactor_name} → {react_type} on {page_name}")

                dm_text = build_dm_from_sequence(page_name, reactor_name, react_type.title(), dm_sequence)
                dm_result = send_facebook_dm(reactor_id, dm_text, page_token)
                if "error" not in dm_result:
                    update_lead(db_path, lead_id, {"dm_sent": 1, "auto_replied": 1})
                    add_lead_message(db_path, lead_id, "outbound", "dm", dm_text)
                else:
                    err = dm_result.get("error", {}).get("message", "")
                    print(f"     ⚠  DM failed ({reactor_name}): {err}")

                send_telegram_alert(lead, "reaction")

        _mark_post_scanned(post_id, page_name, db_path)

    # ── CONVERSATIONS (people who messaged the page) ──────────────────────────
    # These always return real names and PSIDs — use as primary lead source
    print(f"  💬 {page_name} — scanning inbox conversations for leads...")
    conversations = _get_page_conversations(page_token, limit=50)
    for conv in conversations:
        participants = conv.get("participants", {}).get("data", [])
        # Find the non-page participant
        for p in participants:
            pid   = p.get("id", "")
            pname = p.get("name", "Unknown")
            # Skip the page itself
            if pid == page_id:
                continue
            synthetic_id = f"conv_{conv.get('id','')}"
            if lead_exists_by_comment(db_path, synthetic_id):
                continue
            lead_id = create_lead(db_path, {
                "page_name":      page_name,
                "page_id":        page_id,
                "commenter_name": pname,
                "commenter_id":   pid,
                "trigger_keyword": "messenger",
                "trigger_type":   "conversation",
                "source_post_id": conv.get("id", ""),
                "comment_text":   "Sent a message to the page",
                "comment_id":     synthetic_id,
            })
            if lead_id < 0:
                continue
            lead = get_lead_detail(db_path, lead_id)
            new_leads.append(lead)
            add_lead_message(db_path, lead_id, "inbound", "dm", "Sent a message to the page")
            print(f"  ✅ Conversation lead: {pname} (PSID: {pid})")
            send_telegram_alert(lead, "conversation")

    return new_leads


# =============================================================================
# MANUAL DM (Lead Inbox reply button)
# =============================================================================

def send_manual_dm(
    lead_id: int,
    message: str,
    page_name: str,
    pages_config: List[dict],
    db_path: str = LOG_DB_PATH,
) -> dict:
    """
    Send a manual reply DM from the Lead Inbox.
    Looks up the correct page token from pages config.
    """
    lead = get_lead_detail(db_path, lead_id)
    if not lead:
        return {"error": "Lead not found"}

    commenter_id = lead.get("commenter_id", "")
    if not commenter_id:
        return {"error": "No commenter ID on this lead — cannot send DM"}

    page_cfg = next(
        (p for p in pages_config
         if (p.get("client_name") or p.get("name", "")).lower() == page_name.lower()),
        None
    )
    if not page_cfg:
        return {"error": f"Page '{page_name}' not found in config"}

    page_token = page_cfg.get("page_token", "")
    if not page_token:
        return {"error": "No token configured for this page"}

    result = send_facebook_dm(commenter_id, message, page_token)
    if "error" not in result:
        update_lead(db_path, lead_id, {"dm_sent": 1})
        add_lead_message(db_path, lead_id, "outbound", "dm", message)
        return {"status": "sent", "message_id": result.get("message_id")}

    return result


# =============================================================================
# MIGRATION — run once to add missing columns to existing DB
# =============================================================================

def migrate_leads_db(db_path: str = LOG_DB_PATH):
    """
    Safely adds any missing columns to an existing leads table.
    Safe to run multiple times — skips columns that already exist.
    """
    new_columns = [
        ("trigger_type", "TEXT DEFAULT 'keyword'"),
        ("service_requested", "TEXT"),
        ("location", "TEXT"),
        ("email", "TEXT"),
    ]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(leads)")
    existing = {row[1] for row in c.fetchall()}
    for col_name, col_def in new_columns:
        if col_name not in existing:
            try:
                c.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_def}")
                print(f"  ✅ Migration: added column '{col_name}' to leads table")
            except Exception as e:
                print(f"  ⚠  Migration skipped '{col_name}': {e}")
    # Also ensure scanned_posts table exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS scanned_posts (
            post_id    TEXT PRIMARY KEY,
            page_name  TEXT,
            scanned_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()