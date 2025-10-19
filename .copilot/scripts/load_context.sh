#!/bin/bash
# .copilot/scripts/load_context.sh
# Automated context loading for AI-assisted development
# Usage: ./load_context.sh [mode]
# Modes: feature, test, deploy, architecture, role, default

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONTEXT_MODE="${1:-default}"

echo -e "${BLUE}🤖 Loading AI context for: ${YELLOW}${CONTEXT_MODE}${NC}"
echo ""

# Tier 1: Always load (master docs)
TIER_1=(
  "docs/context/PROJECT_REFERENCE_OVERVIEW.md"
  "docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md"
  "docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md"
  "docs/context/CONVERSATION_PERSONALITY.md"
)

# Initialize docs array with Tier 1
DOCS_TO_LOAD=("${TIER_1[@]}")

# Add mode-specific docs
case "$CONTEXT_MODE" in
  feature)
    echo -e "${GREEN}📁 Feature development mode${NC}"
    DOCS_TO_LOAD+=(
      "CONTINUE_HERE.md"
      "docs/QA_STRATEGY.md"
      ".github/copilot-instructions.md"
      "docs/ROLE_FEATURES.md"
      "docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md"
    )
    TEMPLATE=".copilot/templates/implement_feature.md"
    ;;

  test)
    echo -e "${GREEN}🧪 Testing & debugging mode${NC}"
    DOCS_TO_LOAD+=(
      "docs/QA_STRATEGY.md"
      ".github/copilot-instructions.md"
      "CONTINUE_HERE.md"
      "docs/features/ERROR_HANDLING_IMPLEMENTATION.md"
    )
    TEMPLATE=".copilot/templates/fix_tests.md"
    ;;

  deploy)
    echo -e "${GREEN}🚀 Deployment mode${NC}"
    DOCS_TO_LOAD+=(
      "WEEK_1_LAUNCH_GAMEPLAN.md"
      "docs/platform_operations.md"
      "docs/LANGGRAPH_ALIGNMENT.md"
      "docs/QA_STRATEGY.md"
      "docs/EXTERNAL_SERVICES.md"
    )
    TEMPLATE=".copilot/templates/deploy_production.md"
    ;;

  architecture)
    echo -e "${GREEN}🏗️  Architecture decision mode${NC}"
    DOCS_TO_LOAD+=(
      "docs/LANGGRAPH_ALIGNMENT.md"
      "docs/QA_STRATEGY.md"
      "docs/RAG_ENGINE.md"
      "WEEK_1_LAUNCH_GAMEPLAN.md"
    )
    TEMPLATE=".copilot/templates/architecture_decision.md"
    ;;

  role)
    echo -e "${GREEN}🎭 Role-specific behavior mode${NC}"
    DOCS_TO_LOAD+=(
      "docs/ROLE_FEATURES.md"
      "docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md"
      "docs/context/CONVERSATION_PERSONALITY.md"
    )
    TEMPLATE=""
    ;;

  default)
    echo -e "${GREEN}📚 Default context (general development)${NC}"
    DOCS_TO_LOAD+=(
      "CONTINUE_HERE.md"
      ".github/copilot-instructions.md"
    )
    TEMPLATE=""
    ;;

  *)
    echo -e "${RED}❌ Unknown mode: ${CONTEXT_MODE}${NC}"
    echo ""
    echo "Usage: $0 [mode]"
    echo ""
    echo "Available modes:"
    echo "  feature       - Implementing new features"
    echo "  test          - Fixing tests, debugging"
    echo "  deploy        - Production deployment"
    echo "  architecture  - Architecture decisions"
    echo "  role          - Role-specific behaviors"
    echo "  default       - General development (or omit mode)"
    echo ""
    exit 1
    ;;
esac

# Change to repository root
cd "$REPO_ROOT"

