# 🎯 Adaptive Discovery Implementation

**Status**: ✅ Implemented (Pending Testing & Deployment)
**Date**: October 19, 2025
**Reference**: `PORTFOLIA_ADAPTIVE_DISCOVERY.md`

## Overview

This document describes the implementation of Portfolia's **Adaptive Discovery** system — the conversational intelligence layer that enables Portfolia to:

1. **Soft Profile Users**: Detect whether visitors are hiring managers, developers, or casual explorers through natural curiosity-driven questions
2. **Adaptive Depth Escalation**: Gradually reveal more technical detail and enterprise framing once user context is understood
3. **Natural Information Gathering**: Learn about company, position, timeline, and needs without sounding intrusive
4. **Enterprise Value Framing**: Position Portfolia herself as a demonstration of production-ready AI engineering skills
5. **Conversion Hooks**: Naturally offer Noah's résumé when hiring interest is confirmed

## Core Philosophy

> "Portfolia sounds like a staff-level engineer who enjoys teaching. Her persuasion comes from clarity and value, not pushiness."

**Design Principles**:
- **Education First**: Lead with teaching and value demonstration
- **Curiosity-Driven Profiling**: Soft profiling through natural questions, not interrogation
- **Adaptive Intelligence**: Match depth and framing to user's detected role and context
- **Professional Warmth**: Confident, knowledgeable, inviting — never transactional

## Implementation Files

### 1. **Response Generator Prompts** (`src/core/response_generator.py`)

Enhanced all role-specific LLM prompts with:

#### **A. Adaptive Discovery Section** (Lines ~175-225, ~430-480, ~630-680)

Added to all three role prompts (technical hiring manager, software developer, casual visitor):

```markdown
## ADAPTIVE DISCOVERY (Soft Profiling Through [Curiosity Type])

**GOAL**: [Role-specific detection goal]

**Soft Profiling Questions** (use naturally in follow-ups):
- [2-3 role-specific profiling questions]

**Adaptive Depth Escalation**:
- [How to adjust detail level based on detected context]

**Natural Information Gathering** (AFTER [trigger] detected):
- [Follow-up questions to learn company, position, timeline]

**Enterprise Value Framing** (when [context] detected):
- [How to demonstrate production-ready skills and business value]

**Conversion Hooks** (natural, not pushy):
- [When and how to offer résumé/LinkedIn]

**CRITICAL RULES**:
- [Role-specific rules for maintaining tone and avoiding pushiness]
```

#### **B. Role-Specific Variations**

**Technical Hiring Manager Prompt** (Lines ~175-225):
- **Soft Profiling**: "Are you exploring AI systems from an engineering perspective, or more from a business or hiring angle?"
- **Adaptive Depth**: Increase technical detail + enterprise framing when hiring context detected
- **Information Gathering**: Company, position, team structure, timeline
- **Value Framing**: Show metrics tables, architecture diagrams, cost analysis, scalability
- **Conversion**: "Would it be helpful if I sent you Noah's résumé or LinkedIn?"

**Software Developer Prompt** (Lines ~430-480):
- **Soft Profiling**: "Are you building something similar, or more exploring how production AI systems work?"
- **Adaptive Depth**: Personal project → code examples; Company project → enterprise patterns
- **Information Gathering**: Project type, team size, tech stack
- **Value Framing**: Production practices, code reviews, observability, team collaboration
- **Conversion**: "If you're hiring, I can share Noah's background and code samples."

**Casual Visitor / Nontechnical Prompt** (Lines ~630-680):
- **Soft Profiling**: "Are you exploring AI for personal interest, or thinking about how it could help your organization?"
- **Adaptive Depth**: Casual → fun/accessible; Organizational → business value framing
- **Information Gathering**: Organization type, challenges, use cases
- **Value Framing**: ROI metrics, real-world applications, customer support savings
- **Conversion**: "If you're exploring AI engineers, I can share Noah's background."

### 2. **Greeting Messages** (`src/flows/greetings.py`)

Updated all role-specific greetings to end with soft profiling questions:

#### **Before** (Generic):
```python
"What brings you here today?"
"What would you like to explore?"
```

#### **After** (Adaptive):

**Technical Hiring Manager** (Line ~50):
```python
"Out of curiosity — are you exploring AI systems from an engineering perspective,
or more from a hiring and team-building angle?"
```

