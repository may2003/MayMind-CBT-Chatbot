"""
Master Test Runner for MayMind CBT Assistant

This script runs all automated tests and compiles the results for dissertation documentation.
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def run_unit_tests():
    """Run all unit tests"""
    print("Running unit tests...")
    result = subprocess.run(["pytest", "tests/unit", "-v", "--cov=ai", "--cov-report=term-missing"], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Unit tests passed")
    else:
        print("✗ Unit tests failed")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def run_integration_tests():
    """Run all integration tests"""
    print("Running integration tests...")
    result = subprocess.run(["pytest", "tests/integration", "-v"], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Integration tests passed")
    else:
        print("✗ Integration tests failed")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def run_whitebox_tests():
    """Run white box tests"""
    print("Running white box tests...")
    result = subprocess.run(["pytest", "tests/whitebox", "-v"], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ White box tests passed")
    else:
        print("✗ White box tests failed")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def run_blackbox_tests():
    """Run black box tests that don't require actual API"""
    print("Running black box tests...")
    result = subprocess.run(["pytest", "tests/blackbox", "-v", "-k", "not api"], 
                           capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Black box tests passed")
    else:
        print("✗ Black box tests failed")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def generate_report(results):
    """Generate a JSON report with test results"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "overall_success": all(results.values())
    }
    
    # Create reports directory if it doesn't exist
    os.makedirs("tests/reports", exist_ok=True)
    
    # Write report to file
    report_path = f"tests/reports/test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to {report_path}")
    return report_path

def main():
    """Run all tests and generate report"""
    print("=" * 50)
    print("MayMind CBT Assistant - Automated Test Suite")
    print("=" * 50)
    
    results = {
        "unit_tests": run_unit_tests(),
        "integration_tests": run_integration_tests(),
        "whitebox_tests": run_whitebox_tests(),
        "blackbox_tests": run_blackbox_tests()
    }
    
    report_path = generate_report(results)
    
    # Print summary
    print("\nTest Summary:")
    for test_type, success in results.items():
        print(f"  {test_type}: {'✓ PASSED' if success else '✗ FAILED'}")
    
    print(f"\nOverall result: {'SUCCESS' if all(results.values()) else 'FAILURE'}")
    print(f"Detailed report: {report_path}")
    
    # Return exit code (0 for success, 1 for failure)
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())

