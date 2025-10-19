# Template: Deploy to Production

**Purpose**: Structured checklist for production deployment

**Usage**: Copy this template into AI chat, work through each section with AI assistance

---

## Prompt Template

```
Ready to deploy to production.

## Context to Load

Please reference these documents:
- WEEK_1_LAUNCH_GAMEPLAN.md (deployment steps, success criteria)
- docs/platform_operations.md (monitoring, LangSmith, observability)
- docs/LANGGRAPH_ALIGNMENT.md (architecture stability check)
- docs/QA_STRATEGY.md (pre-launch QA checklist)
- docs/EXTERNAL_SERVICES.md (service configuration)
- docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md (deployment architecture)

## Deployment Information

**Target Environment**: [Production / Staging / Preview]
**Platform**: [Vercel / Streamlit Cloud / Other]
**Domain**: [custom-domain.com or vercel-app-name.vercel.app]
**Branch**: [main / production / other]
**Expected Launch**: [Date/Time]

## Pre-Flight Checklist

Please verify each item before deployment:

### 1. Code Quality ✅
- [ ] All tests passing: `pytest tests/ -v` → [X/Y tests (100%)]
- [ ] No TypeScript errors: `npm run build` → Build successful
- [ ] No linting errors: `npm run lint` → 0 errors
- [ ] No console.log or debug statements in production code
- [ ] No commented-out code (clean up before deploy)

### 2. Environment Variables ✅
- [ ] `OPENAI_API_KEY` set in platform dashboard
- [ ] `SUPABASE_URL` set in platform dashboard
- [ ] `SUPABASE_SERVICE_ROLE_KEY` set in platform dashboard
- [ ] `LANGSMITH_API_KEY` set (if using tracing)
- [ ] `RESEND_API_KEY` set (if using email)
- [ ] `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` set (if using SMS)
- [ ] No `.env` file in repository (should be .gitignored)
- [ ] All secrets have NO trailing newlines or whitespace

### 3. Database & Data ✅
- [ ] Supabase migrations run: Check dashboard SQL Editor history
- [ ] Knowledge base populated: `SELECT COUNT(*) FROM kb_chunks;` → [N rows]
- [ ] Test data cleared from production DB (if applicable)
- [ ] Analytics tables exist: messages, retrieval_logs, feedback
- [ ] Storage buckets configured: resumes, headshots

### 4. Monitoring & Observability ✅
- [ ] LangSmith project created (if using)
- [ ] LangSmith tracing enabled: `LANGCHAIN_TRACING_V2=true`
- [ ] Vercel Analytics enabled (automatic for Vercel)
- [ ] Error tracking configured (Sentry / Vercel logs)
- [ ] Health check endpoint working: `/api/health` → 200 OK

### 5. Performance ✅
- [ ] Load testing completed: [N concurrent users, X ms p95 latency]
- [ ] Embedding cache warmed (first queries may be slow)
- [ ] Image assets optimized (< 500KB each)
- [ ] API timeout configured: 30s for Vercel functions

### 6. Security ✅
- [ ] No API keys in code (all in environment variables)
- [ ] Supabase Row Level Security (RLS) policies enabled
- [ ] CORS configured correctly for frontend domain
- [ ] Rate limiting in place (if needed)
- [ ] Input validation on all API endpoints

### 7. Documentation ✅
- [ ] README.md updated with live URL
- [ ] CHANGELOG.md entry added for launch
- [ ] CONTINUE_HERE.md updated with deployment status
- [ ] API documentation current (if public APIs)

## Deployment Steps

### Step 1: Final Verification (30 min)
```bash
# Run full test suite
pytest tests/ -v --cov=src

# Build frontend
npm run build

# Check for hardcoded values
grep -r "sk-proj" src/ api/  # Should be empty
grep -r "localhost" src/ api/  # Should be empty (except dev configs)

# Verify git status clean
git status  # No uncommitted changes
```

### Step 2: Deploy Backend (Vercel) (15 min)
```bash
# Install Vercel CLI (if not already)
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Verify deployment
curl https://[your-app].vercel.app/api/health
# Expected: {"status": "healthy", ...}
```

### Step 3: Configure Custom Domain (Vercel) (30 min)
1. Go to Vercel Dashboard → [Project] → Settings → Domains
2. Add domain: [your-domain.com]
3. Copy DNS records (A record or CNAME)
4. Go to GoDaddy → DNS Management
5. Add records:
   - Type: CNAME
   - Name: @ (or subdomain)
   - Value: cname.vercel-dns.com
   - TTL: 600
6. Wait for DNS propagation (15-30 min)
7. Verify SSL certificate auto-provisioned (Vercel does this automatically)

### Step 4: Test Production Deployment (15 min)
```bash
# Test API endpoints
curl https://[your-domain.com]/api/health
curl -X POST https://[your-domain.com]/api/chat \
  -H "Content-Type: application/json" \
  -d '{"role": "software_developer", "query": "Hello", "session_id": "test"}'