# Verify all documents exist
echo -e "${BLUE}📋 Verifying documents...${NC}"
MISSING_DOCS=()
for doc in "${DOCS_TO_LOAD[@]}"; do
  if [ ! -f "$doc" ]; then
    MISSING_DOCS+=("$doc")
  fi
done

if [ ${#MISSING_DOCS[@]} -gt 0 ]; then
  echo -e "${YELLOW}⚠️  Warning: Some documents are missing:${NC}"
  for doc in "${MISSING_DOCS[@]}"; do
    echo -e "  ${RED}✗${NC} $doc"
  done
  echo ""
  echo "Continuing with available documents..."
  echo ""
fi

# Display what will be loaded
echo -e "${BLUE}📂 Loading ${#DOCS_TO_LOAD[@]} documents:${NC}"
for doc in "${DOCS_TO_LOAD[@]}"; do
  if [ -f "$doc" ]; then
    echo -e "  ${GREEN}✓${NC} $doc"
  fi
done
echo ""

# Check if VSCode CLI is available
if command -v code &> /dev/null; then
  echo -e "${GREEN}📖 Opening in VSCode...${NC}"

  # Open all documents in VSCode
  for doc in "${DOCS_TO_LOAD[@]}"; do
    if [ -f "$doc" ]; then
      code "$doc"
    fi
  done

  # Open template if specified
  if [ -n "$TEMPLATE" ] && [ -f "$TEMPLATE" ]; then
    echo -e "${BLUE}📝 Opening conversation template...${NC}"
    code "$TEMPLATE"
  fi

  echo ""
  echo -e "${GREEN}✅ Context loaded in VSCode${NC}"
  echo ""

  # Provide next steps
  if [ -n "$TEMPLATE" ]; then
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "  1. Review the opened documents"
    echo "  2. Open conversation template: ${YELLOW}$TEMPLATE${NC}"
    echo "  3. Copy template into AI chat"
    echo "  4. Fill in [PLACEHOLDERS] with actual values"
    echo "  5. Start working with AI assistant!"
  else
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo "  1. Review the opened documents"
    echo "  2. Start conversation with AI assistant"
    echo "  3. Reference specific docs as needed"
  fi

else
  # Fallback: display in terminal
  echo -e "${YELLOW}⚠️  VSCode CLI not found. Displaying in terminal...${NC}"
  echo -e "${BLUE}💡 Install VSCode CLI: VSCode → Cmd+Shift+P → 'Shell Command: Install code'${NC}"
  echo ""

  for doc in "${DOCS_TO_LOAD[@]}"; do
    if [ -f "$doc" ]; then
      echo -e "${GREEN}=== $doc ===${NC}"
      head -n 30 "$doc"
      echo "..."
      echo ""
    fi
  done

  echo -e "${BLUE}📋 To view full documents:${NC}"
  for doc in "${DOCS_TO_LOAD[@]}"; do
    if [ -f "$doc" ]; then
      echo "  cat $doc"
    fi
  done
  echo ""

  if [ -n "$TEMPLATE" ]; then
    echo -e "${BLUE}📝 Conversation template:${NC}"
    echo "  cat $TEMPLATE"
  fi
fi

# Summary
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Context loading complete!${NC}"
echo ""
echo -e "${BLUE}Mode:${NC} ${YELLOW}$CONTEXT_MODE${NC}"
echo -e "${BLUE}Documents:${NC} ${#DOCS_TO_LOAD[@]} loaded"
if [ -n "$TEMPLATE" ]; then
  echo -e "${BLUE}Template:${NC} $TEMPLATE"
fi
echo ""
echo -e "${BLUE}💡 Pro tip:${NC} Reference docs in AI prompts:"
echo '   "According to SYSTEM_ARCHITECTURE_SUMMARY.md, the RAG pipeline..."'
echo ""
echo -e "${BLUE}🔄 Change mode:${NC} ./.copilot/scripts/load_context.sh [feature|test|deploy|architecture|role]"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit 0
