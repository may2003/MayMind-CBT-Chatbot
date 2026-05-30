import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env

TESTS_DIR = Path("tests")
REPORTS_DIR = TESTS_DIR / "reports"

def run_tests(test_type, extra_args=None):
    """Run tests of a specific type and capture results
    
    Args:
        test_type: The type of test (unit, integration, whitebox, blackbox, live_api)
        extra_args: Additional command line arguments for pytest
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    print(f"\n=== Running {test_type.title()} Tests ===\n")
    
    # Set up command
    cmd = [sys.executable, "-m", "pytest", str(TESTS_DIR / test_type), "-v"]
    
    # Add coverage reporting for unit tests
    if test_type == "unit":
        cmd.extend(["--cov=ai", "--cov-report=term"])
    
    # Add any extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    # Skip live API tests if no API key
    if test_type == "live_api" and not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Skipping live API tests: No API key found in environment variables.")
        return True  # Skip but don't fail the build
    
    # Run the tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("ERRORS:", result.stderr)
    
    # Parse results to JSON
    passed = result.returncode == 0
    
    # Count tests from output
    test_count = result.stdout.count("PASSED") + result.stdout.count("FAILED") + result.stdout.count("SKIPPED")
    pass_count = result.stdout.count("PASSED")
    skip_count = result.stdout.count("SKIPPED")
    
    # Extract coverage if available
    coverage = None
    if "TOTAL" in result.stdout:
        for line in result.stdout.split("\n"):
            if "TOTAL" in line:
                try:
                    coverage = int(line.split()[-1].replace("%", ""))
                except (ValueError, IndexError):
                    pass
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "passed": passed,
        "test_count": test_count,
        "pass_count": pass_count,
        "skip_count": skip_count,
        "pass_percentage": (pass_count / (test_count - skip_count) * 100) if (test_count - skip_count) > 0 else 0
    }
    
    if coverage is not None:
        results["coverage"] = coverage
    
    # Save results
    REPORTS_DIR.mkdir(exist_ok=True, parents=True)
    with open(REPORTS_DIR / f"{test_type}_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return passed

def main():
    parser = argparse.ArgumentParser(description="Run CBT Chatbot tests")
    parser.add_argument("--live-api", action="store_true", 
                        help="Run tests using the live OpenAI API (costs money)")
    parser.add_argument("--test-type", choices=["unit", "integration", "whitebox", "blackbox", "live_api", "all"],
                        default="all", help="Specify which tests to run")
    args = parser.parse_args()
    
    results = {}
    
    # Determine which tests to run
    test_types = ["unit", "integration", "whitebox", "blackbox"]
    if args.test_type != "all":
        test_types = [args.test_type]
    
    # Add live API tests if requested
    if args.live_api and (args.test_type == "all" or args.test_type == "live_api"):
        test_types.append("live_api")
    
    # Run selected tests
    for test_type in test_types:
        results[f"{test_type}_tests_passed"] = run_tests(test_type)
    
    # Create report directory
    REPORTS_DIR.mkdir(exist_ok=True, parents=True)
    
    # Add timestamp
    results["timestamp"] = datetime.now().isoformat()
    
    # Save summary
    summary_file = REPORTS_DIR / f"test_run_summary_{datetime.now().strftime('%Y%m%d%H%M')}.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)
    
    # Check if all tests passed
    if all(results.values()):
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. See reports for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())