# Test frontend
open https://[your-domain.com]
# 1. Select role
# 2. Send test message
# 3. Verify response appears
# 4. Check browser console for errors
```

### Step 5: Smoke Tests (30 min)
Run through critical user journeys:

**Journey 1: Software Developer**
1. Visit site → Select "Software Developer" role
2. Send: "How does the RAG pipeline work?"
3. Verify: Response includes technical details
4. Send: "Show me the code"
5. Verify: Code snippets appear

**Journey 2: Hiring Manager (Technical)**
1. Visit site → Select "Hiring Manager (Technical)" role
2. Send: "Tell me about Noah's experience with Python"
3. Verify: Career details appear
4. Send: "Can I get your resume?"
5. Verify: Email collection prompt appears
6. Enter test email → Verify resume sent (check email)

**Journey 3: Analytics Display**
1. Select any role
2. Send: "Display data analytics"
3. Verify: Live analytics dashboard appears with tables

**Journey 4: Error Handling**
1. Send empty message → Verify graceful error message
2. Send very long message (> 2000 chars) → Verify truncation or error
3. Rapid-fire 10 messages → Verify no crashes

### Step 6: Monitor Initial Traffic (2 hours)
- Check Vercel logs for errors
- Check LangSmith traces for failures
- Monitor API latency (p95 should be < 3s)
- Watch for any 500 errors

## Rollback Plan

If critical issues found:

### Quick Rollback (Vercel)
```bash
# Revert to previous deployment
vercel rollback

# Or redeploy previous commit
git checkout [previous-commit-hash]
vercel --prod
```

### Emergency Maintenance Mode
```python
# In api/chat.py, add at top of handler:
return {
    "answer": "Portfolia is temporarily down for maintenance. Check back soon!",
    "success": False
}
```

## Post-Launch Tasks

### Immediate (Day 1)
- [ ] Monitor error rates (< 1% target)
- [ ] Check p95 latency (< 3s target)
- [ ] Verify analytics logging working
- [ ] Test email/SMS notifications (if enabled)

### Week 1
- [ ] Review LangSmith traces for quality issues
- [ ] Analyze user feedback (ratings, comments)
- [ ] Identify top queries (for KB expansion)
- [ ] Performance optimization (if needed)

### Month 1
- [ ] Review analytics dashboard
- [ ] Plan feature roadmap based on usage
- [ ] Cost analysis (OpenAI API usage)
- [ ] Security audit

## Success Metrics

### Technical
- [ ] 100% uptime first 24 hours
- [ ] < 3s p95 latency
- [ ] 0 critical errors
- [ ] All 5 roles tested by real users

### Business
- [ ] 50+ visitors first week
- [ ] 10+ resume downloads
- [ ] 20+ feedback submissions
- [ ] 5+ high-quality conversations (> 5 turns)

### Quality
- [ ] All 8 design principles followed
- [ ] QA checklist 100% complete
- [ ] Zero security vulnerabilities
- [ ] Documentation up-to-date

## Additional Notes

[Any specific launch requirements, timing considerations, stakeholder communication]

---

Ready to deploy when you are! 🚀
```

---

## Example: Vercel Production Deployment

```
Ready to deploy to production.

## Context to Load

[Same as template above]

## Deployment Information

**Target Environment**: Production
**Platform**: Vercel
**Domain**: portfolia.noahdelacal.com
**Branch**: main
**Expected Launch**: October 26, 2025, 10:00 AM PST

## Pre-Flight Checklist

### 1. Code Quality ✅
- [x] All tests passing: `pytest tests/ -v` → 74/74 tests (100%)
- [x] No TypeScript errors: `npm run build` → Build successful
- [x] No linting errors: `npm run lint` → 0 errors
- [x] No console.log statements removed
- [x] No commented-out code

### 2. Environment Variables ✅
- [x] OPENAI_API_KEY set in Vercel dashboard
- [x] SUPABASE_URL set
- [x] SUPABASE_SERVICE_ROLE_KEY set (verified no trailing newlines)
- [x] LANGSMITH_API_KEY set
- [x] RESEND_API_KEY set (tested email works)
- [x] TWILIO credentials set (tested SMS works)
- [x] Verified .env not in repo

[Continue with remaining checklist items...]

## Deployment Steps

[Follow steps from template...]

## Additional Notes

- Launch announcement prepared for LinkedIn
- Team notified of 10 AM go-live
- Support email (portfolia@noahdelacal.com) configured
- Backup taken of Supabase database before launch

---

Ready to deploy when you are! 🚀
```

---

## Tips for Using This Template

### 1. Work Through Systematically
- Don't skip checklist items
- Mark each with [x] when complete
- Document any issues found

### 2. Test in Staging First
- Deploy to preview environment first
- Run full smoke tests
- Fix any issues before production

### 3. Have Rollback Ready
- Know exactly how to revert
- Test rollback in staging
- Have emergency contact list

### 4. Monitor Closely
- First 2 hours critical
- Watch for error spikes
- Be ready to rollback if needed

### 5. Document Everything
- Take screenshots of successful deploys
- Note any manual steps taken
- Update runbooks with lessons learned

---

**Launch with confidence! 🎉**
