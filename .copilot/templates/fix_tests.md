# Template: Fix Failing Tests

**Purpose**: Structured prompt for debugging and fixing test failures

**Usage**: Copy this template into AI chat, replace [PLACEHOLDERS] with actual values

---

## Prompt Template

```
Tests are failing in [TEST_FILE].

## Context to Load

Please reference these documents:
- docs/QA_STRATEGY.md (testing philosophy, LangGraph patterns, design principles)
- .github/copilot-instructions.md (mocking patterns, service factories, conventions)
- CONTINUE_HERE.md (current test status, known issues)
- docs/features/ERROR_HANDLING_IMPLEMENTATION.md (error handling patterns)
- docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md (system flow, dependencies)

## Test Failure Information

**Test File**: [TEST_FILE]
**Failing Tests**: [TEST_1, TEST_2, ...]
**Pass Rate**: [X/Y passing (Z%)]

**Error Output**:
```
[PASTE PYTEST OUTPUT HERE]
```

## Debug Steps

Please perform these steps:

### 1. Root Cause Analysis
- What is the test trying to verify?
- What is actually happening vs. expected?
- Is this a code bug or test bug?
- Are there missing mocks or fixtures?
- Are external services being called incorrectly?

### 2. Identify Fix Strategy
Options:
- **Fix code**: If code is buggy, fix the implementation
- **Fix test**: If test is wrong, fix the test logic
- **Add mocks**: If missing Supabase/OpenAI/service mocks
- **Update expectations**: If requirements changed

### 3. Propose Solution
Provide:
- **Root cause explanation** (1-2 sentences)
- **Proposed fix** (code diff)
- **Rationale** (why this fix is correct)
- **Design principle alignment** (which principles apply)

### 4. Verify Fix
- Confirm fix doesn't break other tests
- Run full test suite: `pytest tests/ -v`
- Check coverage maintained: `pytest --cov=src`

## Expected Deliverables

### 1. Root Cause Analysis
- Clear explanation of what's wrong
- Reference to specific code/test lines
- Mention any related issues (e.g., "same pattern in test_X.py")

### 2. Code Diff for Fix
```diff
--- a/[FILE]
+++ b/[FILE]
@@ -X,Y +X,Z @@
[CONTEXT BEFORE]
-[OLD CODE]
+[NEW CODE]
[CONTEXT AFTER]
```

### 3. Test Verification
```bash
# Commands to verify fix
pytest [TEST_FILE] -v
pytest tests/ -v  # Full suite
```

### 4. Documentation Updates (if needed)
- Update test docstrings if test purpose changed
- Update CONTINUE_HERE.md with new test status
- Add to CHANGELOG.md if fixing a bug (not just test)

## Design Principles Checklist

For the fix, verify:
- [ ] **Testability**: Proper mocking of external dependencies
- [ ] **Reliability**: Error handling covers edge cases
- [ ] **Simplicity**: Fix is minimal, doesn't over-engineer
- [ ] **Maintainability**: Clear test intent, good docstrings

## Common Test Issues

### Missing Mocks
```python
# ❌ Wrong: Calling real Supabase
def test_retrieval():
    rag = RagEngine()  # Tries to connect to real DB

# ✅ Right: Mock Supabase client
def test_retrieval(mock_supabase_client):
    with patch('src.retrieval.pgvector_retriever.create_client',
               return_value=mock_supabase_client):
        rag = RagEngine()
```

### Service Factory Not Used
```python
# ❌ Wrong: Direct instantiation
twilio = TwilioService()  # Crashes if no API key

# ✅ Right: Factory function
twilio = get_twilio_service()  # Returns None gracefully
if twilio:
    twilio.send_sms(...)
```

### State Mutation Issues
```python
# ❌ Wrong: Mutating state directly
state.answer = "new answer"  # Breaks immutability