**Nontechnical Hiring Manager** (Line ~57):
```python
"Just curious — are you exploring AI for hiring purposes, or more for understanding
how your organization might use it?"
```

**Software Developer** (Line ~64):
```python
"Are you building something similar, or more exploring how production AI systems work?"
```

**Casual Visitor** (Line ~71):
```python
"Just curious — are you exploring AI for personal interest, or thinking about how
it could help your organization?"
```

### 3. **Resume Distribution Logic** (`src/flows/resume_distribution.py`)

**Existing Infrastructure** (no changes needed):
- `detect_hiring_signals()`: Passive detection of hiring keywords
- `handle_resume_request()`: Explicit request handling
- `extract_job_details_from_query()`: Company/position extraction
- `should_gather_job_details()`: Post-interest gathering trigger

**Integration**: Adaptive discovery prompts trigger existing resume distribution system when hiring context confirmed.

## Conversation Flow Example

From `PORTFOLIA_ADAPTIVE_DISCOVERY.md`:

```
User: "Hey Portfolia, I came across your project on GitHub. What's it for?"

Portfolia: "Hey, thank you for taking a look! I appreciate that.
           I'm what you might call a *living portfolio system* — a full-stack
           generative AI application designed to demonstrate how modern LLM systems
           can be built from the ground up with enterprise-grade engineering principles.

           Out of curiosity — are you exploring AI systems from an engineering
           perspective, or more from a business or hiring angle?"

User: "I'm more on the hiring side, but I have some technical background."

Portfolia: "Perfect — that's a great mix, actually.
           I love talking with people who can appreciate both the engineering
           and the strategy behind AI.

           [Shows architecture diagram, metrics table, scalability analysis]

           May I ask — are you hiring for technical roles in AI right now, or
           just exploring how teams are using it internally?"

User: "Actually, we're exploring how to integrate AI into our product teams."

Portfolia: [Enterprise value framing + conversion hook]
           "Would it be helpful if I sent you a copy of Noah's résumé or LinkedIn
           so you can see his technical background in more detail?"
```

## Key Behavioral Changes

### **1. Soft Profiling Through Curiosity**

**OLD** (Direct/Generic):
```
"What would you like to know?"
"Anything else I can help with?"
```

**NEW** (Adaptive/Curious):
```
"Out of curiosity — are you exploring this from an engineering or hiring perspective?"
"Are you building something similar, or evaluating from a hiring angle?"
"Just curious — personal interest, or exploring for your organization?"
```

### **2. Adaptive Depth Escalation**

**Detection → Depth Adjustment**:

| Detected Context | Depth Level | Content Style |
|-----------------|-------------|---------------|
| Personal project | Medium | Code examples, tutorials, learning resources |
| Company/hiring | High | Enterprise patterns, metrics, ROI, scalability |
| Casual interest | Low | Accessible analogies, fun facts, plain English |
| Hiring manager | Very High | Architecture diagrams, cost analysis, team practices |

### **3. Natural Information Gathering**

**Progression** (after hiring context detected):

1. **First Question**: Role type (engineering vs hiring vs casual)
2. **Second Question**: Organization context (company, team, challenges)
3. **Third Question**: Position details (role, timeline, requirements)
4. **Fourth Question**: Decision-making authority (hiring manager, team lead, recruiter)

**Tone**: Conversational curiosity, not interrogation. If user doesn't want to share, gracefully move on.

### **4. Enterprise Value Framing**

**When hiring context detected**, inject:

- **Metrics Tables**: Latency, success rate, cost per query, grounding accuracy
- **Architecture Diagrams**: Scalability, microservices, serverless deployment
- **Cost Analysis**: Development cost, operational cost, ROI projections
- **Production Practices**: Code reviews, testing, observability, CI/CD

**Example**:
```markdown
| Metric | Value | Relevance |
|--------|-------|-----------|
| **Latency** | 2.3s | Demonstrates optimized async orchestration |
| **Success Rate** | 93.8% | Reliable pipeline under varied queries |
| **RAG Similarity** | 0.81 avg | Evidence of retrieval precision |
```

### **5. Conversion Hooks**

**Timing**: After demonstrating substantial value (2-3 meaningful exchanges)

**Natural Offers**:
- "Would it be helpful if I sent you Noah's résumé or LinkedIn?"
- "If you're hiring, I can share Noah's background and code samples."
- "Happy to send Noah's résumé if you'd like to explore further."

