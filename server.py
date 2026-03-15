"""
KV Systems Agent — On-Demand API Server
Run with: uvicorn server:app --port 7861 --reload
"""

from __future__ import annotations

import os
import json
import threading
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Load .env before anything
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel

from config import LOG_DB_PATH, PAGES_JSON_PATH
from agent import run_for_page, load_pages_config
from logger import init_db, get_success_rate, get_error_breakdown

app = FastAPI(title="KV Systems On-Demand API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# =============================================================================
# JOB TRACKING
# =============================================================================

_jobs: Dict[str, Dict[str, Any]] = {}
_jobs_lock = threading.Lock()


def _new_job(job_id: str, description: str) -> Dict:

    job = {
        "id": job_id,
        "description": description,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "finished_at": None,
        "results": [],
        "error": None,
    }

    with _jobs_lock:
        _jobs[job_id] = job

    return job


def _finish_job(job_id: str, results: list, error: str = None):

    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id]["status"] = "error" if error else "done"
            _jobs[job_id]["finished_at"] = datetime.utcnow().isoformat()
            _jobs[job_id]["results"] = results
            _jobs[job_id]["error"] = error


# =============================================================================
# BACKGROUND WORKER
# =============================================================================

def _post_worker(job_id: str, pages: List[dict]):

    import io
    import sys as _sys

    results = []

    try:

        init_db(LOG_DB_PATH)

        for page in pages:

            name = page.get("client_name") or page.get("name", "Unknown")
            ppr = int(page.get("posts_per_run", 1))

            page_copy = {**page}
            page_copy["features"] = {**page.get("features", {}), "auto_posting": True}

            buf = io.StringIO()

            old_stdout = _sys.stdout
            _sys.stdout = buf

            try:
                run_for_page(page_copy, posts_per_run=ppr)

            except Exception as e:

                results.append({
                    "client": name,
                    "status": "error",
                    "error": str(e),
                    "output": buf.getvalue(),
                })

                continue

            finally:

                _sys.stdout = old_stdout

            output = buf.getvalue()

            try:

                conn = sqlite3.connect(LOG_DB_PATH)
                c = conn.cursor()

                c.execute("""
                SELECT success, fb_post_id, error_code, error_message
                FROM run_logs
                WHERE page_name = ?
                ORDER BY id DESC LIMIT 1
                """, (name,))

                row = c.fetchone()
                conn.close()

                if row:

                    success, fb_post_id, err_code, err_msg = row

                    results.append({
                        "client": name,
                        "status": "success" if success else "failed",
                        "fb_post_id": fb_post_id,
                        "error": err_msg,
                        "output": output,
                    })

                else:

                    results.append({
                        "client": name,
                        "status": "no_log",
                        "output": output
                    })

            except Exception as db_err:

                results.append({
                    "client": name,
                    "status": "unknown",
                    "output": output,
                    "error": str(db_err)
                })

        _finish_job(job_id, results)

    except Exception as e:

        _finish_job(job_id, results, error=str(e))


# =============================================================================
# SCHEMAS
# =============================================================================

class PostClientRequest(BaseModel):
    name: str


class SaveConfigRequest(BaseModel):
    config: Dict[str, Any]


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": "kv-agent-server",
        "version": "1.0"
    }


