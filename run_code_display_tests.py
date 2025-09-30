#!/usr/bin/env python3
"""Test runner for code display functionality.

Provides convenient commands for running different test categories
and generating reports for code display testing.
"""
import subprocess
import sys
import argparse
import time
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=False)
    end_time = time.time()
    
    duration = end_time - start_time
    status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
    print(f"\n{status} - Completed in {duration:.1f}s")
    
    return result.returncode == 0


def run_core_tests():
    """Run core code display accuracy tests."""
    cmd = "python -m pytest tests/test_code_display_accuracy.py -v"
    return run_command(cmd, "Core Code Display Accuracy Tests")


def run_edge_case_tests():
    """Run edge case and robustness tests."""
    cmd = "python -m pytest tests/test_code_display_edge_cases.py -v"
    return run_command(cmd, "Edge Case & Robustness Tests")


def run_ci_tests():
    """Run CI/CD integration tests."""
    cmd = "python -m pytest tests/test_code_display_ci.py -v"
    return run_command(cmd, "CI/CD Integration Tests")


def run_all_code_display_tests():
    """Run all code display related tests."""
    cmd = "python -m pytest tests/test_code_display_*.py -v"
    return run_command(cmd, "All Code Display Tests")


def run_with_coverage():
    """Run tests with coverage report."""
    cmd = ("python -m pytest tests/test_code_display_*.py "
           "--cov=src.core.rag_engine "
           "--cov=src.agents.role_router "
           "--cov=src.retrieval.code_index "
           "--cov-report=html "
           "--cov-report=term-missing "
           "-v")
    return run_command(cmd, "Code Display Tests with Coverage")


def run_performance_only():
    """Run only performance-related tests."""
    cmd = "python -m pytest tests/test_code_display_edge_cases.py::TestCodeDisplayPerformance -v"
    return run_command(cmd, "Performance Tests Only")


def run_quick_smoke_test():
    """Run a quick smoke test of core functionality."""
    cmd = ("python -m pytest "
           "tests/test_code_display_accuracy.py::TestCodeDisplayAccuracy::test_code_snippets_include_required_fields "
           "tests/test_code_display_accuracy.py::TestTechnicalResponseGeneration::test_technical_hiring_manager_gets_code "
           "-v")
    return run_command(cmd, "Quick Smoke Test")


def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("📊 GENERATING COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    results = {}
    
    # Run each test suite and collect results
    results['core'] = run_core_tests()
    results['edge_cases'] = run_edge_case_tests()
    results['ci'] = run_ci_tests()
    
    # Generate summary
    print("\n" + "="*60)
    print("📋 TEST REPORT SUMMARY")
    print("="*60)
    
    total_tests = 0
    passed_suites = 0
    
    for suite_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{suite_name.upper():15} {status}")
        if passed:
            passed_suites += 1
        total_tests += 1
    
    print(f"\nOVERALL: {passed_suites}/{total_tests} test suites passed")
    
    if all(results.values()):
        print("🎉 ALL CODE DISPLAY TESTS PASSING!")
        return True
    else:
        print("⚠️  Some test suites failed - check output above")
        return False


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Test runner for Noah's AI Assistant code display functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_code_display_tests.py --all          # Run all tests
  python run_code_display_tests.py --core         # Core functionality only
  python run_code_display_tests.py --smoke        # Quick smoke test
  python run_code_display_tests.py --coverage     # With coverage report
  python run_code_display_tests.py --report       # Full test report
        """
    )
    
    parser.add_argument('--all', action='store_true', 
                       help='Run all code display tests')
    parser.add_argument('--core', action='store_true',
                       help='Run core accuracy tests only')
    parser.add_argument('--edge', action='store_true',
                       help='Run edge case tests only')
    parser.add_argument('--ci', action='store_true',
                       help='Run CI/CD integration tests only')
    parser.add_argument('--coverage', action='store_true',
                       help='Run tests with coverage report')
    parser.add_argument('--performance', action='store_true',
                       help='Run performance tests only')
    parser.add_argument('--smoke', action='store_true',
                       help='Quick smoke test')
    parser.add_argument('--report', action='store_true',
                       help='Generate comprehensive test report')
    
    args = parser.parse_args()
    
    # If no specific option, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 1
    
    # Change to project directory
    project_root = Path(__file__).parent
    import os
    os.chdir(project_root)
    
    success = True
    
    if args.smoke:
        success = run_quick_smoke_test()
    elif args.core:
        success = run_core_tests()
    elif args.edge:
        success = run_edge_case_tests()
    elif args.ci:
        success = run_ci_tests()
    elif args.performance:
        success = run_performance_only()
    elif args.coverage:
        success = run_with_coverage()
    elif args.report:
        success = generate_test_report()
    elif args.all:
        success = run_all_code_display_tests()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
