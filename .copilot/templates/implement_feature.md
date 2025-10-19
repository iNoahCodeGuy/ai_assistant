# Template: Implement New Feature

**Purpose**: Structured prompt for implementing new features with full context

**Usage**: Copy this template into AI chat, replace [PLACEHOLDERS] with actual values

---

## Prompt Template

```
I need to implement [FEATURE_NAME].

## Context to Load

Please reference these documents:
- docs/context/PROJECT_REFERENCE_OVERVIEW.md (roles, value prop)
- docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md (control flow)
- docs/context/CONVERSATION_PERSONALITY.md (tone, voice)
- docs/QA_STRATEGY.md (design principles, testing standards)
- .github/copilot-instructions.md (coding conventions)
- CONTINUE_HERE.md (current status)
- [RELATED_FEATURE_DOC] (if similar feature exists)

## Feature Requirements

**User Story**: As a [USER_ROLE], I want to [ACTION] so that [BENEFIT].

**Acceptance Criteria**:
1. [CRITERION_1]
2. [CRITERION_2]
3. [CRITERION_3]

**Related Files** (if known):
- [FILE_1]
- [FILE_2]

**Design Constraints**:
- Must follow 8 design principles (see QA_STRATEGY.md)
- Must align with LangGraph conversation flow
- Must maintain current test coverage (95%+)

## Expected Deliverables

Please provide:

### 1. Implementation Plan (3-5 steps)
- Break down into small, testable chunks
- Identify affected files
- Note any dependencies or prerequisites

### 2. Code Changes (Git-style diffs)
- Keep diffs ≤150 lines per file
- Include 3-5 lines context before/after changes
- Follow project conventions (see .github/copilot-instructions.md)

### 3. Test Cases
- **Happy path**: Normal usage scenarios
- **Edge cases**: Boundary conditions, empty inputs
- **Error cases**: Invalid inputs, service failures
- Use pytest, follow existing test patterns

### 4. Documentation Updates
- Update relevant docs in docs/features/
- Add entry to CHANGELOG.md
- Update CONTINUE_HERE.md with new status

### 5. Design Principles Justification
For each change, explain which design principles apply:
- **Cohesion & SRP**: Does it do one thing well?
- **Encapsulation**: Are internals hidden?
- **Loose Coupling**: Can components be swapped?
- **Reusability**: Can code be reused elsewhere?
- **Portability**: Does it work across environments?
- **Defensibility**: Input validation, error handling?
- **Maintainability**: Clear naming, small functions, tests?
- **Simplicity (KISS/DRY/YAGNI)**: Avoid over-engineering?

## QA Checklist

Before considering complete, verify:
- [ ] All tests passing: `pytest tests/ -v`
- [ ] No hardcoded values (use environment variables)
- [ ] Error handling in place (graceful degradation)
- [ ] Follows import patterns (use langchain_compat layer)
- [ ] Service factories used (get_resend_service, get_twilio_service)
- [ ] State immutability preserved (use .stash(), .set_answer())
- [ ] LangSmith tracing enabled (if LLM calls involved)
- [ ] Documentation updated
- [ ] CONTINUE_HERE.md reflects new status

## Additional Notes

[Any other context, constraints, or requirements]

---

Ready to implement when you are!
```

---

## Example: Resume Download Button

```
I need to implement Resume Download Button.

## Context to Load

Please reference these documents:
- docs/context/PROJECT_REFERENCE_OVERVIEW.md (roles, value prop)
- docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md (control flow)
- docs/context/CONVERSATION_PERSONALITY.md (tone, voice)
- docs/QA_STRATEGY.md (design principles, testing standards)
- .github/copilot-instructions.md (coding conventions)
- CONTINUE_HERE.md (current status)
- docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md (resume feature context)
- docs/EXTERNAL_SERVICES.md (Supabase Storage patterns)

## Feature Requirements

**User Story**: As a hiring manager, I want to download Noah's resume with one click so that I can share it with my team or review it offline.

**Acceptance Criteria**:
1. "Download Resume" button appears in chat interface
2. Clicking button downloads PDF from Supabase Storage
3. File is named "Noah_DelaCal_Resume.pdf"
4. Download is logged to analytics
5. Works on all devices (desktop, mobile, tablet)

**Related Files**:
- app/components/chat/ChatMessage.tsx (add button to assistant messages)
- src/services/storage_service.py (get signed URL for resume)
- api/resume.py (new endpoint to generate download URL)

**Design Constraints**:
- Must follow 8 design principles
- Must use Supabase Storage (not local files)
- Must work with current Next.js frontend
- Must maintain test coverage 95%+

## Expected Deliverables

[Same as template above]

## QA Checklist

[Same as template above]

## Additional Notes

- Resume is already uploaded to Supabase Storage bucket "resumes"
- Use storage_service.get_signed_url() to generate time-limited download link
- Button should only appear in hiring manager roles (technical + nontechnical)
- Log download event to analytics for tracking

---

Ready to implement when you are!
```

---

## Tips for Using This Template

### 1. Be Specific
- Replace [FEATURE_NAME] with actual feature name
- Fill in [USER_ROLE], [ACTION], [BENEFIT] with real user story
- List concrete acceptance criteria (not "it should work")

### 2. Provide Context
- Link to related features (e.g., if building on existing work)
- Mention affected files if you know them
- Note any constraints or requirements

### 3. Set Expectations
- Use the "Expected Deliverables" checklist as-is
- This ensures AI provides plan + code + tests + docs
- Saves back-and-forth questions

### 4. Quality First
- Always include QA checklist
- Reference design principles explicitly
- Maintain test coverage

### 5. Iterate
- After AI provides initial implementation, review carefully
- Ask follow-up questions if anything unclear
- Request clarification on design decisions

---

## Common Mistakes to Avoid

❌ **Don't** be vague: "Add a button"
✅ **Do** be specific: "Add 'Download Resume' button that fetches signed URL from Supabase Storage"

❌ **Don't** skip context: Start coding immediately
✅ **Do** load context first: Reference relevant docs

❌ **Don't** forget tests: "Just show me the code"
✅ **Do** require tests: "Include happy path + edge cases + error handling tests"

❌ **Don't** ignore design principles: Accept any implementation
✅ **Do** require justification: "Explain which design principles this follows"

❌ **Don't** skip documentation: Code only
✅ **Do** update docs: CHANGELOG.md, feature docs, CONTINUE_HERE.md

---

## After Implementation

### 1. Verify Locally
```bash
# Run tests
pytest tests/ -v

# Test in browser
npm run dev
# Navigate to feature, test manually
```

### 2. Code Review
- Review diffs carefully
- Check against design principles
- Verify tests cover edge cases

### 3. Update Status
- Update CONTINUE_HERE.md with completion
- Add entry to CHANGELOG.md
- Mark task as done in WEEK_1_LAUNCH_GAMEPLAN.md (if applicable)

### 4. Commit
```bash
git add [files]
git commit -m "feat: [FEATURE_NAME] - [brief description]"
git push origin [branch]
```

---

**Happy feature building! 🚀**
