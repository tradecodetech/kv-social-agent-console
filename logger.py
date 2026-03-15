import sqlite3
from datetime import datetime
from difflib import SequenceMatcher

# =========================
# DATABASE SETUP
# =========================

def init_db(db_path: str):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Prevent exact duplicate posts
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT UNIQUE,
            created_at TEXT
        )
    """)

    # 🔥 UPGRADED: Added prompt_version column
    # Check if column exists before creating table
    c.execute("""
        CREATE TABLE IF NOT EXISTS run_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            page_name TEXT,
            page_id TEXT,
            mode TEXT,
            pillar TEXT,
            message_len INTEGER,
            fb_post_id TEXT,
            success INTEGER,
            error_code TEXT,
            error_message TEXT
        )
    """)
    
    # Add prompt_version column if it doesn't exist
    c.execute("PRAGMA table_info(run_logs)")
    columns = [row[1] for row in c.fetchall()]
    if 'prompt_version' not in columns:
        c.execute("ALTER TABLE run_logs ADD COLUMN prompt_version TEXT")
        print("[INFO] Added prompt_version column to database")

    conn.commit()
    conn.close()


# =========================
# DUPLICATE & SIMILARITY CHECKS
# =========================

def is_duplicate(db_path: str, text: str) -> bool:
    """
    Exact match duplicate detection.
    Returns True if this exact text has been posted before.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT 1 FROM posts WHERE content = ?", (text,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def is_too_similar(
    db_path: str,
    text: str,
    threshold: float = 0.82,
    lookback: int = 50
) -> bool:
    """
    🔥 PRODUCTION-READY semantic similarity guard.
    
    Blocks posts that are too similar to recent ones.
    Uses SequenceMatcher (stdlib) - no OpenAI dependency.
    
    Args:
        db_path: Path to SQLite database
        text: New post text to check
        threshold: Similarity ratio (0–1). 0.82 = 82% similar
        lookback: Number of recent posts to compare against
    
    Returns:
        True if text is too similar to a recent post
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        SELECT content
        FROM posts
        ORDER BY id DESC
        LIMIT ?
    """, (lookback,))

    rows = c.fetchall()
    conn.close()

    for (old_text,) in rows:
        ratio = SequenceMatcher(None, text, old_text).ratio()
        if ratio >= threshold:
            return True

    return False


# =========================
# SAVE + LOGGING
# =========================

def save_post(db_path: str, text: str):
    """
    Save a successfully posted message.
    Uses INSERT OR IGNORE to handle race conditions.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO posts (content, created_at) VALUES (?, ?)",
        (text, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def log_run(
    db_path: str,
    page_name: str,
    page_id: str,
    mode: str,
    pillar: str,
    message: str,
    fb_post_id: str | None,
    success: bool,
    error_code: str | None = None,
    error_message: str | None = None,
    prompt_version: str | None = None  # 🔥 NEW - but optional
):
    """
    🔥 UPGRADED: Now tracks prompt version for debugging and A/B testing.
    
    Log every run attempt (success or failure).
    This creates the audit trail for analytics.
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if prompt_version column exists
    c.execute("PRAGMA table_info(run_logs)")
    columns = [row[1] for row in c.fetchall()]
    has_prompt_version = 'prompt_version' in columns

    if has_prompt_version:
        # New schema with prompt_version
        c.execute("""
            INSERT INTO run_logs
            (ts, page_name, page_id, mode, pillar, message_len, fb_post_id, 
             success, error_code, error_message, prompt_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            page_name,
            page_id,
            mode,
            pillar,
            len(message),
            fb_post_id,
            1 if success else 0,
            error_code,
            error_message,
            prompt_version
        ))
    else:
        # Old schema without prompt_version (backward compatible)
        c.execute("""
            INSERT INTO run_logs
            (ts, page_name, page_id, mode, pillar, message_len, fb_post_id, 
             success, error_code, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            page_name,
            page_id,
            mode,
            pillar,
            len(message),
            fb_post_id,
            1 if success else 0,
            error_code,
            error_message
        ))

    conn.commit()
    conn.close()