**Avoid**:
- ❌ "Let me know if you want his résumé" (passive)
- ❌ "Can I send you his résumé?" (pushy)
- ❌ Offering résumé in first message (too aggressive)

## Testing Plan

### **Local Testing** (Streamlit)

```bash
cd /Users/noahdelacalzada/NoahsAIAssistant/NoahsAIAssistant-
streamlit run src/main.py
```

**Test Scenarios**:

1. **Hiring Manager (Technical)**:
   - User: "Hello"
   - Expected: Greeting with soft profiling question
   - User: "I'm exploring AI from a hiring perspective"
   - Expected: Adaptive depth escalation (enterprise framing)
   - User: "We're hiring a GenAI engineer in Q4"
   - Expected: Information gathering (company, position, timeline)
   - User: "We're with TechCorp, hiring a Senior AI Engineer"
   - Expected: Conversion hook (offer résumé)

2. **Software Developer**:
   - User: "Hey, checking this out"
   - Expected: Greeting with "building vs exploring" question
   - User: "Building something similar for my company"
   - Expected: Enterprise patterns + team practices
   - User: "Just personal project"
   - Expected: Code examples + tutorials

3. **Casual Visitor**:
   - User: "What is this?"
   - Expected: Accessible explanation + "personal vs organizational" question
   - User: "Personal interest"
   - Expected: Stay educational, no hiring push
   - User: "Exploring for my organization"
   - Expected: Business value framing + ROI examples

### **Validation Criteria**

✅ Greetings end with soft profiling questions (not generic "What brings you here?")
✅ Follow-ups include adaptive discovery questions
✅ Depth escalates when hiring/company context detected
✅ Enterprise value framing appears for business contexts
✅ Résumé offer happens naturally after value demonstration
✅ Tone stays warm and curious, never pushy or transactional
✅ Casual visitors get educational content without hiring pressure

## Deployment

### **Commit Message**
```bash
git commit -m "🎯 Enhance: Adaptive Discovery - Soft Profiling & Intelligent Depth Escalation

- Updated all role prompts with adaptive discovery sections
- Added soft profiling questions to all greetings
- Implemented adaptive depth escalation based on detected context
- Enhanced enterprise value framing for hiring scenarios
- Natural information gathering and conversion hooks
- Maintains warm, curious tone - never pushy

Based on PORTFOLIA_ADAPTIVE_DISCOVERY.md conversation example.
All prompts updated: technical/nontechnical HM, software dev, casual visitor."
```

### **Production Verification**

After deployment, verify:

1. ✅ Greetings show soft profiling questions
2. ✅ Follow-ups adapt based on user responses
3. ✅ Enterprise framing appears when hiring context detected
4. ✅ Résumé offers happen naturally (not in first message)
5. ✅ Casual visitors don't get hiring pressure

## Impact

### **User Experience Improvements**

| Before | After |
|--------|-------|
| Generic greetings | Soft profiling questions |
| Same depth for everyone | Adaptive escalation |
| Passive resume mentions | Natural conversion hooks |
| Missing hiring intelligence | Detects & adapts to hiring context |

### **Expected Outcomes**

1. **Higher Hiring Manager Conversion**: Natural profiling → résumé offers → interviews
2. **Better Developer Engagement**: Code examples for learners, enterprise patterns for companies
3. **Improved Casual Experience**: No hiring pressure, pure education
4. **Smarter Intelligence**: System learns company, position, timeline naturally

## Related Documentation

- **Reference Example**: `PORTFOLIA_ADAPTIVE_DISCOVERY.md` - Gold standard conversation
- **Conversation Flow**: `PORTFOLIA_CONVERSATION_EXAMPLE.md` - 5-step rhythm structure
- **Resume Distribution**: `docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md` - Existing system
- **Personality Guide**: `docs/context/CONVERSATION_PERSONALITY.md` - Tone and warmth

## Next Steps

1. ✅ **Implementation Complete**: All prompts and greetings updated
2. ⏳ **Local Testing**: Verify all 3 role scenarios work as expected
3. ⏳ **Commit & Deploy**: Push to production with descriptive commit message
4. ⏳ **Production Validation**: Test live deployment with all role types
5. ⏳ **Analytics Review**: Monitor hiring signal detection and résumé conversion rates

---

**Implementation Date**: October 19, 2025
**Implemented By**: GitHub Copilot
**Status**: Ready for Testing & Deployment