@app.get("/api/config")
def get_config():

    try:

        with open(PAGES_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    except FileNotFoundError:

        raise HTTPException(status_code=404, detail="pages.json not found")


@app.put("/api/config")
def save_config(req: SaveConfigRequest):

    try:

        with open(PAGES_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(req.config, f, indent=2)

        return {"status": "saved"}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):

    with _jobs_lock:
        job = _jobs.get(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.get("/api/clients")
def list_clients():

    cfg = load_pages_config(PAGES_JSON_PATH)

    pages = cfg.get("pages", [])

    clients = []

    for p in pages:

        name = p.get("client_name") or p.get("name")

        clients.append({
            "name": name,
            "page_id": p.get("page_id"),
            "industry": p.get("brand", {}).get("industry", "unknown"),
            "auto_posting": p.get("features", {}).get("auto_posting", True)
        })

    return {
        "clients": clients,
        "total": len(clients)
    }


@app.post("/api/post/client")
def post_client(req: PostClientRequest, background_tasks: BackgroundTasks):

    cfg = load_pages_config(PAGES_JSON_PATH)

    pages = cfg.get("pages", [])

    match = None

    for p in pages:

        name = p.get("client_name") or p.get("name")

        if name.lower() == req.name.lower():
            match = p
            break

    if not match:
        raise HTTPException(status_code=404, detail="Client not found")

    job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    _new_job(job_id, f"post {req.name}")

    background_tasks.add_task(_post_worker, job_id, [match])

    return {"job_id": job_id}


@app.post("/api/post/all")
def post_all(background_tasks: BackgroundTasks):

    cfg = load_pages_config(PAGES_JSON_PATH)

    pages = cfg.get("pages", [])

    job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    _new_job(job_id, "post all")

    background_tasks.add_task(_post_worker, job_id, pages)

    return {"job_id": job_id}


@app.get("/api/jobs")
def list_jobs():

    with _jobs_lock:
        jobs = list(_jobs.values())

    return {"jobs": jobs}


# =============================================================================
# DASHBOARD
# =============================================================================

@app.get("/", response_class=HTMLResponse)
def dashboard():

    return """
    <html>
    <head>

    <title>KV Systems Console</title>

    <style>

    body{
        background:#0f172a;
        color:white;
        font-family:Arial;
        padding:40px;
    }

    h1{
        color:#38bdf8;
    }

    button{
        padding:10px;
        margin:5px;
        background:#22c55e;
        border:none;
        border-radius:6px;
        color:white;
        cursor:pointer;
    }

    .card{
        background:#1e293b;
        padding:20px;
        margin:15px 0;
        border-radius:8px;
    }

    </style>

    </head>

    <body>

    <h1>KV Systems Social Agent</h1>

    <div class="card">

    <h3>System</h3>

    <a href="/api/health">Health Check</a><br>
    <a href="/api/config">View Config</a><br>
    <a href="/api/jobs">Jobs</a><br>

    </div>


    <div class="card">

    <h3>Run Agent</h3>

    <button onclick="postAll()">Post For All Clients</button>

    </div>


    <div class="card">

    <h3>Clients</h3>

    <ul id="clients"></ul>

    </div>


<script>

async function loadClients(){

const res = await fetch('/api/clients')
const data = await res.json()

const list = document.getElementById('clients')

list.innerHTML=""

data.clients.forEach(c=>{

const li=document.createElement('li')

li.innerHTML = `
${c.name}
<button onclick="runClient('${c.name}')">Post Now</button>
`

list.appendChild(li)

})

}

async function runClient(name){

await fetch('/api/post/client',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({name:name})
})

alert("Posting started for "+name)

}

async function postAll(){

await fetch('/api/post/all',{method:'POST'})

alert("Posting started")

}

loadClients()

</script>


</body>
</html>
"""

# =============================================================================
# CONTENT STUDIO ROUTES
# =============================================================================

class GeneratePostRequest(BaseModel):
    industry: str = "trading"
    page_name: Optional[str] = ""
    content_type: Optional[str] = "educational"
    topic: Optional[str] = None

class GenerateViralRequest(BaseModel):
    industry: str = "trading"
    page_name: Optional[str] = ""
    topic: Optional[str] = None

class GenerateLeadRequest(BaseModel):
    industry: str = "trading"
    page_name: Optional[str] = ""
    keyword: Optional[str] = "INFO"
    service: Optional[str] = None

class CalendarRequest(BaseModel):
    industry: str = "trading"
    page_name: Optional[str] = ""

class CommentRequest(BaseModel):
    industry: str = "trading"
    page_name: Optional[str] = ""
    comment: str = ""
    post_context: Optional[str] = None


def _call_openai(system_prompt: str, user_prompt: str, temperature: float = 0.85) -> str:
    """Shared OpenAI call for all studio endpoints."""
    from openai import OpenAI
    from config import OPENAI_API_KEY, OPENAI_MODEL
    client = OpenAI(api_key=OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()


def _industry_voice(industry: str, page_name: str) -> str:
    """Return a short voice description based on industry."""
    voices = {
        "trading":    "You are an experienced market operator writing sharp, calm Facebook posts for traders.",
        "systems":    "You are a builder-mindset trader who created systems after discretion failed under pressure.",
        "lawn":       "You are Contee's Lawn Care — a local lawn pro writing practical tips homeowners share with neighbors.",
        "restaurant": "You are a local restaurant writing warm, appetizing Facebook content that drives foot traffic.",
        "fitness":    "You are a fitness professional writing motivating but practical content for health-conscious adults.",
        "realestate": "You are a real estate professional writing clear, trust-building content for buyers and sellers.",
        "local":      "You are a local business writing friendly, useful content for your community.",
        "tax":        "You are a tax professional writing clear, reassuring content that reduces financial anxiety.",
    }
    base = voices.get(industry, voices["local"])
    if page_name:
        base += f" Writing for: {page_name}."
    return base


@app.post("/api/generate")
def generate_post(req: GeneratePostRequest):
    """Standard post — educational, promotional, testimonial, etc."""
    try:
        voice = _industry_voice(req.industry, req.page_name or "")
        topic_line = f"Topic focus: {req.topic}" if req.topic else "Choose the most relevant topic for the audience."

        system = f"""{voice}

RULES:
- Write ONE Facebook post only
- No hashtags
- No hype or empty motivation
- Be specific and useful
- Match the content type: {req.content_type}
- Length: 2-5 lines max
- Return only the post text, nothing else"""

        user = f"""Content type: {req.content_type}
Industry: {req.industry}
{topic_line}

Write the post now."""

        text = _call_openai(system, user)

        # Determine pillar label
        pillar_map = {
            "educational": "education",
            "promotional": "promotion",
            "testimonial": "social_proof",
            "seasonal": "seasonal",
            "engagement_question": "engagement",
        }
        pillar = pillar_map.get(req.content_type or "educational", req.content_type or "education")

        return {
            "text": text,
            "type": req.content_type,
            "pillar": pillar,
            "industry": req.industry,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/viral")
def generate_viral(req: GenerateViralRequest):
    """High engagement / viral style post."""
    try:
        voice = _industry_voice(req.industry, req.page_name or "")
        topic_line = f"Topic: {req.topic}" if req.topic else "Choose a counter-intuitive, shareable angle."

        system = f"""{voice}

VIRAL POST RULES:
- HARD LIMIT: 1-3 lines MAXIMUM
- One counter-intuitive insight — drop it and stop writing
- Must make someone think "nobody says this out loud"
- Zero setup, zero follow-up, zero explanation
- No hashtags
- No hype
- Return only the post text, nothing else"""

        user = f"""{topic_line}
Industry: {req.industry}

Write a viral-style post now."""

        text = _call_openai(system, user, temperature=0.92)

        return {
            "text": text,
            "type": "viral",
            "pillar": "high_engagement",
            "industry": req.industry,
            "format": "viral_punch",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate/lead")
def generate_lead(req: GenerateLeadRequest):
    """Lead generation post with keyword CTA."""
    try:
        voice = _industry_voice(req.industry, req.page_name or "")
        keyword = req.keyword or "INFO"
        service_line = f"Service: {req.service}" if req.service else ""

        system = f"""{voice}

LEAD GEN POST RULES:
- Write ONE Facebook post
- Build curiosity or value in 2-3 lines
- Final line: tell people to comment the keyword "{keyword}" to get more info
- Keyword must appear in the CTA naturally (e.g. "Comment '{keyword}' below")
- No hashtags
- No hard selling
- Sound helpful, not pushy
- Return only the post text, nothing else"""

        user = f"""Keyword CTA: {keyword}
{service_line}
Industry: {req.industry}

Write the lead gen post now."""

        text = _call_openai(system, user)

        return {
            "text": text,
            "type": "lead_gen",
            "pillar": "lead_generation",
            "keyword": keyword,
            "industry": req.industry,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calendar/generate")
def generate_calendar(req: CalendarRequest):
    """Generate a 30-day content calendar."""
    try:
        voice = _industry_voice(req.industry, req.page_name or "")

        system = f"""{voice}

Generate a 30-day Facebook content calendar.
Return ONLY valid JSON array, no markdown, no explanation.
Format: [{{"day":1,"type":"educational","topic":"topic here","post_text":"full post here"}}, ...]
Types to rotate: educational, promotional, engagement, testimonial, viral, lead_gen, rest
- rest days have no post_text (empty string)
- Include 4-5 rest days spread through the month
- Viral posts: 1-3 lines max
- Educational posts: 3-5 lines
- Total: exactly 30 entries"""

        user = f"""Industry: {req.industry}
Page: {req.page_name or "General"}

Generate the 30-day calendar now."""

        raw = _call_openai(system, user, temperature=0.80)

        # Strip markdown fences if present
        clean = raw.replace("```json", "").replace("```", "").strip()
        days = json.loads(clean)

        return {"days": days, "industry": req.industry, "total": len(days)}

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Calendar parse error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/comments/suggest")
def suggest_comment_reply(req: CommentRequest):
    """Suggest 3 reply options for a customer comment."""
    try:
        voice = _industry_voice(req.industry, req.page_name or "")
        context_line = f"Post context: {req.post_context}" if req.post_context else ""

        system = f"""{voice}

Generate exactly 3 reply options for a customer comment on a Facebook post.
Return ONLY valid JSON array, no markdown:
[{{"tone":"Professional","text":"reply here"}},{{"tone":"Friendly","text":"reply here"}},{{"tone":"Direct","text":"reply here"}}]
- Each reply: 1-3 sentences max
- No hashtags
- Sound human, not robotic
- Match brand voice"""

        user = f"""Customer comment: "{req.comment}"
{context_line}
Industry: {req.industry}

Generate 3 reply options now."""

        raw = _call_openai(system, user, temperature=0.80)
        clean = raw.replace("```json", "").replace("```", "").strip()
        replies = json.loads(clean)

        return {
            "replies": replies,
            "comment": req.comment,
            "industry": req.industry,
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Reply parse error — try again")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ADDITIONAL UTILITY ROUTES (used by console tabs)
# =============================================================================

@app.get("/api/logs")
def get_logs(limit: int = 30):
    """Return recent run logs for the Activity tab."""
    try:
        conn = sqlite3.connect(LOG_DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT page_name, page_id, mode, pillar, success,
                   fb_post_id, error_code, error_message, ts
            FROM run_logs
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = c.fetchall()
        conn.close()
        logs = []
        for row in rows:
            logs.append({
                "page_name":     row[0],
                "page_id":       row[1],
                "mode":          row[2],
                "pillar":        row[3],
                "success":       bool(row[4]),
                "fb_post_id":    row[5],
                "error_code":    row[6],
                "error_message": row[7],
                "ts":            row[8],
            })
        return {"logs": logs}
    except Exception as e:
        return {"logs": [], "error": str(e)}


@app.get("/api/analytics/summary")
def analytics_summary():
    """Return analytics data for the Analytics tab."""
    try:
        conn = sqlite3.connect(LOG_DB_PATH)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM run_logs")
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM run_logs WHERE success=1")
        success = c.fetchone()[0]

        c.execute("""
            SELECT COUNT(*) FROM run_logs
            WHERE ts >= datetime('now', '-7 days')
        """)
        this_week = c.fetchone()[0]

        c.execute("""
            SELECT strftime('%Y-%m-%d', ts) as day, COUNT(*) as cnt
            FROM run_logs
            WHERE ts >= datetime('now', '-30 days')
            GROUP BY day ORDER BY day
        """)
        last_30 = [{"date": r[0], "count": r[1]} for r in c.fetchall()]

        c.execute("""
            SELECT page_name,
                   COUNT(*) as total,
                   SUM(success) as ok
            FROM run_logs GROUP BY page_name
        """)
        by_page = []
        for r in c.fetchall():
            rate = round((r[2] / r[1]) * 100) if r[1] else 0
            by_page.append({"page": r[0], "total": r[1], "success_rate": rate})

        c.execute("""
            SELECT pillar, COUNT(*) as cnt
            FROM run_logs WHERE pillar != ''
            GROUP BY pillar ORDER BY cnt DESC LIMIT 10
        """)
        top_pillars = [{"pillar": r[0], "count": r[1]} for r in c.fetchall()]

        c.execute("""
            SELECT strftime('%w', ts) as dow, COUNT(*) as cnt
            FROM run_logs GROUP BY dow
        """)
        dow_map = {"0":"Sun","1":"Mon","2":"Tue","3":"Wed","4":"Thu","5":"Fri","6":"Sat"}
        by_dow = {dow_map.get(r[0], r[0]): r[1] for r in c.fetchall()}

        conn.close()

        rate = round((success / total) * 100) if total else 0

        return {
            "total_posts":        total,
            "successful_posts":   success,
            "success_rate":       rate,
            "posts_this_week":    this_week,
            "posts_last_30_days": last_30,
            "posts_by_page":      by_page,
            "top_pillars":        top_pillars,
            "posts_by_day_of_week": by_dow,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/diagnose")
def diagnose():
    """System health check for Activity tab diagnostics panel."""
    from config import OPENAI_API_KEY
    cfg = load_pages_config(PAGES_JSON_PATH)
    pages = cfg.get("pages", [])
    clients = []
    for p in pages:
        name = p.get("client_name") or p.get("name", "Unnamed")
        has_token = bool(p.get("page_token", "").strip())
        has_id = bool(p.get("page_id", "").strip())
        clients.append({
            "name": name,
            "ready": has_token and has_id,
            "missing": [] if (has_token and has_id) else
                       (["token"] if not has_token else []) + (["page_id"] if not has_id else []),
        })
    return {
        "overall_ok": bool(OPENAI_API_KEY) and all(c["ready"] for c in clients),
        "openai_key": bool(OPENAI_API_KEY),
        "clients": clients,
    }


# =============================================================================
# LEAD CAPTURE ROUTES
# =============================================================================

from leads import (
    init_leads_db, migrate_leads_db, get_leads, get_lead_detail,
    update_lead, get_leads_stats,
    scan_page_for_leads, send_manual_dm,
)

# Ensure leads tables exist and schema is current on startup
try:
    init_leads_db(LOG_DB_PATH)
    migrate_leads_db(LOG_DB_PATH)
except Exception as _e:
    print(f"DB init warning: {_e}")


class LeadUpdateRequest(BaseModel):
    status:            Optional[str] = None
    phone:             Optional[str] = None
    notes:             Optional[str] = None
    service_requested: Optional[str] = None
    location:          Optional[str] = None
    email:             Optional[str] = None

class LeadMessageRequest(BaseModel):
    message:   str
    page_name: str

class ScanRequest(BaseModel):
    keywords: Optional[List[str]] = ["INFO", "YES", "FREE", "QUOTE", "JOIN"]


@app.get("/api/leads")
def list_leads_route():
    try:
        from leads import get_leads as _get_leads
        leads = _get_leads(LOG_DB_PATH)
        return {"leads": leads}
    except Exception as e:
        import traceback
        print(f"list_leads error: {traceback.format_exc()}")
        return {"leads": [], "error": str(e)}


@app.get("/api/leads/stats")
def get_lead_stats_route():
    try:
        return get_leads_stats(LOG_DB_PATH)
    except Exception as e:
        return {"total_leads": 0, "by_status": {}, "dm_sent": 0, "error": str(e)}


@app.get("/api/leads/{lead_id}")
def get_lead_route(lead_id: int):
    lead = get_lead_detail(LOG_DB_PATH, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.put("/api/leads/{lead_id}")
def update_lead_route(lead_id: int, req: LeadUpdateRequest):
    fields = req.dict(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    update_lead(LOG_DB_PATH, lead_id, fields)
    return {"status": "updated"}


@app.post("/api/leads/{lead_id}/message")
def send_lead_message(lead_id: int, req: LeadMessageRequest):
    try:
        cfg = load_pages_config(PAGES_JSON_PATH)
        pages = cfg.get("pages", [])
        result = send_manual_dm(lead_id, req.message, req.page_name, pages, LOG_DB_PATH)

        if "error" in result:
            err = result["error"]
            # Parse nested Facebook error objects
            if isinstance(err, dict):
                fb_msg = err.get("message", str(err))
                fb_code = err.get("code", "")
                raise HTTPException(status_code=400, detail=f"Facebook error [{fb_code}]: {fb_msg}")
            raise HTTPException(status_code=400, detail=str(err))

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/leads/check-comments")
def check_comments(req: ScanRequest):
    """
    Scan all lead-capture-enabled pages for keyword comments and reactions.
    """
    import traceback
    try:
        cfg  = load_pages_config(PAGES_JSON_PATH)
        pages = [
            p for p in cfg.get("pages", [])
            if p.get("features", {}).get("lead_capture", False)
        ]

        if not pages:
            return {
                "status": "no_pages",
                "message": "No pages have lead_capture enabled. Enable it in the Clients tab."
            }

        keywords = req.keywords or ["INFO", "YES", "FREE", "QUOTE", "JOIN"]
        total_new = 0
        page_results = []

        for page in pages:
            name = page.get("client_name") or page.get("name", "Unknown")
            try:
                new = scan_page_for_leads(
                    page=page,
                    keywords=keywords,
                    scan_reactions=True,
                    db_path=LOG_DB_PATH,
                )
                total_new += len(new)
                page_results.append({"page": name, "new_leads": len(new), "status": "ok"})
            except Exception as page_err:
                tb = traceback.format_exc()
                print(f"  ERROR scanning {name}: {tb}")
                page_results.append({"page": name, "status": "error", "error": str(page_err), "traceback": tb})

        return {
            "status": "complete",
            "pages_scanned": len(pages),
            "new_leads": total_new,
            "details": page_results,
        }
    except Exception as e:
        tb = traceback.format_exc()
        print(f"  FATAL check_comments error: {tb}")
        raise HTTPException(status_code=500, detail=f"{str(e)} | {tb}")


# =============================================================================
# DEBUG ROUTE — remove after testing
# =============================================================================

@app.get("/api/debug/leads-scan")
def debug_leads_scan():
    """
    Diagnostic endpoint — shows exactly what the scanner sees.
    Visit http://localhost:7861/api/debug/leads-scan in your browser.
    """
    import requests as req_lib
    from config import FB_GRAPH_VERSION

    cfg   = load_pages_config(PAGES_JSON_PATH)
    pages = cfg.get("pages", [])
    report = []

    for p in pages:
        name    = p.get("client_name") or p.get("name", "Unnamed")
        page_id = p.get("page_id", "")
        token   = p.get("page_token", "")
        lc_flag = p.get("features", {}).get("lead_capture", False)
        kw      = p.get("lead_keywords", [])

        entry = {
            "page":           name,
            "lead_capture":   lc_flag,
            "lead_keywords":  kw,
            "page_id":        page_id,
            "token_present":  bool(token),
            "posts":          [],
            "error":          None,
        }

        if not lc_flag:
            entry["error"] = "lead_capture is FALSE — enable it in Clients tab and Save"
            report.append(entry)
            continue

        if not token or not page_id:
            entry["error"] = "Missing token or page_id"
            report.append(entry)
            continue

        # Try fetching posts
        try:
            url = f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{page_id}/posts"
            r = req_lib.get(url, params={
                "access_token": token,
                "fields": "id,message,created_time",
                "limit": 5,
            }, timeout=10)
            data = r.json()

            if "error" in data:
                entry["error"] = f"FB API error: {data['error'].get('message')}"
                report.append(entry)
                continue

            posts = data.get("data", [])
            entry["posts_found"] = len(posts)

            for post in posts[:3]:
                post_id = post.get("id", "")
                # Fetch comments for each post
                cr = req_lib.get(
                    f"https://graph.facebook.com/{FB_GRAPH_VERSION}/{post_id}/comments",
                    params={"access_token": token, "fields": "id,message,from", "limit": 10},
                    timeout=10
                )
                comments = cr.json().get("data", [])
                entry["posts"].append({
                    "post_id":       post_id,
                    "message":       (post.get("message") or "")[:80],
                    "comments_count": len(comments),
                    "comments":      [
                        {
                            "from": c.get("from", {}).get("name"),
                            "text": c.get("message", "")[:60],
                            "id":   c.get("id"),
                        }
                        for c in comments
                    ],
                })

        except Exception as e:
            entry["error"] = str(e)

        report.append(entry)

    return {"debug": report}


# =============================================================================
# AI REPLY SUGGESTIONS — uses OpenAI key from .env
# =============================================================================

class ReplySuggestionsRequest(BaseModel):
    system_prompt: str
    user_prompt:   str
    page_name:     Optional[str] = ""
    industry:      Optional[str] = "general"
    keyword:       Optional[str] = ""
    comment:       Optional[str] = ""
    provider:      Optional[str] = "openai"   # "openai" or "anthropic"
    anthropic_key: Optional[str] = ""         # passed from browser if user chooses Anthropic


@app.post("/api/generate/reply-suggestions")
def generate_reply_suggestions(req: ReplySuggestionsRequest):
    """
    Generate AI reply suggestions.
    provider="openai"    — uses OPENAI_API_KEY from .env (default)
    provider="anthropic" — uses anthropic_key passed from browser
                           (or ANTHROPIC_API_KEY from .env if set)
    """
    import json as _json

    try:
        raw = ""

        # ── ANTHROPIC ────────────────────────────────────────────────────────
        if req.provider == "anthropic":
            anthropic_key = (
                req.anthropic_key.strip()
                or os.getenv("ANTHROPIC_API_KEY", "")
            )
            if not anthropic_key:
                raise HTTPException(
                    status_code=400,
                    detail="No Anthropic API key provided. Add ANTHROPIC_API_KEY to .env or enter it in Settings."
                )
            import requests as _req
            r = _req.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type":      "application/json",
                    "x-api-key":         anthropic_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model":      "claude-sonnet-4-20250514",
                    "max_tokens": 600,
                    "system":     req.system_prompt,
                    "messages":   [{"role": "user", "content": req.user_prompt}],
                },
                timeout=20,
            )
            data = r.json()
            if "error" in data:
                raise HTTPException(status_code=400, detail=data["error"].get("message", "Anthropic error"))
            raw = data["content"][0]["text"].strip()

        # ── OPENAI (default) ─────────────────────────────────────────────────
        else:
            from openai import OpenAI
            from config import OPENAI_API_KEY, OPENAI_MODEL
            client = OpenAI(api_key=OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": req.system_prompt},
                    {"role": "user",   "content": req.user_prompt},
                ],
                temperature=0.82,
            )
            raw = resp.choices[0].message.content.strip()

        clean   = raw.replace("```json", "").replace("```", "").strip()
        replies = _json.loads(clean)
        return {"replies": replies, "provider": req.provider}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))