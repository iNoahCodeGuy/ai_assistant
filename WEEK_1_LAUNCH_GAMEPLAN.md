# 🚀 Week 1 Launch Gameplan - Portfolia Web Application

**Created:** October 19, 2025
**Target Launch:** October 26, 2025 (7 days)
**Domain:** GoDaddy custom domain
**Architecture:** Next.js on Vercel (professional, scalable)

---

## 📊 Current Status Assessment

### ✅ What's Working
- **Backend APIs**: 6 Vercel serverless functions production-ready
  - `/api/chat` - Main conversation endpoint
  - `/api/analytics` - Live data dashboard
  - `/api/email` - Resume distribution
  - `/api/feedback` - User ratings
  - `/api/confess` - Confession collection
  - `/api/health` - Health check

- **Test Coverage**: 70/74 tests passing (95%)
  - ✅ test_conversation_flow.py: 12/12 (100%)
  - ✅ test_conversation_quality.py: 19/19 (100%)
  - ✅ test_resume_distribution.py: 37/37 (100%)
  - ⚠️ test_error_handling.py: 2/6 (33% - fixable in 30 min)

- **Data Layer**: Supabase pgvector fully configured
- **LangGraph Flow**: TypedDict-based conversation pipeline

### ⚠️ Blockers to Resolve
1. **Frontend incomplete**: Next.js has TypeScript errors, missing node_modules
2. **3 failing tests**: Need Supabase mocks in error_handling tests
3. **Legacy code**: Some deprecated FAISS stubs, unused utilities

---

## 🎯 Week 1 Strategy: Next.js on Vercel

### Why Next.js (Not Streamlit)?
✅ **Professional**: Custom branding on your GoDaddy domain
✅ **Scalable**: Handles 100k+ users on free tier
✅ **Modern**: React, TypeScript, responsive design
✅ **SEO-ready**: Server-side rendering, meta tags
✅ **Future-proof**: Easy to add auth, analytics, mobile app

### Architecture Overview
```
User Browser
     ↓
portfolio.yourdomain.com (Next.js UI on Vercel)
     ↓
Vercel Serverless Functions (api/*.py) ← Already working!
     ↓
Supabase (pgvector) + OpenAI (GPT-4o-mini)
```

---

## 📅 7-Day Execution Plan

### **Day 1 (Today): Fix Tests + Setup Frontend**

#### Morning (3 hours): Backend Quality Assurance

