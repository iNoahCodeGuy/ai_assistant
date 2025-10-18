# Intelligent Resume Distribution System

**Feature Type**: Hybrid User-Initiated + Passive Awareness
**Status**: In Development (October 16, 2025)
**Priority**: HIGH - Critical for hiring manager conversion

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution: Hybrid Approach](#solution-hybrid-approach)
3. [User Experience Flow](#user-experience-flow)
4. [Behavioral Modes](#behavioral-modes)
5. [Technical Architecture](#technical-architecture)
6. [Implementation Details](#implementation-details)
7. [Transparency & Ethics](#transparency--ethics)
8. [Testing Strategy](#testing-strategy)
9. [Success Metrics](#success-metrics)

---

## Problem Statement

### Current State

**Portfolia successfully educates users about GenAI applications**, but:
- Hiring managers learn about the technology but don't know to ask for Noah's resume
- No mechanism to convert educational conversations into hiring opportunities
- Noah must manually follow up on promising conversations
- No automated notification system for hiring interest

### Impact

- **Missed opportunities**: Qualified hiring managers leave without connecting
- **Manual overhead**: Noah spends time monitoring conversations for signals
- **Conversion gap**: Education doesn't translate to job opportunities

### User Feedback (October 16, 2025)

> "For hiring manager roles, as conversation progresses and they're learning about GenAI, I want Portfolia to ask questions to probe if they're actively looking to hire someone... offer the resume, then email the resume and text me with the details."

**Critical clarification**: "**Portfolia needs to mainly offer education on generative ai applications, she only goes deeper if the user asks for the resume to be sent.**"

---

## Solution: Hybrid Approach

### Three-Tier Behavioral Model

Portfolia operates in three distinct modes based on user behavior:

#### **Mode 1: Education First (Default)**
- **Primary purpose**: Teach about GenAI applications
- **Behavior**: Enthusiastic, helpful, focused on concepts
- **Resume**: Not mentioned unless user asks
- **Philosophy**: *"I'm here to teach, not to sell"*

#### **Mode 2: Subtle Availability (When Hiring Signals Detected)**
- **Trigger**: User mentions hiring, describes role, asks about team size, etc.
- **Behavior**: Continue education, but add subtle availability mention
- **Example**: *"Noah's available for roles like this if you'd like to learn more about his background"*
- **Philosophy**: *"Make them aware, but don't push"*

#### **Mode 3: Deep Dive (When User Requests Resume)**
- **Trigger**: User explicitly asks: "Can I get your resume?", "Send me your CV", etc.
- **Behavior**: Immediately shift to resume distribution + job details gathering
- **No qualification needed**: If they ask, they're interested
- **Philosophy**: *"Respect explicit interest, respond immediately"*

---

## User Experience Flow

### Scenario A: Pure Education (80% of conversations)

```
User: "How do RAG systems work?"
Portfolia: "Great question! RAG combines retrieval and generation..."
[Full educational response, no resume mention]

User: "That's helpful, thanks!"
Portfolia: "You're welcome! What else would you like to explore?"
[Conversation ends naturally]
```

**Result**: ✅ User learned something valuable, Portfolia fulfilled primary purpose

---

### Scenario B: Hiring Signals Detected (15% of conversations)

```
User: "How do RAG systems work? We're building a chatbot for our company."
Portfolia: [Detects "we're building" = hiring signal]

Portfolia: "Great question! RAG combines retrieval and generation...
[Full educational response]

By the way, Noah's available for roles like this if you'd like to learn
more about his experience building production RAG systems."

User: "That's interesting, but I'm just researching for now."
Portfolia: "Perfect! Let me know if you have more questions about RAG."
[Conversation continues as education]
```

**Result**: ✅ User aware of Noah's availability, but no pressure applied

---

### Scenario C: Explicit Resume Request (5% of conversations)

```
User: "This is amazing! Can I get your resume?"
Portfolia: "Absolutely! I'd be happy to share Noah's résumé with you.
Could I get your name and email address?"

User: "Sure, I'm Jane Smith at jane@techcorp.com"
Portfolia: "Thanks Jane! I've sent Noah's résumé to jane@techcorp.com
and notified him of your interest."

[Behind the scenes: Resume emailed, Noah gets SMS]

Portfolia: "Just curious - what company are you with and what role
are you hiring for? (Helps me give Noah context)"

User: "We're TechCorp, looking for a Senior GenAI Engineer."
Portfolia: "Perfect, I've passed that along to Noah. He'll reach out soon!"
```

**Result**: ✅ Resume sent immediately, Noah notified with job context

---

## Behavioral Modes

### Mode 1: Education First (Default)

**Characteristics**:
- Enthusiastic about teaching GenAI concepts
- Focuses on user's learning goals
- Asks clarifying questions about concepts
- Provides code examples, architecture diagrams
- No resume mentions whatsoever

**Conversation Personality** (from `CONVERSATION_PERSONALITY.md`):
- **Warmth**: High - "I'm excited to help you understand..."
- **Enthusiasm**: High - "This is such a cool application!"
- **Invitation**: Medium - "Would you like to explore X?"
- **Pushiness**: Zero - Never mentions Noah's availability

**Detection**:
```python
# state.hiring_signals = []  # No signals detected
# state.resume_explicitly_requested = False
```

**Example Response**:
```
"Great question about RAG systems! Let me walk you through the architecture...

[Detailed technical explanation with examples]

The key insight is that retrieval gives LLMs access to current information
without retraining. Would you like me to show you how Noah implemented
this in his AI assistant?"
```

---

### Mode 2: Subtle Availability (Hiring Signals Detected)

**Triggers** (Hiring Signals):
- `mentioned_hiring`: "we're hiring", "looking for", "need a developer"
- `described_role`: "need someone who knows RAG", "senior engineer role"
- `team_context`: "our team", "we're building", "at my company"
- `asked_timeline`: "when could you start", "available next month"
- `budget_mentioned`: "what's your rate", "salary expectations"

**Characteristics**:
- **Primary behavior**: Still education-focused (80% of response)
- **Added element**: One subtle availability mention (20% of response)
- **Tone**: Natural, not salesy - "Oh by the way..."
- **Frequency**: Once per conversation, not repeated

**Detection**:
```python
# state.hiring_signals = ["mentioned_hiring", "team_context"]
# state.resume_explicitly_requested = False
```

**Example Response**:
```
"Great question about RAG systems! Let me walk you through the architecture...

[Full educational response - identical to Mode 1]

By the way, I noticed you mentioned your team is building something similar -
Noah's available for roles like this if you'd like to learn more about his
experience with production RAG systems. Just let me know!"
```

**Key Principle**: *Awareness without pressure*

---

### Mode 3: Deep Dive (User Requests Resume)

**Triggers** (Explicit Resume Requests):
- Direct: "Can I get your resume?", "Send me your CV", "Share Noah's resume"
- Indirect: "I'd like to learn more about Noah's background", "Do you have his info?"
- Interest-based: "Is Noah available?", "Can I contact him?"

**Characteristics**:
- **Immediate response**: No qualification checks, no delays
- **Shift in tone**: From teacher to facilitator
- **Information gathering**: Email, name, company, position
- **Transparency**: Explicit about sending resume and notifying Noah

**Detection**:
```python
# state.resume_explicitly_requested = True
# Resume request pattern detected in query
```

**Flow**:
1. **Confirm & Collect**: "Absolutely! Could I get your name and email?"
2. **Send & Notify**: Send resume via Resend, SMS to Noah via Twilio
3. **Gather Context**: "What company and role are you hiring for?"
4. **Close Loop**: "I've passed this along to Noah - he'll reach out soon!"

**Example Response**:
```
"Absolutely! I'd be happy to share Noah's résumé with you.

Could I get your name and email address? I'll send it over right away
and let Noah know you're interested."
```

**After email collected**:
```
"Perfect! I've sent Noah's résumé to [email] and he's been notified
of your interest.

Just to give him some context - what company are you with and what
role are you hiring for? (This helps him prepare for your conversation)"
```

**Key Principle**: *Respect explicit interest, respond immediately*

---

## Technical Architecture

### Conversation State Extensions

**File**: `src/flows/conversation_nodes.py`

```python
@dataclass
class ConversationState:
    """Extended state for resume distribution."""

    # Existing fields...
    role: str
    query: str
    answer: str
    chat_history: List[Dict]

    # NEW: Resume distribution fields
    hiring_signals: List[str] = field(default_factory=list)
    """Passive tracking: ['mentioned_hiring', 'team_context', 'described_role']"""

    resume_explicitly_requested: bool = False
    """True if user explicitly asks for resume (triggers Mode 3)"""

    resume_sent: bool = False
    """Once-per-session enforcement flag"""

    user_email: str = ""
    """Collected after explicit resume request"""

    user_name: str = ""
    """For personalized email greeting"""

    job_details: Dict[str, str] = field(default_factory=dict)
    """
    Gathered naturally during conversation:
    - company: str (REQUIRED after resume sent)
    - position: str (REQUIRED after resume sent)
    - timeline: str (NICE-TO-HAVE)
    - team_size: str (NICE-TO-HAVE)
    - budget: str (BONUS - only if volunteered)
    """
```

---

### Pipeline Nodes (New/Modified)

#### Node 1: Detect Hiring Signals (Passive)

**Function**: `detect_hiring_signals(state: ConversationState) -> ConversationState`

**Purpose**: Passively log hiring-related keywords for Mode 2 awareness

**Logic**:
```python
def detect_hiring_signals(state: ConversationState) -> ConversationState:
    """Passively detect hiring signals without triggering proactive offers."""

    query_lower = state.query.lower()
    signals = []

    # Signal 1: Mentioned hiring
    if re.search(r'\b(hiring|recruit|looking for|need a|searching for)\b', query_lower):
        signals.append('mentioned_hiring')

    # Signal 2: Described role
    if re.search(r'\b(engineer|developer|architect|senior|junior|role|position)\b', query_lower):
        signals.append('described_role')

    # Signal 3: Team context
    if re.search(r'\b(our team|we\'re building|at my company|my organization)\b', query_lower):
        signals.append('team_context')

    # Signal 4: Timeline questions
    if re.search(r'\b(when|start date|available|timeline|how soon)\b', query_lower):
        signals.append('asked_timeline')

    # Signal 5: Budget mentions
    if re.search(r'\b(rate|salary|compensation|budget|pay)\b', query_lower):
        signals.append('budget_mentioned')

    # Update state (append, don't replace - track across turns)
    state.hiring_signals = list(set(state.hiring_signals + signals))

    return state
```

**Integration**: Runs early in pipeline (after `classify_query`, before `retrieve_chunks`)

---

#### Node 2: Handle Resume Request (Explicit)

**Function**: `handle_resume_request(state: ConversationState) -> ConversationState`

**Purpose**: Detect explicit resume requests and shift to Mode 3

**Logic**:
```python
def handle_resume_request(state: ConversationState) -> ConversationState:
    """Detect explicit resume requests and flag for immediate handling."""

    query_lower = state.query.lower()

    # Explicit request patterns
    resume_patterns = [
        r'\b(can i get|send me|share|show me).{0,20}(resume|cv|curriculum)\b',
        r'\b(your resume|noah\'s resume|his resume)\b',
        r'\b(is noah available|can i contact|reach out to noah)\b',
        r'\b(learn more about noah|noah\'s background|his experience)\b',
    ]

    for pattern in resume_patterns:
        if re.search(pattern, query_lower):
            state.resume_explicitly_requested = True
            break

    return state
```

**Integration**: Runs immediately after `detect_hiring_signals` in pipeline

---

#### Node 3: Add Subtle Availability Mention (Mode 2)

**Function**: `add_availability_mention(state: ConversationState) -> ConversationState`

**Purpose**: Add subtle availability mention when hiring signals detected

**Logic**:
```python
def add_availability_mention(state: ConversationState) -> ConversationState:
    """Add subtle availability mention to educational responses (Mode 2)."""

    # Only add if:
    # 1. Hiring signals detected
    # 2. Resume NOT explicitly requested (Mode 3 handles that)
    # 3. Resume NOT already sent (once per session)
    # 4. NOT already mentioned in this response

    if (len(state.hiring_signals) >= 2 and
        not state.resume_explicitly_requested and
        not state.resume_sent and
        "noah's available" not in state.answer.lower()):

        # Get subtle mention from content_blocks
        mention = get_subtle_availability_mention(state.hiring_signals)

        # Append to end of educational response
        state.answer = f"{state.answer}\n\n{mention}"

    return state
```

**Integration**: Runs after `generate_answer`, before `plan_actions`

---

#### Node 4: Collect Email (Mode 3)

**Function**: Email collection handled in `generate_answer` prompt

**Behavior**:
- After `resume_explicitly_requested = True`
- If `user_email` is empty → Ask for email/name
- If `user_email` provided → Proceed to send

**Example Prompt Addition**:
```
[In generate_answer prompt for Mode 3]

RESUME REQUEST DETECTED: User explicitly asked for Noah's résumé.

IMMEDIATE NEXT STEP:
- If you don't have their email: "Absolutely! Could I get your name and email address?"
- If you have their email: Confirm resume sent, ask for job details

DO NOT qualify or delay - they explicitly requested it.
```

---

#### Node 5: Send Resume + Notify Noah (Action Execution)

**Function**: `execute_send_resume(state: ConversationState, action: Dict) -> None`

**File**: `src/flows/action_execution.py`

**Logic**:
```python
def execute_send_resume(self, state: ConversationState, action: Dict[str, Any]) -> None:
    """Send resume via email and notify Noah via SMS."""

    # Validation
    if state.resume_sent:
        logger.warning("Resume already sent this session, skipping duplicate")
        return

    if not state.user_email:
        logger.error("Cannot send resume - no email address collected")
        return

    # Step 1: Send resume PDF via Resend
    resend = get_resend_service()
    if resend:
        try:
            resend.send_email(
                to=state.user_email,
                subject=f"Noah De La Calzada - Résumé",
                html_body=self._get_resume_email_template(state.user_name),
                attachments=[{
                    'filename': 'Noah_De_La_Calzada_Resume.pdf',
                    'content': self._get_resume_pdf_base64()
                }]
            )
            logger.info(f"Resume sent to {state.user_email}")
        except Exception as e:
            logger.error(f"Failed to send resume: {e}")
            return

    # Step 2: Notify Noah via SMS with job details
    twilio = get_twilio_service()
    if twilio:
        job_context = self._format_job_details(state.job_details)
        message = f"""
🎯 Resume Request from Portfolia

Name: {state.user_name or 'Not provided'}
Email: {state.user_email}
{job_context}

Session ID: {state.session_id}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        """

        try:
            twilio.send_sms(
                to=supabase_settings.noah_phone_number,
                body=message
            )
            logger.info("SMS notification sent to Noah")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")

    # Step 3: Log to Supabase analytics
    self._log_resume_distribution(state)

    # Step 4: Set flag (once per session)
    state.resume_sent = True
```

---

#### Node 6: Gather Job Details (Mode 3 Post-Send)

**Function**: Natural prompting in `generate_answer` after resume sent

**Behavior**:
- After `resume_sent = True`
- Ask conversationally for company/position (REQUIRED)
- Ask naturally for timeline/team (NICE-TO-HAVE)
- Store in `state.job_details`

**Example Prompt Addition**:
```
[In generate_answer prompt after resume sent]

CONTEXT: You just sent Noah's résumé to this user.

NEXT STEPS:
1. Confirm resume sent: "I've sent Noah's résumé to [email]"
2. Gather job context: "Just curious - what company are you with and what
   role are you hiring for? This helps Noah prepare for your conversation."
3. Store their responses in job_details dict

TONE: Conversational, not interrogative. Frame as "helping Noah prepare".

DO NOT ask about budget/salary - let them volunteer if interested.
```

---

## Transparency & Ethics

### What Users Know (Explicit)

✅ **Resume sending**: "I've sent Noah's résumé to [email]"
✅ **Noah notification**: "I've notified Noah of your interest"
✅ **Email confirmation**: Users see confirmation message

### What Users Don't Know (Implicit)

⚠️ **Hiring signal tracking**: System logs signals passively
⚠️ **Job details storage**: Conversation data stored for Noah's context

### If User Asks About Data Collection

**Response**: *"Great question! This is actually a perfect example of how GenAI applications gather structured data from natural conversations. I'm tracking our discussion to help Noah understand the context if you reach out. Everything is stored securely and used only to facilitate your connection with him. Would you like to know more about how this data pipeline works?"*

**Philosophy**: Turn into teaching moment, maintain educational focus

### Privacy Compliance

- ✅ **CAN-SPAM compliant**: Resume email includes unsubscribe link
- ✅ **Data minimization**: Only collect necessary fields
- ✅ **User consent**: Implicit consent via resume request
- ✅ **Secure storage**: Supabase encrypted at rest
- ✅ **Transparency**: Honest if asked directly

---

## Testing Strategy

### Automated Tests

**File**: `tests/test_resume_distribution.py` (NEW)

#### Test Suite 1: Behavioral Modes

```python
def test_mode_1_pure_education():
    """Verify no resume mention in pure education mode."""
    state = ConversationState(
        role="hiring_manager_technical",
        query="How do RAG systems work?"
    )

    result = run_conversation_flow(state, mock_rag_engine)

    # Assert NO resume mention
    assert "resume" not in result.answer.lower()
    assert "available" not in result.answer.lower()
    assert len(result.hiring_signals) == 0


def test_mode_2_subtle_availability():
    """Verify subtle mention when hiring signals detected."""
    state = ConversationState(
        role="hiring_manager_technical",
        query="We're hiring a GenAI engineer. How do RAG systems work?"
    )

    result = run_conversation_flow(state, mock_rag_engine)

    # Assert hiring signals detected
    assert "mentioned_hiring" in result.hiring_signals
    assert "described_role" in result.hiring_signals

    # Assert subtle availability mention added
    assert "noah's available" in result.answer.lower()
    assert "if you'd like to learn more" in result.answer.lower()

    # Assert NOT pushy
    assert "send me your email" not in result.answer.lower()


def test_mode_3_explicit_request():
    """Verify immediate response to explicit resume request."""
    state = ConversationState(
        role="hiring_manager_technical",
        query="This is great! Can I get your resume?"
    )

    result = run_conversation_flow(state, mock_rag_engine)

    # Assert explicit request detected
    assert result.resume_explicitly_requested is True

    # Assert immediate email collection
    assert "could i get your name and email" in result.answer.lower()
```

#### Test Suite 2: Once-Per-Session Enforcement

```python
def test_resume_sent_once_per_session():
    """Verify resume only sent once per session."""
    state = ConversationState(
        role="hiring_manager_technical",
        query="Can I get your resume?",
        user_email="jane@example.com",
        user_name="Jane Smith"
    )

    # First request - should send
    result1 = run_conversation_flow(state, mock_rag_engine)
    assert result1.resume_sent is True
    assert mock_resend.send_email.call_count == 1

    # Second request in same session - should NOT send
    result2 = run_conversation_flow(result1, mock_rag_engine)
    assert result2.resume_sent is True
    assert mock_resend.send_email.call_count == 1  # Still 1, not 2
```

#### Test Suite 3: Job Details Gathering

```python
def test_job_details_gathered_naturally():
    """Verify job details collected after resume sent."""
    # Simulate conversation after resume sent
    state = ConversationState(
        role="hiring_manager_technical",
        query="We're TechCorp, hiring for Senior GenAI Engineer",
        resume_sent=True,
        user_email="jane@techcorp.com"
    )

    result = run_conversation_flow(state, mock_rag_engine)

    # Assert job details extracted
    assert result.job_details.get("company") == "TechCorp"
    assert result.job_details.get("position") == "Senior GenAI Engineer"
```

---

### Manual Testing (Streamlit)

**Phase 1: Local Testing (2 hours)**

#### Scenario 1: Pure Education Mode
```
1. Start Streamlit: `streamlit run src/main.py`
2. Select "Hiring Manager (Technical)"
3. Ask: "How do RAG systems work?"
4. Verify: NO resume mention in response
5. Ask: "What about vector databases?"
6. Verify: Still no resume mention
✅ Pass: Education-focused, no resume push
```

#### Scenario 2: Subtle Availability Mode
```
1. Select "Hiring Manager (Technical)"
2. Ask: "We're hiring a GenAI engineer. How do RAG systems work?"
3. Verify: Hiring signals detected (check logs)
4. Verify: Subtle mention at end of response ("Noah's available...")
5. Ask: "That's helpful, but I'm just researching"
6. Verify: No further resume mentions
✅ Pass: Subtle awareness without pressure
```

#### Scenario 3: Explicit Request Mode
```
1. Select "Hiring Manager (Technical)"
2. Ask: "This is amazing! Can I get your resume?"
3. Verify: Immediate email request ("Could I get your name and email?")
4. Respond: "I'm Jane Smith, jane@techcorp.com"
5. Verify: Confirmation message ("I've sent Noah's résumé...")
6. Check email inbox: Resume PDF received
7. Check Noah's phone: SMS notification received
8. Verify: Job details request ("What company are you with?")
9. Respond: "TechCorp, Senior GenAI Engineer role"
10. Verify: Details passed to Noah
✅ Pass: Full explicit request flow working
```

#### Scenario 4: Duplicate Prevention
```
1. Complete Scenario 3 (resume already sent)
2. Ask: "Can you send the resume again?"
3. Verify: Polite response ("I've already sent it to jane@techcorp.com")
4. Verify: NO second email sent
5. Verify: NO second SMS to Noah
✅ Pass: Once-per-session enforcement working
```

---

## Success Metrics

### Behavioral Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Education Quality** | >90% satisfaction | User feedback after conversations |
| **Subtle Mention Acceptance** | >60% positive response | Users engage after availability mention |
| **Explicit Request Conversion** | >95% complete flow | Requests → Email collected → Resume sent |
| **Duplicate Prevention** | 100% enforcement | Zero duplicate sends per session |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Resume Requests/Month** | >10 (Month 1) | Track `resume_sent` events |
| **Job Details Capture** | >80% include company/position | Check `job_details` completeness |
| **Noah Response Rate** | >90% within 24h | Track Noah's follow-up actions |
| **Hire Conversion** | >5% (1 hire per 20 requests) | Track final hiring outcomes |

### Quality Metrics (QA Integration)

| Metric | Target | Enforcement |
|--------|--------|-------------|
| **No pushy offers** | 0 violations | `test_no_pushy_resume_offers()` |
| **Education-first principle** | 100% adherence | `test_education_remains_primary()` |
| **Explicit request priority** | 100% immediate response | `test_explicit_request_immediate()` |
| **Transparency standards** | 100% honest answers | `test_data_collection_transparency()` |

---

## Implementation Checklist

### Phase 1: Core Architecture (4 hours)

- [ ] **State Extensions** (30 min)
  - Add `hiring_signals`, `resume_explicitly_requested`, `resume_sent` fields to `ConversationState`
  - Add `user_email`, `user_name`, `job_details` fields

- [ ] **Passive Detection** (1 hour)
  - Create `detect_hiring_signals()` function
  - Integrate into conversation pipeline
  - Test signal detection with sample queries

- [ ] **Explicit Request Handler** (1 hour)
  - Create `handle_resume_request()` function
  - Add resume request patterns
  - Integrate into pipeline before `generate_answer`

- [ ] **Prompt Updates** (1.5 hours)
  - Update `generate_answer` prompts for Mode 1, 2, 3
  - Add email collection logic for Mode 3
  - Add job details gathering for post-send

- [ ] **Content Blocks** (30 min)
  - Create `get_subtle_availability_mention()` in `content_blocks.py`
  - Create resume email template
  - Create SMS notification template

### Phase 2: Action Execution (2 hours)

- [ ] **Resume Send Action** (1.5 hours)
  - Create `execute_send_resume()` in `action_execution.py`
  - Integrate Resend email sending
  - Integrate Twilio SMS notification
  - Add Supabase logging

- [ ] **Error Handling** (30 min)
  - Add graceful degradation if Resend fails
  - Add fallback if Twilio fails
  - Log all errors to Supabase

### Phase 3: Testing (3 hours)

- [ ] **Automated Tests** (2 hours)
  - Create `tests/test_resume_distribution.py`
  - Write Mode 1, 2, 3 behavioral tests
  - Write once-per-session enforcement tests
  - Write job details gathering tests

- [ ] **Manual Streamlit Testing** (1 hour)
  - Test all 4 scenarios (education, subtle, explicit, duplicate)
  - Verify email delivery with test account
  - Verify SMS delivery to test number
  - Document any edge cases

### Phase 4: Documentation & QA (1 hour)

- [ ] **Master Docs Update** (30 min)
  - Update `PROJECT_REFERENCE_OVERVIEW.md` (hiring manager behavior)
  - Update `SYSTEM_ARCHITECTURE_SUMMARY.md` (pipeline nodes)
  - Update `CONVERSATION_PERSONALITY.md` (Mode 2 subtle mentions)

- [ ] **QA Integration** (30 min)
  - Add alignment tests for new functions
  - Update `QA_STRATEGY.md` with new quality standards
  - Update `CHANGELOG.md` with feature summary

---

## Next Steps

1. ✅ **Feature documentation complete** (this document)
2. ⏭️ **Begin Phase 1**: State extensions + detection nodes
3. ⏭️ **Phase 2**: Action execution + email/SMS integration
4. ⏭️ **Phase 3**: Automated + manual testing
5. ⏭️ **Phase 4**: Documentation + QA alignment
6. ⏭️ **Deploy**: Vercel production deployment
7. ⏭️ **Monitor**: Track success metrics for 2 weeks

---

**Last Updated**: October 16, 2025
**Author**: Noah De La Calzada (via AI assistant)
**Status**: Ready for implementation ✅
