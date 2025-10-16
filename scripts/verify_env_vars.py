#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic script to verify environment variables are properly configured.
Run this locally before deploying to Vercel to catch common issues.

Usage:
    python scripts/verify_env_vars.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, reading from os.environ only")
    pass


def check_env_var(name, required=True):
    """Check if environment variable is set and properly formatted.

    Returns:
        (is_valid, message)
    """
    value = os.getenv(name)

    if not value:
        if required:
            return False, "FAIL {}: NOT SET (required)".format(name)
        else:
            return True, "WARN {}: not set (optional)".format(name)

    # Check for common issues
    issues = []

    # Check for newlines (causes HTTP header errors)
    if '\n' in value or '\r' in value:
        issues.append("contains newline characters")

    # Check for leading/trailing whitespace
    if value != value.strip():
        issues.append("has leading/trailing whitespace")

    # Check length (API keys should be reasonably long)
    if name.endswith("_KEY") or name.endswith("_API_KEY"):
        if len(value) < 20:
            issues.append("seems too short for an API key")

    if issues:
        return False, "FAIL {}: {} (length: {})".format(name, ', '.join(issues), len(value))

    # Mask sensitive values for display
    if len(value) > 20:
        display_value = "{}...{}".format(value[:8], value[-4:])
    else:
        display_value = "{}...".format(value[:4])

    return True, "OK {}: {} (length: {})".format(name, display_value, len(value))


def main():
    """Run all environment variable checks."""
    print("Verifying environment variables...\n")

    # Required variables
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]

    # Optional variables
    optional_vars = [
        "SUPABASE_ANON_KEY",
        "RESEND_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM",
        "LANGSMITH_API_KEY",
    ]

    all_valid = True

    print("Required Variables:")
    for var in required_vars:
        is_valid, message = check_env_var(var, required=True)
        print("  " + message)
        if not is_valid:
            all_valid = False

    print("\nOptional Variables:")
    for var in optional_vars:
        is_valid, message = check_env_var(var, required=False)
        print("  " + message)
        # Optional vars don't affect all_valid

    print("\n" + "="*60)

    if all_valid:
        print("SUCCESS: All required environment variables are properly configured!")
        print("\nNext steps:")
        print("   1. Copy these environment variables to Vercel dashboard")
        print("   2. Ensure you paste values WITHOUT trailing newlines")
        print("   3. Redeploy your Vercel function")
        return 0
    else:
        print("ERROR: Some environment variables have issues!")
        print("\nHow to fix:")
        print("   1. Check your .env file for trailing newlines")
        print("   2. Ensure API keys are complete (no truncation)")
        print("   3. Run this script again to verify")
        return 1


if __name__ == "__main__":
    sys.exit(main())