# =========================
# CSV EXPORT
# =========================

def export_csv(db_path: str, csv_path: str):
    """
    Export run logs to CSV for analytics.
    Includes all fields including prompt_version if it exists.
    """
    import csv
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if prompt_version column exists
    c.execute("PRAGMA table_info(run_logs)")
    columns = [row[1] for row in c.fetchall()]
    has_prompt_version = 'prompt_version' in columns

    if has_prompt_version:
        c.execute("""
            SELECT ts, page_name, page_id, mode, pillar, message_len,
                   fb_post_id, success, error_code, error_message, prompt_version
            FROM run_logs
            ORDER BY id DESC
        """)
        
        header = [
            "ts", "page_name", "page_id", "mode", "pillar",
            "message_len", "fb_post_id", "success",
            "error_code", "error_message", "prompt_version"
        ]
    else:
        c.execute("""
            SELECT ts, page_name, page_id, mode, pillar, message_len,
                   fb_post_id, success, error_code, error_message
            FROM run_logs
            ORDER BY id DESC
        """)
        
        header = [
            "ts", "page_name", "page_id", "mode", "pillar",
            "message_len", "fb_post_id", "success",
            "error_code", "error_message"
        ]

    rows = c.fetchall()
    conn.close()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# =========================
# ANALYTICS HELPERS (NEW)
# =========================

def get_success_rate(db_path: str, page_name: str = None, days: int = 7) -> dict:
    """
    🔥 NEW: Calculate success rate for analytics dashboard.
    
    Args:
        db_path: Path to SQLite database
        page_name: Optional - filter by specific page
        days: Look back this many days
    
    Returns:
        dict with total, success, failure counts and rate
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    from datetime import timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    if page_name:
        c.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(success) as successes
            FROM run_logs
            WHERE page_name = ? AND ts > ?
        """, (page_name, cutoff))
    else:
        c.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(success) as successes
            FROM run_logs
            WHERE ts > ?
        """, (cutoff,))
    
    total, successes = c.fetchone()
    conn.close()
    
    if total == 0:
        return {"total": 0, "successes": 0, "failures": 0, "rate": 0.0}
    
    successes = successes or 0
    failures = total - successes
    rate = (successes / total) * 100
    
    return {
        "total": total,
        "successes": successes,
        "failures": failures,
        "rate": round(rate, 2)
    }


def get_error_breakdown(db_path: str, days: int = 7) -> list:
    """
    🔥 NEW: Get breakdown of error types for troubleshooting.
    
    Returns:
        List of (error_code, count) tuples
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    from datetime import timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    c.execute("""
        SELECT error_code, COUNT(*) as count
        FROM run_logs
        WHERE success = 0 AND ts > ? AND error_code IS NOT NULL
        GROUP BY error_code
        ORDER BY count DESC
    """, (cutoff,))
    
    rows = c.fetchall()
    conn.close()
    
    return rows


def get_posting_cadence(db_path: str, page_name: str, days: int = 30) -> dict:
    """
    🔥 NEW: Analyze actual posting frequency vs expected.
    
    Returns:
        dict with posts_per_day breakdown
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    from datetime import timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    c.execute("""
        SELECT DATE(ts) as post_date, COUNT(*) as count
        FROM run_logs
        WHERE page_name = ? AND success = 1 AND ts > ?
        GROUP BY DATE(ts)
        ORDER BY post_date DESC
    """, (page_name, cutoff))
    
    rows = c.fetchall()
    conn.close()
    
    if not rows:
        return {"avg_posts_per_day": 0, "days_with_posts": 0, "total_days": days}
    
    days_with_posts = len(rows)
    total_posts = sum(count for _, count in rows)
    avg = total_posts / days if days > 0 else 0
    
    return {
        "avg_posts_per_day": round(avg, 2),
        "days_with_posts": days_with_posts,
        "total_days": days,
        "total_posts": total_posts
    }
