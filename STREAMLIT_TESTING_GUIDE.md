# Intelligent Resume Distribution - Streamlit Testing Guide

**Purpose**: Manual validation of the Intelligent Resume Distribution System before production deployment

**Date**: October 16, 2025

**Status**: Task 11 - Ready for manual testing

---

## Pre-Testing Setup

### 1. Environment Configuration

Ensure your `.env` file has these keys configured:

```bash
# Required for all scenarios
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Required for email testing (Scenario 3)
RESEND_API_KEY=re_...

# Required for SMS testing (Scenario 3)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
NOAH_PHONE_NUMBER=+1...  # Your actual phone number
```

### 2. Start Streamlit Server

```bash
# Navigate to project root
cd /Users/noahdelacalzada/NoahsAIAssistant/NoahsAIAssistant-

# Start server
streamlit run src/main.py
```

**Expected output**:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

### 3. Prepare Test Email & Phone

- **Email**: Use a test email you can access (check inbox during Scenario 3)
- **Phone**: Ensure Noah's phone can receive SMS (check during Scenario 3)
- **Browser**: Open incognito/private window to avoid cache issues

---

## Testing Scenarios

### Scenario 1: Mode 1 - Pure Education (ZERO Resume Mentions)

**Purpose**: Verify educational queries receive NO resume mentions

**Steps**:
1. Select role: **"Hiring Manager (technical)"**
2. Ask: `"How do RAG systems work?"`

**Expected Behavior**:
- ✅ Educational response about RAG systems
- ✅ Code examples (if technical HM role)
- ✅ Follow-up prompt offered (e.g., "Would you like me to show you implementation details?")
- ❌ **ZERO** mentions of Noah's availability, resume, or contact
- ❌ **ZERO** "click here", "send email", "sign up" phrases

**Validation Checklist**:
- [ ] Response is 100% educational
- [ ] No resume mentions anywhere in response
- [ ] Follow-up prompt is professional (not pushy)
- [ ] Code examples displayed correctly (if applicable)
- [ ] No aggressive CTAs

**Pass Criteria**: Response contains ONLY educational content + optional follow-up prompt

---

### Scenario 2: Mode 2 - Hiring Signals (Subtle Availability Mention)

**Purpose**: Verify subtle mention appears when hiring signals detected

**Steps**:
1. **Clear chat** (start new conversation)
2. Select role: **"Hiring Manager (technical)"**
3. Ask: `"We're hiring a Senior GenAI Engineer. How do RAG systems work?"`

**Expected Behavior**:
- ✅ Educational response about RAG systems (≥50% of content)
- ✅ **ONE** subtle mention at end: "By the way, Noah's available for roles like this if you'd like to learn more."
- ✅ Natural placement (feels like afterthought, not pitch)
- ❌ **NO** aggressive CTAs ("send email now", "click here", "sign up")
- ❌ **NO** more than 1 availability mention

**Validation Checklist**:
- [ ] Response is primarily educational (≥50%)
- [ ] Exactly ONE subtle availability mention
- [ ] Mention is at end of response
- [ ] No pressure language ("if you'd like")
- [ ] Educational content still comprehensive

**Pass Criteria**: Education + subtle mention (no more than 1 sentence about availability)

**Follow-Up Test**:
- Ask another educational question: `"What's the difference between FAISS and pgvector?"`
- **Expected**: Educational answer with NO additional availability mention (already mentioned once)

---

### Scenario 3: Mode 3 - Explicit Request (Immediate Distribution)

**Purpose**: Verify resume sends immediately when explicitly requested

**Steps**:
1. **Clear chat** (start new conversation)
2. Select role: **"Hiring Manager (technical)"**
3. Ask: `"Can I get your resume?"`

**Expected Behavior (Step 1 - Email Collection)**:
- ✅ Immediate response: "I'd be happy to send that. What's your email address?"
- ✅ Natural tone (not interrogative)
- ❌ **NO** qualification questions ("Tell me about your company")

**Continue Conversation**:
4. Provide email: `your-test-email@example.com`

**Expected Behavior (Step 2 - Name Collection)**:
- ✅ Response: "Thanks! And your name?"
- ✅ Brief, natural ask