**Task 1.1: Fix Error Handling Tests** (30 min)
- Add Supabase mocks to `tests/test_error_handling.py`
- Target: 74/74 tests passing ✅
- **Design Principle**: Testability (#7) - Proper mocking for external dependencies

**Task 1.2: Archive Legacy Code** (30 min)
- Move `src/utils/embeddings.py` → `archive/utils/embeddings_legacy.py`
- Remove FAISS stub from `src/core/langchain_compat.py`
- Clean up unused imports
- **Design Principle**: Simplicity (YAGNI #8) - Remove unused code

**Task 1.3: LangGraph Alignment Check** (1 hour)
- Compare our TypedDict flow with https://github.com/techwithtim/LangGraph-Tutorial.git
- Document differences in `docs/LANGGRAPH_ALIGNMENT.md`
- Plan StateGraph migration for Week 2
- **Design Principle**: Maintainability (#7) - Follow framework best practices

**Task 1.4: Run Full Test Suite** (1 hour)
```bash
pytest tests/ -v --cov=src --cov-report=html
```
- Verify 100% test pass rate
- Check code coverage
- Fix any issues found

#### Afternoon (3 hours): Frontend Setup

**Task 1.5: Install Dependencies** (15 min)
```bash
npm install
```
- Install Next.js, React, TypeScript, Tailwind
- Verify package.json is complete

**Task 1.6: Fix TypeScript Errors** (2 hours)
- Resolve missing module imports (`next`, `react`, `lucide-react`)
- Fix JSX namespace errors in `app/layout.tsx`, `app/components/chat/ChatHeader.tsx`
- Ensure clean TypeScript compilation
- **Design Principle**: Defensibility (#6) - Type safety catches bugs early

**Task 1.7: Build Successfully** (15 min)
```bash
npm run build
```
- Target: Zero TypeScript errors
- Verify production build works

**Task 1.8: Create Missing Components** (30 min)
- `app/components/chat/ChatMessage.tsx` - Message display
- `app/components/chat/ChatInput.tsx` - User input
- `app/components/shared/Button.tsx` - Reusable button
- **Design Principle**: Reusability (#4) - Component-based architecture

**End of Day 1 Success Criteria**:
- ✅ All 74 tests passing
- ✅ Next.js builds without errors
- ✅ Legacy code archived
- ✅ LangGraph alignment documented

---

### **Day 2: Deploy to Vercel + Custom Domain**

#### Morning (2 hours): Vercel Deployment

**Task 2.1: Install Vercel CLI** (5 min)
```bash
npm i -g vercel
```

**Task 2.2: Deploy to Vercel** (15 min)
```bash
vercel --prod
```
- Answer prompts (project name, settings)
- Note deployment URL

**Task 2.3: Configure Environment Variables** (30 min)
In Vercel dashboard (Settings → Environment Variables):
```bash
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbG...

# Resend (Email)
RESEND_API_KEY=re_...
ADMIN_EMAIL=noah@yourdomain.com

# Twilio (SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
ADMIN_PHONE=+1...

# LangSmith (Optional - for monitoring)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=portfolia-production
```
- **Design Principle**: Portability (#5) - Environment-based configuration

**Task 2.4: Verify API Endpoints** (30 min)
```bash
# Test health check
curl https://your-app.vercel.app/api/health

# Test chat endpoint
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello", "role": "Just looking around"}'
```

**Task 2.5: Test Frontend-Backend Integration** (30 min)
- Visit deployed Next.js URL
- Test role selection
- Send test message
- Verify response appears

#### Afternoon (2 hours): Custom Domain Configuration

**Task 2.6: Add Domain in Vercel** (15 min)
- Vercel Dashboard → Settings → Domains
- Add: `portfolia.yourdomain.com`

**Task 2.7: Configure DNS in GoDaddy** (30 min)
- Login to GoDaddy DNS management
- Add CNAME record:
  - Host: `portfolia`
  - Points to: `cname.vercel-dns.com`
  - TTL: 600 seconds

**Task 2.8: Wait for DNS Propagation** (15 min)
```bash
# Check DNS propagation
nslookup portfolia.yourdomain.com
```

**Task 2.9: Verify SSL Certificate** (15 min)
- Vercel auto-provisions SSL
- Test: `https://portfolia.yourdomain.com`
- Verify padlock icon in browser

**Task 2.10: Update README.md** (30 min)
- Add live URL
- Update deployment instructions
- Document environment variables
- **Design Principle**: Maintainability (#7) - Clear documentation

**End of Day 2 Success Criteria**:
- ✅ Live at `https://portfolia.yourdomain.com`
- ✅ All API endpoints responding
- ✅ SSL certificate active
- ✅ Frontend loads successfully

---

### **Day 3: UI Polish + Role Testing**

#### Morning (3 hours): Frontend Enhancements

**Task 3.1: Improve Landing Page** (1 hour)
Update `app/page.tsx`:
```tsx
- Hero section: "Meet Portfolia - Noah's AI Teaching Assistant"
- Value proposition: Learn GenAI by exploring a real system
- CTA button: "Start Learning"
- Feature highlights grid
```
- **Design Principle**: Simplicity (KISS #8) - Clear, focused messaging

**Task 3.2: Enhance Chat Interface** (1 hour)
Update `app/chat/page.tsx`:
- Role selector with descriptions
- Typing indicators
- Loading states
- Error messages
- Copy code snippet buttons
- **Design Principle**: Defensibility (#6) - User-friendly error handling

**Task 3.3: Add Markdown Rendering** (30 min)
```bash
npm install react-markdown remark-gfm react-syntax-highlighter
```
- Render code blocks with syntax highlighting
- Support tables, lists, links
- **Design Principle**: Reusability (#4) - Standard markdown renderer

**Task 3.4: Mobile Responsiveness** (30 min)
- Test on iPhone/Android simulators
- Fix layout issues
- Ensure touch-friendly buttons
- **Design Principle**: Portability (#5) - Works on all devices

#### Afternoon (2 hours): Comprehensive Role Testing

**Task 3.5: Test All 5 Roles** (2 hours)

For each role, test:
1. **Hiring Manager (nontechnical)**
   - Query: "How can AI help my business?"
   - Expected: Plain English, business value, no code
   - Hiring signals: "We're hiring a developer"
   - Expected: Subtle availability mention

2. **Hiring Manager (technical)**
   - Query: "Explain your RAG architecture"
   - Expected: Technical details + code snippets
   - Resume request: "Can I get your resume?"
   - Expected: Email collection flow

3. **Software Developer**
   - Query: "Show me the retrieval code"
   - Expected: Syntax-highlighted Python code
   - Follow-up: "How does pgvector work?"
   - Expected: Technical deep dive

4. **Just looking around**
   - Query: "What can you do?"
   - Expected: Casual, fun tone
   - MMA query: "Tell me about fights"
   - Expected: YouTube link (if implemented)

5. **Looking to confess crush**
   - Query: "I have a secret"
   - Expected: Confession collection flow
   - Verify: Data logged to Supabase (privacy protected)

**Task 3.6: Create Bug List** (30 min)
- Document all issues found
- Prioritize: Critical, High, Medium, Low
- Create GitHub issues or tracking doc

**End of Day 3 Success Criteria**:
- ✅ Polished UI matching designs
- ✅ All 5 roles tested end-to-end
- ✅ Mobile responsive
- ✅ Bug list created and prioritized

---

### **Day 4: Bug Fixes + Core Features**

#### Morning (3 hours): Critical Bug Fixes

**Task 4.1: Fix High-Priority Bugs** (3 hours)
From Day 3 testing, address:
- API timeout issues
- Session management bugs
- UI rendering glitches
- Error handling gaps
- **Design Principle**: Defensibility (#6) - Fail-safe, fail-loud

**Design Principles to Apply**:
- **Cohesion (#1)**: Keep bug fixes localized to single modules
- **Loose Coupling (#3)**: Fix without breaking other components
- **Testability (#7)**: Add tests for each bug fixed

#### Afternoon (2 hours): Essential Features

**Task 4.2: Add Copy Code Button** (30 min)
```tsx
// app/components/CodeBlock.tsx
<button onClick={() => navigator.clipboard.writeText(code)}>
  Copy
</button>
```

**Task 4.3: Add Download Resume Button** (30 min)
- Generate signed URL from Supabase Storage
- Download PDF on click
- Track analytics event

**Task 4.4: Add Feedback Widget** (45 min)
```tsx
// app/components/FeedbackWidget.tsx
- Thumbs up/down buttons
- Optional comment textarea
- POST to /api/feedback
```
- **Design Principle**: Encapsulation (#2) - Self-contained widget

**Task 4.5: Add Share Conversation** (15 min)
- Generate shareable URL with session ID
- Copy link to clipboard
- (Optional: Add social share buttons)

**End of Day 4 Success Criteria**:
- ✅ All critical bugs fixed
- ✅ Copy code working
- ✅ Resume download working
- ✅ Feedback widget functional
- ✅ Share feature implemented

---

### **Day 5: Analytics + Production Testing**

#### Morning (2 hours): Analytics Integration

**Task 5.1: Add Google Analytics** (30 min)
```bash
npm install @next/third-parties
```
Update `app/layout.tsx`:
```tsx
import { GoogleAnalytics } from '@next/third-parties/google'

<GoogleAnalytics gaId="G-XXXXXXXXXX" />
```

**Task 5.2: Add Vercel Analytics** (15 min)
```bash
npm install @vercel/analytics
```
```tsx
import { Analytics } from '@vercel/analytics/react'

<Analytics />
```

**Task 5.3: Track Custom Events** (45 min)
```tsx
// Track key interactions
analytics.track('role_selected', { role: selectedRole })
analytics.track('message_sent', { query_type: classifiedType })
analytics.track('resume_downloaded', { session_id: sessionId })
analytics.track('code_copied', { snippet_length: code.length })
```

**Task 5.4: Create Analytics Dashboard** (30 min)
- Vercel Dashboard → Analytics
- Set up custom events monitoring
- Configure alerts for errors

#### Afternoon (3 hours): Production Testing

**Task 5.5: Load Testing** (1 hour)
```bash
# Simulate 50 concurrent users
npm install -g autocannon

autocannon -c 50 -d 30 \
  -m POST \
  -H "Content-Type: application/json" \
  -b '{"query":"Hello","role":"Just looking around"}' \
  https://portfolia.yourdomain.com/api/chat
```
- Monitor response times
- Check for errors
- Verify auto-scaling

**Task 5.6: Cross-Browser Testing** (1 hour)
Test on:
- ✅ Chrome (Windows, Mac)
- ✅ Safari (Mac, iOS)
- ✅ Firefox (Windows, Mac)
- ✅ Edge (Windows)
- ✅ Mobile browsers (iOS Safari, Android Chrome)

**Task 5.7: Error Scenario Testing** (1 hour)
Test failure modes:
- Invalid API keys (simulate OpenAI error)
- Supabase timeout (disconnect network mid-request)
- Malformed user input (XSS attempts, SQL injection)
- Rate limiting (send 100 requests/second)
- **Design Principle**: Defensibility (#6) - Fail gracefully

**End of Day 5 Success Criteria**:
- ✅ Analytics tracking all events
- ✅ Load testing passed (avg response < 3s)
- ✅ Cross-browser compatibility verified
- ✅ Error handling robust

---

### **Day 6: Content + Documentation**

#### Morning (3 hours): Landing Page Content

**Task 6.1: Write Hero Section** (30 min)
```md
# Meet Portfolia
Noah's AI Teaching Assistant

Learn how generative AI systems work by exploring a real production application.
Ask about RAG, vector search, LLM orchestration, and enterprise patterns.

[Start Learning →]
```

**Task 6.2: Create Features Section** (1 hour)
```tsx
<FeatureGrid>
  <Feature icon="🎓" title="Educational Focus">
    Learn GenAI concepts through hands-on exploration
  </Feature>
  <Feature icon="💻" title="Real Code Examples">
    See actual Python implementations with explanations
  </Feature>
  <Feature icon="📊" title="Live Analytics">
    View real-time metrics and system performance
  </Feature>
  <Feature icon="🏢" title="Enterprise Patterns">
    Understand production-ready AI architecture
  </Feature>
</FeatureGrid>
```

**Task 6.3: Add Demo Queries Section** (45 min)
```tsx
<DemoQueries>
  <QueryCard role="Developer">
    "Show me the RAG retrieval code"
  </QueryCard>
  <QueryCard role="Business">
    "How can AI reduce customer support costs?"
  </QueryCard>
  <QueryCard role="Curious">
    "Display data analytics"
  </QueryCard>
</DemoQueries>
```

**Task 6.4: Create About Section** (45 min)
- Noah's background
- Project motivation
- Tech stack overview
- Open source contribution info

#### Afternoon (2 hours): Documentation + Legal

**Task 6.5: Write FAQ Section** (45 min)
```md
## Frequently Asked Questions

**Q: What is Portfolia?**
A: An educational AI assistant that teaches GenAI concepts...

**Q: How is this different from ChatGPT?**
A: Portfolia is specialized for teaching about AI systems...

**Q: Can I see the source code?**
A: Yes! Check out the GitHub repository...

**Q: What data do you collect?**
A: We log queries, responses, and analytics (see Privacy Policy)...
```

**Task 6.6: Create Privacy Policy** (30 min)
```md
# Privacy Policy

## Data We Collect
- User queries and responses
- Session IDs (for conversation continuity)
- Analytics (query types, response times)

## Data We DON'T Collect
- Personal information (unless voluntarily provided for resume requests)
- Passwords or authentication credentials

## How We Use Data
- Improve response quality
- Monitor system performance
- Research and development
```

**Task 6.7: Create Terms of Service** (30 min)
```md
# Terms of Service

## Acceptable Use
- Educational purposes
- Respectful interactions
- No harmful content

## Limitations
- No guarantee of accuracy
- Service provided "as-is"
- May be updated without notice
```

**Task 6.8: Update README.md** (15 min)
- Live production URL
- Quick start guide
- Architecture diagram
- Contributing guidelines

**End of Day 6 Success Criteria**:
- ✅ Professional landing page
- ✅ Comprehensive FAQ
- ✅ Privacy policy published
- ✅ Terms of service published
- ✅ Documentation complete

---

### **Day 7: Launch Preparation + Go Live**

#### Morning (2 hours): Pre-Launch Checklist

**Task 7.1: Final Security Review** (30 min)
```bash
# Check for exposed secrets
grep -r "sk-" . --exclude-dir=node_modules
grep -r "API_KEY" . --exclude-dir=node_modules

# Verify .env is in .gitignore
git status --ignored
```
- **Design Principle**: Defensibility (#6) - Least privilege, secure defaults

**Task 7.2: Performance Optimization** (45 min)
```bash
# Lighthouse audit
npm install -g lighthouse
lighthouse https://portfolia.yourdomain.com --view

# Optimize images
npm install next-image-optimization

# Enable caching headers
```

**Task 7.3: Final Test Pass** (45 min)
```bash
# Run all tests
pytest tests/ -v

# Check TypeScript
npm run build

# Verify deployment
curl https://portfolia.yourdomain.com/api/health
```

**Production Readiness Checklist**:
- [ ] All 74 tests passing ✅
- [ ] TypeScript compiles without errors ✅
- [ ] Environment variables set in Vercel ✅
- [ ] Custom domain working ✅
- [ ] SSL certificate active ✅
- [ ] Analytics tracking events ✅
- [ ] Error logging configured ✅
- [ ] Backup plan documented ✅
- [ ] Rollback procedure tested ✅

#### Afternoon (2 hours): Soft Launch

**Task 7.4: Deploy Final Version** (15 min)
```bash
git add .
git commit -m "🚀 Production launch v1.0"
git push origin main

# Vercel auto-deploys
```

**Task 7.5: Soft Launch to Friends** (1 hour)
- Share with 10 people (friends, colleagues, family)
- Ask for specific feedback:
  - UI/UX experience
  - Clarity of responses
  - Bug reports
  - Feature suggestions

**Task 7.6: Monitor in Real-Time** (45 min)
```bash
# Watch Vercel logs
vercel logs --follow

# Monitor analytics dashboard
# Check error rates, response times, user flow
```

**Task 7.7: Fix Immediate Issues** (varies)
- Hot fixes for critical bugs
- Quick UI tweaks
- Performance optimizations

#### Evening (1 hour): Public Launch

**Task 7.8: Announcement Posts** (30 min)

**LinkedIn**:
```md
🚀 Excited to launch Portfolia - my AI teaching assistant!

Instead of just telling you about GenAI systems, Portfolia shows you
the actual code, architecture, and data flows powering our conversation.

Try it: https://portfolia.yourdomain.com

Built with:
- Next.js + Vercel (frontend + serverless)
- Supabase pgvector (RAG retrieval)
- OpenAI GPT-4o-mini (generation)
- LangGraph (conversation orchestration)

All code open source: [GitHub link]

#AI #GenAI #MachineLearning #OpenSource
```

**Twitter**:
```md
🚀 Just launched Portfolia - an AI assistant that teaches you about
GenAI systems by letting you explore its own code and architecture!

Ask about RAG, vector search, LLM orchestration, and more.

Try it: https://portfolia.yourdomain.com

Built in public with Next.js, Supabase, and OpenAI 🛠️
```

**Task 7.9: Community Sharing** (20 min)
- r/MachineLearning
- r/OpenAI
- r/webdev
- Hacker News (Show HN)
- Product Hunt

**Task 7.10: Monitor & Respond** (10 min)
- Watch for comments
- Answer questions
- Thank early users
- Address concerns

**End of Day 7 Success Criteria**:
- ✅ **LIVE IN PRODUCTION** 🎉
- ✅ Real users interacting
- ✅ Analytics showing activity
- ✅ No critical errors
- ✅ Positive feedback received

---

## 🎨 Design Principles Compliance

### How We're Following the 8 Principles

#### 1. Cohesion & SRP (Single Responsibility Principle)
- ✅ **Backend**: Each API endpoint handles one concern (chat, analytics, email)
- ✅ **Frontend**: Component-based architecture (ChatMessage, RoleSelector, etc.)
- ✅ **Data**: Separate tables for messages, retrieval_logs, feedback
- **Example**: `ChatInput.tsx` only handles user input, not API calls or rendering

#### 2. Encapsulation & Abstraction
- ✅ **Service Layer**: Factory functions hide implementation (`get_resend_service()`)
- ✅ **RAG Engine**: Internal retrieval logic hidden behind public `retrieve()` method
- ✅ **State Management**: `ConversationState` TypedDict with controlled mutations
- **Example**: Frontend doesn't know if backend uses pgvector or FAISS

#### 3. Loose Coupling & Modularity
- ✅ **Dependency Injection**: Services injected, not instantiated internally
- ✅ **API Contracts**: Frontend talks to backend via JSON, not direct imports
- ✅ **Swappable Components**: Can replace OpenAI with Anthropic easily
- **Example**: Email service can be Resend, SendGrid, or mock without changing callers

#### 4. Reusability & Extensibility
- ✅ **Conversation Nodes**: Modular pipeline (classify → retrieve → generate)
- ✅ **Content Blocks**: Reusable message templates in `content_blocks.py`
- ✅ **React Components**: Shared Button, Card, Modal components
- **Example**: Adding a new role doesn't require rewriting retrieval logic

#### 5. Portability
- ✅ **Environment Variables**: All config in `.env`, no hardcoded values
- ✅ **Cross-Platform**: Works on Windows, Mac, Linux
- ✅ **Database Agnostic**: Uses Supabase client, not raw SQL
- **Example**: Can deploy to Vercel, AWS, or Azure without code changes

#### 6. Defensibility
- ✅ **Input Validation**: Email regex, query sanitization, rate limiting
- ✅ **Fail-Safe Defaults**: `debug_mode=False`, `timeout=30`
- ✅ **PII Protection**: Redact emails/phones from analytics, confession privacy
- ✅ **Error Handling**: Graceful degradation when services fail
- **Example**: If OpenAI fails, return helpful fallback instead of crashing

#### 7. Maintainability & Testability
- ✅ **Test Coverage**: 74 automated tests, 95% pass rate
- ✅ **Clear Naming**: `classify_query`, `retrieve_chunks`, `generate_answer`
- ✅ **Documentation**: Master docs in `docs/context/`, inline comments
- ✅ **Type Safety**: TypeScript frontend, TypedDict backend
- **Example**: Can test `retrieve_chunks` without calling OpenAI (mocked)

#### 8. Simplicity (KISS, DRY, YAGNI)
- ✅ **KISS**: Pipeline is linear (no complex branching)
- ✅ **DRY**: Single RAG engine, not one per role
- ✅ **YAGNI**: Building features as needed, not speculating
- **Example**: No premature optimization, no over-engineered abstractions

---

## 🧪 Quality Assurance Strategy

### Daily QA Checkpoints

**Every Day Before Committing**:
```bash
# 1. Run tests
pytest tests/ -v

# 2. Check TypeScript
npm run build

# 3. Lint code
npm run lint

# 4. Check for secrets
git diff | grep -i "api_key\|secret\|password"
```

### Code Review Checklist

Before merging any code, verify:
- [ ] Follows design principles (documented above)
- [ ] Has tests (or documents why not)
- [ ] No hardcoded values (use env vars)
- [ ] Error handling in place
- [ ] Documentation updated
- [ ] No console.logs or debug prints
- [ ] TypeScript types defined
- [ ] Imports organized

### Pre-Deployment Checklist

**Before deploying to production**:
- [ ] All tests passing locally
- [ ] Staging environment tested
- [ ] Environment variables verified
- [ ] Database migrations run
- [ ] Backup taken
- [ ] Rollback plan ready
- [ ] Monitoring enabled
- [ ] Team notified

---

## 📚 LangGraph Alignment

### Current Implementation vs Best Practices

**Reference**: https://github.com/techwithtim/LangGraph-Tutorial.git

#### ✅ What We're Doing Correctly
1. **TypedDict State**: Using `ConversationState` TypedDict for state management
2. **Functional Nodes**: Pure functions that take state, return state
3. **Linear Pipeline**: Clear flow through conversation stages
4. **Immutable Updates**: `state.set_answer()`, `state.stash()` helpers

#### ⚠️ Improvements for Week 2 (Post-Launch)
1. **StateGraph Migration**: Upgrade to actual `StateGraph` class
2. **Conditional Edges**: Add routing based on query type
3. **Parallel Execution**: Run retrieval + code fetching concurrently
4. **Checkpointing**: Add conversation state persistence

#### 📝 Documented in `docs/LANGGRAPH_ALIGNMENT.md`
- Detailed comparison with tutorial repo
- Migration path from TypedDict → StateGraph
- Benefits of each approach
- Timeline for upgrade

---

## 🗂️ File Cleanup & Archiving

### Files to Archive (Day 1)

**Legacy Utilities** (→ `archive/utils/`):
- `src/utils/embeddings.py` (marked as legacy, not used)

**Deprecated Code** (→ Remove):
- `src/core/langchain_compat.py` lines 34-49 (FAISS stub)

**Test Cleanup** (Already organized ✅):
- Manual tests in `tests/manual/` (keep as-is)
- Automated tests in `tests/` (verified)

### Dependencies Audit

**Verify all imports are used**:
```bash
# Check for unused imports
pylint src/ --disable=all --enable=unused-import

# Check package usage
pip-check
```

**Remove if unused**:
- Old FAISS dependencies
- Deprecated LangChain packages

---

## 🚨 Risk Mitigation

### Potential Blockers & Solutions

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **TypeScript errors persist** | Medium | High | Allocate extra day, consider Streamlit fallback |
| **API rate limits hit** | Low | Medium | Monitor usage, upgrade OpenAI tier if needed |
| **DNS propagation slow** | Low | Low | Start early (Day 2), have patience |
| **User finds critical bug** | Medium | High | Hot fix process, rollback capability |
| **Performance issues** | Low | Medium | Load testing on Day 5 catches early |

### Rollback Plan

If production breaks:
```bash
# 1. Revert to last known good deployment
vercel rollback

# 2. Check logs for error
vercel logs

# 3. Fix locally
npm run build  # Verify fix works

# 4. Redeploy
git commit -m "fix: critical bug"
git push origin main
```

---

## 📞 Support & Escalation

### When to Ask for Help

**Immediate Questions** (ask in gameplan updates):
1. **GoDaddy DNS Access**: Do you have login credentials?
2. **Email Service**: Resend account set up? API key ready?
3. **Domain Preference**: Exact subdomain? (`portfolia` vs `portfolio` vs other)
4. **Branding**: Logo, colors, fonts preferences?
5. **Content**: Bio for About section? Specific accomplishments to highlight?

**Decision Points** (confirm before proceeding):
1. **Day 3**: If major bugs found, extend testing or continue?
2. **Day 5**: If load testing fails, optimize or launch anyway?
3. **Day 7**: Soft launch feedback negative - delay public launch?

### Communication Protocol

**Daily Updates** (end of each day):
- What was completed
- What's blocking
- What's next
- Questions/decisions needed

**Emergency Protocol** (critical issues):
- Immediate Slack/email
- Document issue
- Propose solution
- Wait for approval before changing production

---

## 🎯 Success Metrics

### Week 1 Targets

**Technical Metrics**:
- ✅ 100% test pass rate (74/74)
- ✅ Zero TypeScript errors
- ✅ API response time < 3s (p95)
- ✅ Uptime > 99% (1 hour downtime max)

**Business Metrics**:
- 🎯 50 unique visitors (first week)
- 🎯 10 resume downloads
- 🎯 20 feedback submissions
- 🎯 5 GitHub stars

**Quality Metrics**:
- ✅ All 8 design principles followed
- ✅ QA checklist 100% complete
- ✅ Documentation comprehensive
- ✅ Zero security vulnerabilities

### Post-Launch (Week 2+)

**User Engagement**:
- Session duration > 5 minutes
- Messages per session > 5
- Return user rate > 20%

**Technical Debt**:
- Migrate to StateGraph (LangGraph best practices)
- Add authentication (Supabase Auth)
- Implement caching (Redis)
- Mobile app (React Native)

---

## 📖 Documentation Alignment

### Master Documentation Structure

**Must Read Before Coding**:
1. `docs/context/PROJECT_REFERENCE_OVERVIEW.md` - System purpose
2. `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md` - How it works
3. `docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md` - Data contracts
4. `docs/context/CONVERSATION_PERSONALITY.md` - Behavior rules

**Update During Development**:
- `CHANGELOG.md` - All changes logged
- `README.md` - Reflects current deployment
- `docs/LANGGRAPH_ALIGNMENT.md` - New file, alignment check
- API docs in `api/README.md`

**Verify Alignment**:
```bash
# Run documentation alignment tests
pytest tests/test_documentation_alignment.py -v
```

---

## 🎉 Launch Day Checklist

### Morning of Day 7

- [ ] Coffee ☕
- [ ] Run all tests one final time
- [ ] Check Vercel deployment status
- [ ] Verify all environment variables
- [ ] Test custom domain
- [ ] Screenshot working app (for announcements)
- [ ] Prepare social media posts
- [ ] Notify friends/family of launch time

### Launch Moment

- [ ] Final `git push`
- [ ] Watch Vercel deployment logs
- [ ] Test production URL
- [ ] Post announcements simultaneously
- [ ] Monitor analytics dashboard
- [ ] Respond to early feedback
- [ ] Celebrate! 🎉

---

## 🤔 Questions & Clarifications Needed

### Before We Start (Needs Your Input)

1. **GoDaddy Domain Access**
   - Question: What's the exact domain you purchased?
   - Why: Need to configure DNS correctly
   - Impact: Day 2 task depends on this

2. **Resend Email Service**
   - Question: Do you have a Resend account and API key?
   - Why: Resume distribution feature needs it
   - Impact: Can use mock service if not ready
   - Junior Dev Note: Resend sends transactional emails (like resume PDFs). Without it, users can't request your resume. We can launch without it and add later.

3. **Twilio SMS Service**
   - Question: Do you have Twilio account and phone number?
   - Why: Notifications when someone requests resume
   - Impact: Optional feature, can disable if not set up
   - Junior Dev Note: Twilio sends you text messages. It's nice-to-have, not required for launch.

4. **Branding Preferences**
   - Question: Any specific colors, fonts, or logo for the site?
   - Why: Professional appearance on landing page
   - Impact: Can use defaults (blue/purple gradient) if no preference
   - Junior Dev Note: We can always change styling later. Don't let this block launch.

5. **Content for About Section**
   - Question: Short bio (2-3 sentences) about you and why you built this?
   - Why: Makes landing page personal and engaging
   - Impact: Can write generic version if you prefer
   - Junior Dev Note: People connect with stories. "I built this to..." is powerful.

6. **Launch Timing Preference**
   - Question: Prefer soft launch (friends first) or immediate public launch?
   - Why: Soft launch lets us catch bugs with friendly testers
   - Impact: Could delay public announcement by 1 day
   - Junior Dev Note: I recommend soft launch - easier to fix bugs when it's just friends testing.

### Design Decisions (Confirm Approach)

7. **LangGraph Migration**
   - Recommendation: Keep current TypedDict implementation for Week 1, migrate to StateGraph in Week 2
   - Why: Current implementation works, migration adds risk close to deadline
   - Tradeoff: Launch faster vs use framework best practices
   - Junior Dev Note: TypedDict is simpler but StateGraph is "official" LangGraph way. Both work, StateGraph scales better.

8. **Test Coverage Target**
   - Recommendation: Fix 3 failing tests to get 100% pass rate
   - Why: All tests passing = confidence in production
   - Effort: 30 minutes to add mocks
   - Junior Dev Note: Tests are like safety nets. We want all passing before launch.

9. **Legacy Code Cleanup**
   - Recommendation: Archive (don't delete) unused code
   - Why: Might need to reference later, git history preserves
   - Risk: Minimal, these files aren't imported
   - Junior Dev Note: Archive means "move to archive/ folder" - keeps code but out of the way.

### Technical Clarifications

10. **Deployment Strategy**
    - Recommendation: Vercel for both frontend (Next.js) and backend (Python APIs)
    - Why: Single platform, auto-deploy on git push, generous free tier
    - Alternative: Could use Streamlit Cloud for frontend, but less professional
    - Junior Dev Note: Vercel handles scaling automatically. You push code, it deploys. Simple!

---

## 📝 Next Steps

**Immediate Actions** (waiting for your approval):

1. **Confirm gameplan acceptance**
   - Review 7-day schedule
   - Approve or request changes
   - Confirm you're ready to start

2. **Answer clarification questions** (above)
   - Domain name
   - Email/SMS service status
   - Branding preferences
   - Content for About section

3. **Begin Day 1 execution**
   - Fix 3 failing tests (30 min)
   - Archive legacy code (30 min)
   - Install Next.js dependencies (15 min)
   - Fix TypeScript errors (2 hours)

**Ready to execute on your command!** 🚀

Just say "proceed with Day 1" and I'll start working through the tasks systematically.

---

**Questions or concerns about this gameplan?** Let me know and I'll explain any part in more detail!
