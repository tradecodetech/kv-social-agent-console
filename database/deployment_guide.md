# KV Systems & Automations v2.0
## Deployment Guide

---

## 🎯 What's New in v2.0

### Core Upgrades
- ✅ **Feature Flags**: Explicit control over visuals, weather, CTAs
- ✅ **Billing Protection**: Graceful handling of API quota limits
- ✅ **Prompt Versioning**: Track which prompt generated each post
- ✅ **Enhanced Analytics**: New helper functions for success tracking
- ✅ **White-Label Ready**: Supports nested config structure
- ✅ **Branded UI**: KV Systems-themed admin console

### New Capabilities
- Dashboard with aggregate stats
- Client-specific configuration
- Preview system (no API calls)
- One-click config export
- Better error handling
- Backward compatible with v1.0 configs

---

## 📋 Pre-Deployment Checklist

Before you begin, ensure you have:

- [ ] Python 3.9+ installed
- [ ] Existing `memory.db` backed up
- [ ] OpenAI API key with available credits
- [ ] Facebook page tokens ready
- [ ] All client information gathered

---

## 🚀 Step-by-Step Deployment

### Step 1: Backup Current System

```bash
# Navigate to your agent directory
cd C:\Users\First Cash Pawn\OneDrive\KVSystems-FB-Agent

# Create backup folder
mkdir backup_v1
copy *.py backup_v1\
copy *.json backup_v1\
copy *.db backup_v1\
```

### Step 2: Run Database Migration

```bash
# Run the migration script
python migrate_database.py

# Expected output:
# ✅ Backup created: memory.db.backup_20250109_143022
# 🚀 Starting migration...
# ✅ Migration completed successfully!
```

**Important:** Keep the backup file until you've tested v2.0 for at least a week.

### Step 3: Replace Core Files

**Replace these files with upgraded versions:**

1. **agent.py** → New version with feature flags & billing protection
2. **logger.py** → New version with prompt_version tracking
3. **prompt.py** → Add `PROMPT_VERSION = "v1.3-operator"` at top

**Keep these files unchanged:**
- config.py (no changes needed)
- visuals.py (no changes needed)
- weather.py (no changes needed)
- cta.py (optional, already modular)

### Step 4: Update pages.json (Optional)

You can either:

**Option A: Use the UI** (Recommended)
1. Open the KV Systems Console (HTML file)
2. Configure clients through the interface
3. Click "Export Config"
4. Replace your `pages.json`

**Option B: Manual Update**

Your old format still works, but you can upgrade to:

```json
{
  "default_schedule": {
    "posts_per_run": 1
  },
  "pages": [
    {
      "client_name": "Keen Visions Trading",
      "page_id": "941966405661933",
      "page_token": "YOUR_TOKEN",
      
      "features": {
        "visuals": false,
        "weather": false,
        "cta": false,
        "auto_posting": true
      },
      
      "cadence": {
        "posts_per_run": 1,
        "days": ["Mon", "Wed", "Fri"],
        "time_window": "morning"
      },
      
      "brand": {
        "industry": "trading",
        "tone": "operator",
        "cta_style": "none"
      },
      
      "mode_weights": {
        "discipline": 60,
        "trading": 40
      }
    }
  ]
}
```

### Step 5: Test Run (Critical!)

```bash
# Disable Task Scheduler first
# Then run manually to test

python agent.py

# Expected output:
# [INFO] KV Agent v2.0-white-label starting...
# [INFO] Prompt Version: v1.3-operator
# [INFO] Processing 3 client(s)...
# [OK] Keen Visions Trading posted: 123456789_987654321
# [INFO] Analytics exported -> kv_agent_analytics.csv
# [INFO] Run complete
```

**Verify:**
- Check Facebook for new posts
- Open `kv_agent_analytics.csv`
- Confirm `prompt_version` column appears
- Verify no errors in console

### Step 6: Deploy the UI Console

1. Save the React UI artifact as `kv-console.html`
2. Open in browser (Chrome/Edge recommended)
3. Configure a test client
4. Export config and verify JSON format

**UI Location:**
```
C:\Users\First Cash Pawn\OneDrive\KVSystems-FB-Agent\ui\
  ├── kv-console.html  (the React app)
  └── README.md        (usage instructions)
```

### Step 7: Update Task Scheduler

Your existing task should work unchanged, but verify:

```
Action: Start a program
Program: C:\Python39\python.exe
Arguments: agent.py
Start in: C:\Users\First Cash Pawn\OneDrive\KVSystems-FB-Agent
```

