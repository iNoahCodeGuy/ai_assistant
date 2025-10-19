#!/usr/bin/env python3
"""
Verify Context Documentation

Purpose: Check that all referenced documents exist and are accessible.
Usage: python .copilot/scripts/verify_context.py
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def get_repo_root() -> Path:
    """Get repository root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent.parent


def parse_required_reading() -> List[str]:
    """Parse REQUIRED_READING.md for document paths."""
    repo_root = get_repo_root()
    required_reading = repo_root / ".copilot" / "REQUIRED_READING.md"

    if not required_reading.exists():
        print(f"{Colors.RED}❌ REQUIRED_READING.md not found{Colors.NC}")
        return []

    docs = []
    with open(required_reading, 'r') as f:
        for line in f:
            # Look for lines with pipe-separated format
            if '|' in line and line.strip().startswith(('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')):
                parts = line.split('|')
                if len(parts) >= 2:
                    doc_path = parts[1].strip()
                    if doc_path.endswith('.md'):
                        docs.append(doc_path)

    return docs


def check_document_exists(doc_path: str, repo_root: Path) -> Tuple[bool, str]:
    """Check if document exists and return status."""
    full_path = repo_root / doc_path

    if not full_path.exists():
        return False, f"Missing: {doc_path}"

    # Check if file is readable
    try:
        with open(full_path, 'r') as f:
            content = f.read(100)  # Read first 100 chars to verify readable
        return True, f"OK: {doc_path}"
    except Exception as e:
        return False, f"Unreadable: {doc_path} ({str(e)})"


def check_master_docs(repo_root: Path) -> List[Tuple[bool, str]]:
    """Check Tier 1 master documents."""
    master_docs = [
        "docs/context/PROJECT_REFERENCE_OVERVIEW.md",
        "docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md",
        "docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md",
        "docs/context/CONVERSATION_PERSONALITY.md",
    ]

    results = []
    for doc in master_docs:
        status, message = check_document_exists(doc, repo_root)
        results.append((status, message))

    return results


def check_key_docs(repo_root: Path) -> List[Tuple[bool, str]]:
    """Check key development documents."""
    key_docs = [
        "CONTINUE_HERE.md",
        "docs/QA_STRATEGY.md",
        ".github/copilot-instructions.md",
        "docs/LANGGRAPH_ALIGNMENT.md",
        "WEEK_1_LAUNCH_GAMEPLAN.md",
    ]

    results = []
    for doc in key_docs:
        status, message = check_document_exists(doc, repo_root)
        results.append((status, message))

    return results


def check_templates(repo_root: Path) -> List[Tuple[bool, str]]:
    """Check conversation templates."""
    templates = [
        ".copilot/templates/implement_feature.md",
        ".copilot/templates/fix_tests.md",
        ".copilot/templates/deploy_production.md",
        ".copilot/templates/architecture_decision.md",
    ]

    results = []
    for template in templates:
        status, message = check_document_exists(template, repo_root)
        results.append((status, message))

    return results


def main():
    """Main verification function."""
    print(f"{Colors.BLUE}🔍 Verifying AI Context Documentation{Colors.NC}")
    print("")

    repo_root = get_repo_root()
    print(f"{Colors.BLUE}Repository root:{Colors.NC} {repo_root}")
    print("")

    all_passed = True

    # Check master docs (Tier 1)
    print(f"{Colors.BLUE}📚 Tier 1: Master Documents{Colors.NC}")
    master_results = check_master_docs(repo_root)
    for passed, message in master_results:
        if passed:
            print(f"  {Colors.GREEN}✓{Colors.NC} {message}")
        else:
            print(f"  {Colors.RED}✗{Colors.NC} {message}")
            all_passed = False
    print("")

    # Check key development docs
    print(f"{Colors.BLUE}📋 Key Development Documents{Colors.NC}")
    key_results = check_key_docs(repo_root)
    for passed, message in key_results:
        if passed:
            print(f"  {Colors.GREEN}✓{Colors.NC} {message}")
        else:
            print(f"  {Colors.RED}✗{Colors.NC} {message}")
            all_passed = False
    print("")

    # Check templates
    print(f"{Colors.BLUE}📝 Conversation Templates{Colors.NC}")
    template_results = check_templates(repo_root)
    for passed, message in template_results:
        if passed:
            print(f"  {Colors.GREEN}✓{Colors.NC} {message}")
        else:
            print(f"  {Colors.RED}✗{Colors.NC} {message}")
            all_passed = False
    print("")

    # Check documents from REQUIRED_READING.md
    print(f"{Colors.BLUE}📖 Documents from REQUIRED_READING.md{Colors.NC}")
    required_docs = parse_required_reading()
    if required_docs:
        required_results = []
        for doc in required_docs:
            status, message = check_document_exists(doc, repo_root)
            required_results.append((status, message))

        # Show summary (not all docs to avoid clutter)
        passed_count = sum(1 for s, _ in required_results if s)
        total_count = len(required_results)

        if passed_count == total_count:
            print(f"  {Colors.GREEN}✓ All {total_count} referenced documents exist{Colors.NC}")
        else:
            print(f"  {Colors.YELLOW}⚠️  {passed_count}/{total_count} documents exist{Colors.NC}")
            print(f"{Colors.BLUE}  Missing documents:{Colors.NC}")
            for passed, message in required_results:
                if not passed:
                    print(f"    {Colors.RED}✗{Colors.NC} {message}")
                    all_passed = False
    else:
        print(f"  {Colors.YELLOW}⚠️  Could not parse REQUIRED_READING.md{Colors.NC}")
    print("")

    # Summary
    print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
    if all_passed:
        print(f"{Colors.GREEN}✅ All documentation verified successfully!{Colors.NC}")
        print("")
        print(f"{Colors.BLUE}💡 Next steps:{Colors.NC}")
        print("  1. Load context: ./.copilot/scripts/load_context.sh [mode]")
        print("  2. Use templates: cat .copilot/templates/[template].md")
        print("  3. Start working with AI assistant!")
        return 0
    else:
        print(f"{Colors.RED}❌ Some documentation is missing or unreadable{Colors.NC}")
        print("")
        print(f"{Colors.YELLOW}📋 Action items:{Colors.NC}")
        print("  1. Create missing documents")
        print("  2. Update REQUIRED_READING.md if docs moved")
        print("  3. Run this script again to verify")
        return 1


if __name__ == "__main__":
    sys.exit(main())
