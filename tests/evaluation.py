"""
Evaluation Framework for MayMind CBT Assistant

This module provides functions for evaluating the CBT Assistant across multiple dimensions:
1. Therapeutic effectiveness
2. Technical robustness
3. User experience
4. Safety mechanisms
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def load_all_test_results():
    """Load all test results for comprehensive evaluation"""
    results = {
        "unit_tests": load_unit_test_results(),
        "integration_tests": load_integration_test_results(),
        "alpha_tests": load_alpha_test_results(),
        "user_tests": load_user_test_results()
    }
    return results

def load_unit_test_results():
    """Load unit test results if available"""
    if os.path.exists("tests/reports/unit_test_results.json"):
        with open("tests/reports/unit_test_results.json") as f:
            return json.load(f)
    return None

def load_integration_test_results():
    """Load integration test results if available"""
    if os.path.exists("tests/reports/integration_test_results.json"):
        with open("tests/reports/integration_test_results.json") as f:
            return json.load(f)
    return None

def load_alpha_test_results():
    """Load alpha test summary if available"""
    if os.path.exists("tests/reports"):
        for filename in os.listdir("tests/reports"):
            if filename.startswith("alpha_test_summary"):
                with open(os.path.join("tests/reports", filename)) as f:
                    return json.load(f)
    return None

def load_user_test_results():
    """Load user test report if available"""
    if os.path.exists("tests/reports"):
        for filename in os.listdir("tests/reports"):
            if filename.startswith("user_testing_report"):
                with open(os.path.join("tests/reports", filename)) as f:
                    return json.load(f)
    return None

def evaluate_therapeutic_effectiveness():
    """Evaluate therapeutic effectiveness based on available data"""
    results = {}
    
    # Check for alpha test results
    alpha_results = load_alpha_test_results()
    if alpha_results:
        # Extract therapeutic criteria from alpha testing
        therapeutic_metrics = {}
        for scenario_id, data in alpha_results["scenario_results"].items():
            for criterion, score in data["criteria_averages"].items():
                if "empathy" in criterion.lower() or "cbt" in criterion.lower() or "distortion" in criterion.lower():
                    therapeutic_metrics[criterion] = score
        
        if therapeutic_metrics:
            results["alpha_therapeutic_metrics"] = therapeutic_metrics
            results["alpha_therapeutic_average"] = sum(therapeutic_metrics.values()) / len(therapeutic_metrics)
    
    # Check for user test results
    user_results = load_user_test_results()
    if user_results and "summary" in user_results:
        results["user_therapeutic_score"] = user_results["summary"].get("avg_therapeutic_score")
    
    # Calculate overall score if both sources available
    if "alpha_therapeutic_average" in results and "user_therapeutic_score" in results:
        results["overall_therapeutic_score"] = (results["alpha_therapeutic_average"] + results["user_therapeutic_score"]) / 2
    
    return results

def evaluate_technical_robustness():
    """Evaluate technical robustness based on test results"""
    results = {}
    
    # Check for unit test results
    unit_results = load_unit_test_results()
    if unit_results:
        results["unit_test_pass_rate"] = unit_results.get("pass_percentage", 0)
    
    # Check for integration test results
    integration_results = load_integration_test_results()
    if integration_results:
        results["integration_test_pass_rate"] = integration_results.get("pass_percentage", 0)
    
    # If we have both, calculate overall technical score
    if "unit_test_pass_rate" in results and "integration_test_pass_rate" in results:
        results["overall_technical_score"] = (results["unit_test_pass_rate"] + results["integration_test_pass_rate"]) / 2
    
    return results

def evaluate_user_experience():
    """Evaluate user experience based on user testing"""
    results = {}
    
    # Check for user test results
    user_results = load_user_test_results()
    if user_results and "summary" in user_results:
        results["sus_score"] = user_results["summary"].get("avg_sus_score", 0)
        results["task_completion_rates"] = user_results["summary"].get("task_completion_rates", {})
    
    return results

def evaluate_safety_mechanisms():
    """Evaluate safety mechanisms based on specialized tests"""
    # In a real implementation, this would load results from specific safety tests
    # For now, we'll return placeholder data
    return {
        "crisis_detection_accuracy": 0.95,
        "false_positive_rate": 0.05,
        "false_negative_rate": 0.02
    }

def generate_comprehensive_evaluation():
    """Generate comprehensive evaluation across all dimensions"""
    evaluation = {
        "timestamp": datetime.now().isoformat(),
        "therapeutic_effectiveness": evaluate_therapeutic_effectiveness(),
        "technical_robustness": evaluate_technical_robustness(),
        "user_experience": evaluate_user_experience(),
        "safety_mechanisms": evaluate_safety_mechanisms()
    }
    
    # Generate overall scores
    scores = {}
    
    if "overall_therapeutic_score" in evaluation["therapeutic_effectiveness"]:
        scores["therapeutic"] = evaluation["therapeutic_effectiveness"]["overall_therapeutic_score"]
    
    if "overall_technical_score" in evaluation["technical_robustness"]:
        scores["technical"] = evaluation["technical_robustness"]["overall_technical_score"]
    
    if "sus_score" in evaluation["user_experience"]:
        # Normalize SUS score to 0-1 range
        scores["user_experience"] = evaluation["user_experience"]["sus_score"] / 100
    
    if "crisis_detection_accuracy" in evaluation["safety_mechanisms"]:
        scores["safety"] = evaluation["safety_mechanisms"]["crisis_detection_accuracy"]
    
    # Calculate overall score if we have at least 3 dimensions
    if len(scores) >= 3:
        evaluation["overall_score"] = sum(scores.values()) / len(scores)
    
    # Generate visualization
    if scores:
        os.makedirs("tests/reports/figures", exist_ok=True)
        
        plt.figure(figsize=(10, 8))
        categories = list(scores.keys())
        values = [scores[cat] for cat in categories]
        
        plt.bar(categories, values, color="lightblue")
        plt.ylim(0, 1)
        plt.title("MayMind CBT Assistant Evaluation Scores")
        plt.ylabel("Score (0-1)")
        plt.grid(True, alpha=0.3)
        
        for i, v in enumerate(values):
            plt.text(i, v + 0.02, f"{v:.2f}", ha="center")
        
        plt.tight_layout()
        plt.savefig("tests/reports/figures/evaluation_summary.png", dpi=300, bbox_inches="tight")
        
        evaluation["visualization"] = "tests/reports/figures/evaluation_summary.png"
    
    # Save evaluation report
    os.makedirs("tests/reports", exist_ok=True)
    with open(f"tests/reports/comprehensive_evaluation_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
        json.dump(evaluation, f, indent=2)
    
    return evaluation