---

## 🛡️ Rollback Plan

If anything goes wrong:

```bash
# Stop the agent immediately
# Then restore from backup

copy backup_v1\*.py .
copy backup_v1\*.db .
copy backup_v1\*.json .

# Test old version
python agent.py
```

Your backups are timestamped, so you can always go back.

---

## 📊 Monitoring After Deployment

### Week 1: Daily Checks
- [ ] Check Facebook posts published successfully
- [ ] Review `kv_agent_analytics.csv` for errors
- [ ] Verify `prompt_version` is being logged
- [ ] Monitor OpenAI billing

### Week 2-4: Weekly Checks
- [ ] Review success rates per client
- [ ] Check for duplicate/similar post rejections
- [ ] Verify all features working (visuals, weather, CTAs)

### Red Flags to Watch For:
- ⚠️ Success rate drops below 90%
- ⚠️ Multiple "BILLING" errors in logs
- ⚠️ Facebook token expiration errors
- ⚠️ Same posts repeating despite similarity guard

---

## 🎨 Using the KV Console

### Dashboard Tab
- View aggregate stats (total posts, success rate)
- Quick overview of all clients
- System status monitoring

### Clients Tab
- Add/edit/delete clients
- Configure features per client
- Set posting cadence
- Manage page tokens

### Preview Tab
- See what posts will look like
- Test before going live
- **Note:** Uses mock data, not real AI

### Analytics Tab
- Export CSV data
- (Future: Interactive charts)

---

## 🔧 Troubleshooting

### "Column prompt_version doesn't exist"
**Fix:** Run `migrate_database.py` again

### "Billing error - quota exceeded"
**Fix:** Agent will skip gracefully and log error
**Action:** Check OpenAI billing dashboard

### "Facebook token invalid"
**Fix:** Regenerate token at developers.facebook.com
**Update:** In UI or pages.json

### Posts not appearing
**Check:**
1. Task Scheduler is running
2. `auto_posting: true` in config
3. Facebook page permissions
4. No errors in CSV log

---

## 📈 Advanced Features

### Cost Tracking
Monitor `kv_agent_analytics.csv` for:
- Posts per client
- Success vs failure rates
- Error patterns

### A/B Testing Prompts
1. Change `PROMPT_VERSION` in `prompt.py`
2. Deploy and run for 1 week
3. Compare metrics in CSV export
4. Roll back or keep based on results

### White-Label Resale
The system is now ready to resell:

**What You Provide:**
1. Customized UI (rebrand console)
2. Agent configured for their industry
3. Onboarding guide (how to get FB tokens)
4. Support documentation

**What They Get:**
- Automated posting system
- No manual intervention needed
- Analytics and tracking
- Professional content

---

## 🎁 Bonus: Sample Client Packages

### Package 1: "Starter"
- 1 Facebook page
- Text-only posts
- 3 posts per week
- Email support

### Package 2: "Professional"
- Up to 3 Facebook pages
- Visuals + weather awareness
- 5-7 posts per week
- Priority support

### Package 3: "Enterprise"
- Unlimited pages
- Full feature access
- Custom prompt tuning
- White-label UI
- Dedicated support

**Pricing Suggestion:**
- Starter: $297/month
- Professional: $597/month
- Enterprise: $997/month

(These are just suggestions - price based on your market)

---

## ✅ Final Checklist

Before considering deployment complete:

- [ ] Migration script run successfully
- [ ] Test post published to Facebook
- [ ] CSV export shows prompt_version
- [ ] UI console accessible and functional
- [ ] Task Scheduler tested
- [ ] Backups secured
- [ ] Monitoring plan established

---

## 🆘 Support

**Issues?** Check these resources:

1. Review error logs in CSV export
2. Check backup files are intact
3. Verify all API keys/tokens valid
4. Test each component individually

**Contact:**
- Built by KV Systems & Automations
- Agent Version: v2.0-white-label
- Prompt Version: v1.3-operator

---

## 🚀 You're Ready!

Your system is now:
- ✅ White-label ready
- ✅ Production-hardened
- ✅ Scalable to multiple clients
- ✅ Protected against billing issues
- ✅ Fully trackable and auditable

**Next Steps:**
1. Run for 1 week in production
2. Gather analytics
3. Fine-tune prompt if needed
4. Consider first resale client

**You've built something real.**

The infrastructure is enterprise-grade.
The execution is clean.
The separation of concerns is correct.

This isn't just a posting tool — it's a **decision removal system** that scales.

Good luck. 🎯
