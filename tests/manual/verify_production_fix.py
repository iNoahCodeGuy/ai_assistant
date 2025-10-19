#!/usr/bin/env python3
"""Verify production deployment fixes the import_retriever error.

Usage:
    python verify_production_fix.py https://your-app.vercel.app
"""

import sys
import json
import requests
from typing import Dict, Any

def test_production_query(base_url: str, query: str, role: str) -> Dict[str, Any]:
    """Send test query to production API."""
    url = f"{base_url}/api/chat"
    payload = {
        "query": query,
        "role": role,
        "session_id": "production-test-fix"
    }

    print(f"\n🔍 Testing: '{query}' as {role}")
    print(f"📍 URL: {url}")

    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            print(f"📝 Answer length: {len(answer)} chars")
            print(f"📄 First 200 chars: {answer[:200]}...")

            # Check for error messages
            if "encountered an error" in answer.lower():
                print("❌ ERROR: Response still contains error message")
                return {"success": False, "error": "Error message in response"}
            else:
                print("✅ SUCCESS: No error message detected")
                return {"success": True, "data": data}
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return {"success": False, "error": f"HTTP {response.status_code}"}

    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: Request took longer than 30 seconds")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_production_fix.py https://your-app.vercel.app")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")

    print("=" * 70)
    print("🚀 Production Fix Verification")
    print("=" * 70)
    print(f"Target: {base_url}")
    print(f"Testing import_retriever error handling...")

    # Test cases that previously failed
    test_cases = [
        {
            "query": "how does this product work?",
            "role": "Hiring Manager (technical)",
            "description": "Original failing query"
        },
        {
            "query": "show me the architecture",
            "role": "Software Developer",
            "description": "Code display trigger"
        },
        {
            "query": "why did you use Supabase?",
            "role": "Software Developer",
            "description": "Import explanation trigger"
        },
        {
            "query": "tell me about your experience",
            "role": "Hiring Manager (nontechnical)",
            "description": "Regular career query"
        }
    ]

    results = []
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'=' * 70}")
        print(f"Test {i}/{len(test_cases)}: {case['description']}")
        print(f"{'=' * 70}")

        result = test_production_query(
            base_url,
            case["query"],
            case["role"]
        )
        result["test_case"] = case["description"]
        results.append(result)

    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)

    passed = sum(1 for r in results if r.get("success"))
    total = len(results)

    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result.get("success") else "❌ FAIL"
        print(f"{status} - Test {i}: {result['test_case']}")
        if not result.get("success"):
            print(f"         Error: {result.get('error', 'Unknown')}")

    print(f"\n📈 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Production fix verified.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
