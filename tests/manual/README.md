# Manual Test Scripts

This directory contains ad-hoc validation and testing scripts used during development. These are **not** part of the automated pytest suite in `tests/`.

## Purpose

Manual test scripts are used for:
- **Quick validation** of specific features or integrations
- **Debugging** connection issues or API problems
- **One-off testing** during development
- **Exploratory testing** of new functionality

## Organization

These scripts are organized by purpose:

### Connection & Setup Tests
- `test_connection.py` - Basic connection validation
- `test_connection_simple.py` - Simplified connection test
- `test_api_keys.py` - Validate API keys are configured

### Feature Tests
- `test_architecture_retrieval.py` - Architecture KB retrieval
- `test_code_integration.py` - Code display integration
- `test_data_display.py` - Analytics display functionality
- `test_enhanced_followups.py` - Follow-up system validation
- `test_personality_improvements.py` - Personality implementation

### Integration Tests
- `test_embedding_formats.py` - Embedding generation/format
- `test_memory_basic.py` - Basic memory functionality
- `test_openai_memory.py` - OpenAI memory integration
- `test_retriever_fixed.py` - Retrieval system validation

### Role & Query Tests
- `test_role_functionality.py` - Role-specific behaviors
- `test_roles_quick.py` - Quick role validation
- `test_backend_stack_query.py` - Backend stack queries
- `test_exact_question.py` - Exact match queries
- `test_vague_query.py` - Vague query handling

### Debugging Scripts
- `test_debug.py` - General debugging utilities
- `test_clean.py` - Cleanup validation
- `test_copilot_verification.py` - Copilot integration check
- `test_direct_search.py` - Direct search validation

### Verification Scripts
- `verify_deployment.py` - Deployment verification
- `verify_production_fix.py` - Production fix validation
- `verify_schema.py` - Schema validation

## Usage

Run individual scripts directly:

```bash
# From project root
python tests/manual/test_connection.py

# Or with specific Python version
python3 tests/manual/test_architecture_retrieval.py
```

## Difference from Automated Tests

| Automated Tests (`tests/`) | Manual Tests (`tests/manual/`) |
|----------------------------|-------------------------------|
| Run via `pytest` | Run directly with `python` |
| Part of CI/CD | Development-only |
| Must pass for deployment | Optional validation |
| Mocked external services | Often use real APIs |
| Fast execution | May be slow |

## Maintenance

These scripts are **not actively maintained** like the pytest suite. They may:
- Use outdated imports
- Reference deprecated functions
- Fail with current codebase

**If you need reliable testing**, use the automated suite in `tests/` instead.

## Adding New Manual Tests

When creating new manual test scripts:

1. Use descriptive names: `test_<feature>_<aspect>.py`
2. Add a docstring explaining the test purpose
3. Consider if it should be an automated test instead
4. Update this README if adding new categories

## Migration to Automated Tests

If a manual test proves useful, consider migrating it to the automated suite:

```bash
# Convert manual test to pytest test
cp tests/manual/test_example.py tests/test_example.py
# Edit to use pytest fixtures and assertions
# Add to CI/CD pipeline
```