**Continue Conversation**:
5. Provide name: `"I'm Jane Smith"`

**Expected Behavior (Step 3 - Resume Sent Confirmation)**:
- ✅ Confirmation: "Sent! Check your inbox at your-test-email@example.com"
- ✅ Professional thank you message
- ✅ Offer to continue conversation

**Validation Checklist (Conversation)**:
- [ ] Immediate email collection (no delays)
- [ ] No qualification questions asked
- [ ] Natural conversational flow
- [ ] Clear confirmation message
- [ ] Professional tone maintained

**Validation Checklist (Email - CHECK YOUR INBOX)**:
- [ ] Email received at test address
- [ ] Subject line: "Noah de la Calzada - Resume"
- [ ] Email contains resume PDF attachment
- [ ] Email body is professional
- [ ] From address is correct (via Resend)

**Validation Checklist (SMS - CHECK NOAH'S PHONE)**:
- [ ] SMS received on Noah's phone
- [ ] Message format: "Resume sent to your-test-email@example.com from Jane Smith"
- [ ] Sent via Twilio
- [ ] Timestamp is current

**Pass Criteria**: Email received + SMS received + confirmation shown in UI

---

### Scenario 4: Job Details Gathering (Post-Interest)

**Purpose**: Verify conversational job details extraction after resume sent

**Prerequisites**: Complete Scenario 3 first (resume must be sent)

**Steps**:
1. **Continue from Scenario 3** (same conversation, resume already sent)
2. Ask educational question: `"How do you handle retrieval failures in RAG?"`

**Expected Behavior (Step 1 - Job Details Prompt)**:
- ✅ Educational response about retrieval failures
- ✅ Natural job details question at end: "Just curious — what company are you with, and what position is this for?"
- ✅ Conversational tone (not interrogative)
- ❌ **NOT** mandatory (user can skip)

**Continue Conversation**:
3. Provide details: `"I'm with Acme Corp, hiring for a Senior AI Engineer starting next month."`

**Expected Behavior (Step 2 - Extraction Confirmation)**:
- ✅ Response acknowledges details: "Got it — Acme Corp, Senior AI Engineer."
- ✅ Optional: "Feel free to continue asking about Noah's experience!"
- ✅ No further job details questions (only asks once)

**Validation Checklist**:
- [ ] Job details question appears ONLY AFTER resume sent
- [ ] Question is natural and conversational
- [ ] User can skip without issue
- [ ] Extraction correctly identifies: company ("Acme Corp"), position ("Senior AI Engineer"), timeline ("next month")
- [ ] System doesn't ask again in same conversation

**Pass Criteria**: Natural job details gathering with correct extraction

---

### Scenario 5: Duplicate Prevention (Once-Per-Session)

**Purpose**: Verify resume can only be sent once per conversation

**Prerequisites**: Complete Scenario 3 (resume already sent in conversation)

**Steps**:
1. **Continue from Scenario 3** (same conversation)
2. Ask: `"Can you send me your resume again?"`

**Expected Behavior**:
- ✅ Polite response: "I've already sent my resume to your-test-email@example.com earlier in this conversation."
- ✅ Offer to help: "Is there something else I can help you with?"
- ❌ **NO** second email sent
- ❌ **NO** second SMS sent

**Validation Checklist**:
- [ ] Polite duplicate prevention message
- [ ] Reminds user of email where resume was sent
- [ ] Offers continued assistance
- [ ] No second email received (check inbox)
- [ ] No second SMS received (check phone)

**Pass Criteria**: Polite rejection + no duplicate sends

---

## Cross-Role Consistency Tests

### Test 6: Non-HM Role Behavior

**Purpose**: Verify resume distribution only activates for hiring manager roles

**Steps**:
1. **Clear chat** (new conversation)
2. Select role: **"Software Developer"**
3. Ask: `"We're hiring. How do RAG systems work?"`

**Expected Behavior**:
- ✅ Educational response about RAG systems
- ✅ Code examples (Developer role priority)
- ❌ **NO** availability mention (even though "hiring" mentioned)
- ❌ **NO** resume distribution flow

**Validation Checklist**:
- [ ] Educational content only
- [ ] No availability mention
- [ ] Developer-specific enhancements (code focus)

**Pass Criteria**: Educational response with no resume distribution features

---

## Error Handling Tests

### Test 7: Invalid Email Detection

**Steps**:
1. **Clear chat**
2. Select role: **"Hiring Manager (technical)"**
3. Ask: `"Can I get your resume?"`
4. Provide invalid email: `not-an-email`

**Expected Behavior**:
- ✅ Error message: "That doesn't look like a valid email address. Could you provide your email?"
- ✅ Retry allowed
- ❌ **NO** resume sent with invalid email

**Pass Criteria**: Graceful error handling with retry

---

### Test 8: Service Degradation (Optional - Requires Disabling Services)

**Purpose**: Verify graceful degradation when Resend/Twilio unavailable

**Setup**: Temporarily remove `RESEND_API_KEY` from `.env`

**Steps**:
1. **Clear chat**
2. Ask: `"Can I get your resume?"`
3. Provide email and name

**Expected Behavior**:
- ✅ Error message: "Sorry, I couldn't send the resume right now. Please email noah@example.com directly."
- ✅ Graceful fallback (doesn't crash)
- ✅ Logs error to Supabase

**Pass Criteria**: Graceful error message + no crash

---

## Post-Testing Validation

### Supabase Logs Check

1. **Open Supabase Dashboard** → Messages Table
2. **Verify logs exist** for all test conversations:
   - [ ] Scenario 1 logged (education query)
   - [ ] Scenario 2 logged (hiring signals)
   - [ ] Scenario 3 logged (resume request + send action)
   - [ ] Scenario 4 logged (job details extraction)
   - [ ] Scenario 5 logged (duplicate prevention)

3. **Check analytics** → `retrieval_logs` table:
   - [ ] All queries logged with timestamps
   - [ ] Latency recorded for each query
   - [ ] Success/failure status correct

### Final Checklist

**Functionality**:
- [ ] Mode 1 (Pure Education): ZERO resume mentions ✅
- [ ] Mode 2 (Hiring Signals): ONE subtle mention ✅
- [ ] Mode 3 (Explicit Request): Immediate distribution ✅
- [ ] Job Details Gathering: Conversational extraction ✅
- [ ] Duplicate Prevention: Once per session ✅

**Quality Standards**:
- [ ] No pushy language anywhere ✅
- [ ] Education remains primary (≥50% content) ✅
- [ ] Natural conversational tone ✅
- [ ] Professional formatting ✅
- [ ] No aggressive CTAs ✅

**External Services**:
- [ ] Email sent via Resend ✅
- [ ] SMS sent via Twilio ✅
- [ ] Resume PDF attached correctly ✅
- [ ] Job details in SMS (if gathered) ✅

**Error Handling**:
- [ ] Invalid email detected ✅
- [ ] Graceful service degradation ✅
- [ ] No crashes or exceptions ✅

**Observability**:
- [ ] All conversations logged to Supabase ✅
- [ ] Analytics tracking working ✅
- [ ] Resume send actions logged ✅

---

## Known Issues / Expected Failures

**None** - All 37 automated tests passing, ready for manual validation.

---

## Troubleshooting

### Issue: No subtle mention in Scenario 2

**Cause**: Insufficient hiring signals detected (need ≥2)

**Fix**: Ensure query contains 2+ signal types:
- ✅ Good: "We're **hiring** a **Senior Engineer**" (2 signals: mentioned_hiring + described_role)
- ❌ Bad: "We're hiring" (1 signal only)

### Issue: Email not received in Scenario 3

**Checks**:
1. Is `RESEND_API_KEY` set correctly?
2. Check spam folder
3. Verify email in Streamlit UI confirmation message
4. Check Resend dashboard for send status
5. Check Supabase logs for `resume_email_sent` action

### Issue: SMS not received in Scenario 3

**Checks**:
1. Is `TWILIO_AUTH_TOKEN` set correctly?
2. Is `NOAH_PHONE_NUMBER` correct format (+1...)?
3. Check Twilio console for delivery status
4. Check Supabase logs for `noah_notified_via_sms` action

### Issue: Duplicate prevention not working in Scenario 5

**Cause**: May have cleared chat (resets conversation state)

**Fix**: Must be in SAME conversation as Scenario 3 (don't click "Clear Chat")

---

## Success Criteria

**All scenarios must pass** with:
- ✅ Expected behavior matches actual behavior
- ✅ All validation checklists complete
- ✅ No console errors
- ✅ No exceptions in logs
- ✅ Email and SMS received
- ✅ Supabase logs present

**If any scenario fails**: Document issue, create GitHub issue, fix before production deployment.

---

## Next Steps After Testing

**If all tests pass**:
1. Mark Task 11 as complete ✅
2. Update CHANGELOG.md with "Manual testing complete"
3. Proceed to production deployment (Vercel)
4. Monitor LangSmith for production behavior

**If tests fail**:
1. Document specific failure
2. Create bug report with reproduction steps
3. Fix issue
4. Re-run automated tests: `pytest tests/test_resume_distribution.py -v`
5. Re-test failed scenario
6. Repeat until all pass

---

## Contact

**Questions?** Review:
- Feature doc: `docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md`
- QA standards: `docs/QA_STRATEGY.md` Section 1.1-1.2
- Test suite: `tests/test_resume_distribution.py`

**Found a bug?** Document in this file and create GitHub issue.

---

**Status**: Ready for testing ✅ (All 37 automated tests passing, documentation complete)

---

## Vercel Deployment & Testing

### Pre-Deployment Checklist

**Before deploying to Vercel, ensure:**

1. **All automated tests passing locally**:
   ```bash
   pytest tests/test_conversation_quality.py tests/test_documentation_alignment.py tests/test_resume_distribution.py -v
   # Expected: 70 passed, 1 skipped
   ```

2. **Environment variables documented**:
   - Create `.env.production` with Vercel-specific values
   - Never commit `.env` files to git (already in `.gitignore`)

3. **Vercel configuration updated**:
   - Check `vercel.json` includes all API routes
   - Ensure Python runtime version specified

---

### Vercel Deployment Steps

#### Step 1: Configure Environment Variables in Vercel

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Set production environment variables
vercel env add OPENAI_API_KEY
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add RESEND_API_KEY
vercel env add TWILIO_ACCOUNT_SID
vercel env add TWILIO_AUTH_TOKEN
vercel env add TWILIO_PHONE_NUMBER
vercel env add NOAH_PHONE_NUMBER

# Optional: LangSmith for monitoring
vercel env add LANGSMITH_API_KEY
vercel env add LANGCHAIN_TRACING_V2
```

**⚠️ CRITICAL**: Ensure NO trailing newlines in environment variables:
```bash
# Test locally first
python3 -c "import os; key=os.getenv('OPENAI_API_KEY'); print(f'Length: {len(key)}, Clean: {repr(key[-5:])}')"
# Should show: Length: 164, Clean: '...abc' (NOT '...abc\n')
```

---

#### Step 2: Deploy to Vercel

```bash
# Deploy to production
vercel --prod

# Expected output:
# ✓ Production: https://noahs-ai-assistant.vercel.app [1m]
```

**Deployment will:**
- Build Python serverless functions from `api/*.py`
- Deploy Streamlit UI (if configured)
- Set environment variables from Vercel dashboard
- Enable automatic HTTPS

---

#### Step 3: Verify Deployment Health

**API Endpoint Tests**:

```bash
# Test 1: Health check (if you have one)
curl https://noahs-ai-assistant.vercel.app/api/health

# Test 2: Chat endpoint
curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do RAG systems work?",
    "role": "Hiring Manager (technical)",
    "session_id": "test-session-123"
  }'

# Expected: JSON response with educational answer

# Test 3: Explicit resume request
curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can I get your resume?",
    "role": "Hiring Manager (technical)",
    "session_id": "test-session-456"
  }'

# Expected: JSON response asking for email
```

---

### Vercel-Specific Testing Scenarios

#### Scenario V1: Production API - Pure Education (Mode 1)

**Purpose**: Verify production API returns educational content only

**Steps**:
```bash
curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain vector databases",
    "role": "Hiring Manager (technical)",
    "session_id": "vercel-test-1"
  }'
```

**Expected Response**:
```json
{
  "answer": "[Educational content about vector databases...]",
  "sources": [...],
  "session_id": "vercel-test-1"
}
```

**Validation**:
- [ ] Response contains educational content
- [ ] NO resume mentions in response
- [ ] Response time <5s (check Vercel logs)
- [ ] No errors in Vercel function logs

---

#### Scenario V2: Production API - Hiring Signals (Mode 2)

**Purpose**: Verify subtle mention appears on production

**Steps**:
```bash
curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "We are hiring a Senior AI Engineer. How do RAG systems work?",
    "role": "Hiring Manager (technical)",
    "session_id": "vercel-test-2"
  }'
```

**Expected Response**:
```json
{
  "answer": "[Educational content...] By the way, Noah's available for roles like this if you'd like to learn more.",
  "sources": [...],
  "session_id": "vercel-test-2"
}
```

**Validation**:
- [ ] Educational content primary (≥50%)
- [ ] ONE subtle availability mention at end
- [ ] No aggressive CTAs
- [ ] hiring_signals logged to Supabase

---

#### Scenario V3: Production API - Resume Request Flow

**Purpose**: Verify full resume distribution flow on Vercel

**Step 1 - Request Resume**:
```bash
SESSION_ID="vercel-test-3-$(date +%s)"

curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"Can I get your resume?\",
    \"role\": \"Hiring Manager (technical)\",
    \"session_id\": \"$SESSION_ID\"
  }"
```

**Expected**: Email collection prompt

**Step 2 - Provide Email**:
```bash
curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"test-vercel@example.com\",
    \"role\": \"Hiring Manager (technical)\",
    \"session_id\": \"$SESSION_ID\"
  }"
```

**Expected**: Name collection prompt

**Step 3 - Provide Name**:
```bash
curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"I'm Jane Vercel\",
    \"role\": \"Hiring Manager (technical)\",
    \"session_id\": \"$SESSION_ID\"
  }"
```

**Expected**: Resume sent confirmation

**Validation**:
- [ ] Email received at test-vercel@example.com (check inbox)
- [ ] SMS received on Noah's phone
- [ ] Supabase logs show resume_sent action
- [ ] Confirmation message in API response

---

### Vercel-Specific Issues & Fixes

#### Issue 1: Cold Start Timeout (Function exceeds 10s)

**Symptoms**:
- First request takes >10s
- `FUNCTION_INVOCATION_TIMEOUT` in Vercel logs

**Fixes**:
1. **Reduce import overhead**:
   ```python
   # api/chat.py - Move heavy imports inside handler
   def handler(req):
       from src.core.rag_engine import RagEngine  # Lazy load
       engine = RagEngine()
       ...
   ```

2. **Enable Vercel Pro (if needed)**:
   - Provisioned concurrency keeps functions warm
   - Upgrade: https://vercel.com/pricing

3. **Monitor cold starts**:
   ```bash
   vercel logs --follow
   # Look for: "Cold Start: 5234ms"
   ```

---

#### Issue 2: Environment Variable Errors

**Symptoms**:
- `httpcore.LocalProtocolError: Illegal header value`
- `APIConnectionError: Connection error`

**Root Cause**: Trailing newlines in env vars

**Fix**:
```bash
# In Vercel dashboard → Settings → Environment Variables
# Delete and re-add WITHOUT pressing Enter after value

# Test locally first:
python3 -c "import os; print(repr(os.getenv('OPENAI_API_KEY')))"
# Should NOT show '\n' at end
```

---

#### Issue 3: Resume Email Not Sending

**Symptoms**:
- API returns success but no email received
- Vercel logs show: "Email service unavailable"

**Checks**:
1. **Verify Resend API key in Vercel**:
   ```bash
   vercel env ls
   # Should show: RESEND_API_KEY (Production)
   ```

2. **Check Resend dashboard**:
   - Go to https://resend.com/emails
   - Look for send attempts with your test email
   - Check for error messages

3. **Verify graceful degradation**:
   ```bash
   # API should return error message, not crash
   curl -X POST https://noahs-ai-assistant.vercel.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Can I get your resume?", ...}'

   # Should get: "Sorry, couldn't send resume. Please email noah@..."
   ```

---

#### Issue 4: Supabase Connection Fails

**Symptoms**:
- `404 Not Found` from Supabase
- `FUNCTION_INVOCATION_FAILED` in Vercel logs

**Checks**:
1. **Verify Supabase credentials in Vercel**:
   ```bash
   vercel env ls
   # Should show:
   # SUPABASE_URL (Production)
   # SUPABASE_SERVICE_ROLE_KEY (Production)
   ```

2. **Test Supabase connection**:
   ```python
   # Create test script: test_vercel_supabase.py
   import os
   from supabase import create_client

   url = os.getenv("SUPABASE_URL")
   key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

   client = create_client(url, key)
   response = client.table("messages").select("*").limit(1).execute()
   print(f"✅ Supabase connected: {len(response.data)} records")
   ```

3. **Check Supabase migrations**:
   - Go to Supabase Dashboard → SQL Editor
   - Verify `messages`, `kb_chunks`, `retrieval_logs` tables exist
   - Re-run migrations if missing (see `supabase/migrations/`)

---

### Vercel Performance Monitoring

#### Check Function Logs

```bash
# Real-time logs
vercel logs --follow

# Filter by function
vercel logs --follow api/chat.py

# Check for errors
vercel logs | grep "ERROR"
```

**Look for**:
- Cold start times (should be <5s)
- Error rates (should be <1%)
- Response times (should be <3s average)
- Memory usage (should be <512MB)

---

#### Monitor with Vercel Analytics

1. **Enable Analytics**:
   - Go to Vercel Dashboard → Your Project → Analytics
   - Enable "Web Analytics" and "Speed Insights"

2. **Key Metrics**:
   - **Real Experience Score (RES)**: Should be >75
   - **First Contentful Paint**: Should be <2s
   - **Time to First Byte**: Should be <800ms

3. **Set up Alerts**:
   - Dashboard → Settings → Notifications
   - Alert on: Error rate >5%, Latency >5s

---

### Post-Deployment Validation Checklist

**Functionality** (via curl or Postman):
- [ ] Mode 1 (Education): ZERO resume mentions ✅
- [ ] Mode 2 (Hiring Signals): ONE subtle mention ✅
- [ ] Mode 3 (Explicit Request): Resume sent ✅
- [ ] Job Details: Extraction working ✅
- [ ] Duplicate Prevention: Once per session ✅

**Production Services**:
- [ ] OpenAI API calls working (check responses)
- [ ] Supabase logging working (check tables)
- [ ] Resend email working (check inbox)
- [ ] Twilio SMS working (check phone)
- [ ] pgvector retrieval working (check sources)

**Performance**:
- [ ] Cold start <10s (Vercel limit)
- [ ] Warm response <3s average
- [ ] No timeout errors in logs
- [ ] Memory usage <512MB

**Error Handling**:
- [ ] Invalid email returns error (not crash)
- [ ] Missing env vars handled gracefully
- [ ] Service failures return user-friendly messages
- [ ] All errors logged to Supabase

**Observability**:
- [ ] Vercel logs showing all requests
- [ ] Supabase analytics updated
- [ ] LangSmith tracing enabled (if configured)
- [ ] No sensitive data in logs

---

### Success Criteria (Vercel Deployment)

**All scenarios must pass on production**:
- ✅ Local Streamlit tests passing (Scenarios 1-8)
- ✅ Vercel API tests passing (Scenarios V1-V3)
- ✅ Email/SMS working in production
- ✅ Supabase logging in production
- ✅ No console errors in Vercel logs
- ✅ Performance within acceptable limits (<5s)

**If Vercel tests fail**:
1. Check Vercel logs: `vercel logs --follow`
2. Verify environment variables: `vercel env ls`
3. Test locally first: `streamlit run src/main.py`
4. Fix issue and redeploy: `vercel --prod`
5. Re-test failed scenario

---

### Rollback Procedure (If Needed)

**If production deployment has critical issues**:

```bash
# 1. Check deployment history
vercel ls

# 2. Rollback to previous version
vercel rollback https://noahs-ai-assistant-abc123.vercel.app

# 3. Fix issue locally
# Make changes, run tests

# 4. Redeploy when fixed
vercel --prod
```

---

**Status**: Ready for Vercel deployment ✅ (All automated tests passing, local validation pending)
