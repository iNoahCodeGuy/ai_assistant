# Testing Documentation

This directory contains testing strategies, checklists, and quality assurance documentation.

## Purpose

Centralized location for all testing-related documentation:
- Test strategies and methodologies
- Feature testing checklists
- QA procedures and standards
- Test coverage reports

## Contents

- **ROLE_FUNCTIONALITY_CHECKLIST.md**: Manual testing checklist for role-specific behavior
- Future: Test strategy docs, coverage reports, testing guides

## How to Use

### For Developers
- **Before implementing feature**: Check if test checklist exists
- **After implementing feature**: Run through relevant checklist
- **Adding new feature**: Create or update testing checklist

### For QA
- **Manual testing**: Use checklists systematically
- **Regression testing**: Verify all checklist items after changes
- **Bug reporting**: Reference checklist item that failed

### For Code Reviewers
- **PR review**: Check if tests added/updated
- **Quality gate**: Ensure checklist items pass
- **Documentation**: Verify test docs updated

## Related Documentation

- **QA Strategy**: `docs/QA_STRATEGY.md` (overall testing approach)
- **Role Specifications**: `docs/ROLE_FEATURES.md` (what to test)
- **Automated Tests**: `tests/` directory (pytest tests)

## Testing Pyramid

```
           /\
          /  \
         / E2E \         (Manual checklists)
        /------\
       /  Integ \        (API tests, integration tests)
      /----------\
     /    Unit    \      (pytest suite in tests/)
    /--------------\
```

This directory focuses on **E2E/manual testing documentation**.
Automated tests live in `tests/` directory.

## Checklist Format

Each checklist should include:
1. **Scope**: What feature/area does this cover?
2. **Prerequisites**: What setup is needed?
3. **Test Scenarios**: Step-by-step testing instructions
4. **Pass Criteria**: How to know if test passed
5. **Failure Handling**: What to do if test fails
6. **Related Tests**: Links to automated tests covering same area