# ✅ Right: Use helper methods
state.set_answer("new answer")
```

### Incorrect Assertions
```python
# ❌ Wrong: Too specific
assert result.answer == "Hello! I'm Portfolia..."  # Fragile

# ✅ Right: Check behavior
assert len(result.answer) > 0
assert "Portfolia" in result.answer
```

## Additional Notes

[Any context about recent changes, environment, or related issues]

---

Ready to debug when you are!
```

---

## Example: test_error_handling.py Failures

```
Tests are failing in tests/test_error_handling.py.

## Context to Load

Please reference these documents:
- docs/QA_STRATEGY.md (testing philosophy, LangGraph patterns)
- .github/copilot-instructions.md (mocking patterns, service factories)
- CONTINUE_HERE.md (current test status)
- docs/features/ERROR_HANDLING_IMPLEMENTATION.md (error handling patterns)
- docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md (system flow)

## Test Failure Information

**Test File**: tests/test_error_handling.py
**Failing Tests**:
- test_conversation_without_twilio
- test_conversation_without_resend
- test_low_quality_retrieval_fallback

**Pass Rate**: 3/6 passing (50%)

**Error Output**:
```
tests/test_error_handling.py::test_conversation_without_twilio FAILED
tests/test_error_handling.py::test_conversation_without_resend FAILED
tests/test_error_handling.py::test_low_quality_retrieval_fallback FAILED

_________________________ test_conversation_without_twilio _________________________
E   RuntimeError: Failed to initialize pgvector retriever: No Supabase client available

_________________________ test_conversation_without_resend _________________________
E   RuntimeError: Failed to initialize pgvector retriever: No Supabase client available

_________________________ test_low_quality_retrieval_fallback _________________________
E   RuntimeError: Failed to initialize pgvector retriever: No Supabase client available
```

## Debug Steps

[Same as template above]

## Expected Deliverables

[Same as template above]

## Design Principles Checklist

[Same as template above]

## Additional Notes

- Tests are trying to verify graceful degradation when services unavailable
- Issue seems to be missing Supabase mocks (all 3 failures have same error)
- Tests should NOT call real Supabase database
- Need to add mock_supabase_client fixture to conftest.py
- Similar pattern working in test_conversation_flow.py (check for reference)

---

Ready to debug when you are!
```

---

## Tips for Using This Template

### 1. Always Include Test Output
- Copy/paste the actual pytest output
- Include full traceback if available
- Don't paraphrase errors

### 2. Note Recent Changes
- Did you just change code that might affect tests?
- Were dependencies updated (requirements.txt)?
- Did environment variables change?

### 3. Check Related Tests
- Are other tests in same file passing?
- Are similar tests in other files passing?
- This helps isolate the issue

### 4. Reference Working Tests
- If similar tests work elsewhere, mention them
- AI can compare patterns to find the issue

### 5. Verify Environment
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -i [package]

# Check environment variables
echo $OPENAI_API_KEY  # Should be set
echo $SUPABASE_URL    # Should be set
```

---

## After Fixing

### 1. Run Tests Locally
```bash
# Run specific test file
pytest tests/test_error_handling.py -v

# Run full suite
pytest tests/ -v

# Check coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### 2. Verify Fix Quality
- [ ] All tests in file passing?
- [ ] No new failures introduced?
- [ ] Coverage maintained or improved?
- [ ] Test intent clear from docstrings?

### 3. Update Status
```bash
# Update CONTINUE_HERE.md
# Change: "⚠️ test_error_handling.py: 3/6 (50%)"
# To: "✅ test_error_handling.py: 6/6 (100%)"

# Add to CHANGELOG.md
# [Unreleased]
# ### Fixed
# - Fixed test failures in test_error_handling.py (added Supabase mocks)
```

### 4. Commit
```bash
git add tests/test_error_handling.py tests/conftest.py
git commit -m "test: fix error_handling tests with Supabase mocks"
```

---

**Happy debugging! 🐛➡️✅**
