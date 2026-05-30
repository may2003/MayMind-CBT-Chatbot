"""
User Testing Protocol for MayMind CBT Assistant

This file defines the protocol for structured user testing, including tasks,
metrics, and data collection instruments.
"""

import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Define user testing tasks
USER_TESTING_TASKS = [
    {
        "id": "task1",
        "name": "Complete Initial Assessment",
        "instructions": "Start the application and complete the PHQ-9 and GAD-7 assessments.",
        "success_criteria": "PHQ-9 and GAD-7 scores are recorded and user proceeds to main interface.",
        "metrics": ["completion_time", "errors", "assistance_needed"]
    },
    {
        "id": "task2",
        "name": "Have a Therapeutic Conversation",
        "instructions": "Share a concern with the chatbot and engage in at least 3 exchanges.",
        "success_criteria": "User completes 3+ exchanges and gets therapeutically appropriate responses.",
        "metrics": ["completion_time", "perceived_empathy", "perceived_helpfulness"]
    },
    {
        "id": "task3",
        "name": "Use the Thought Journal",
        "instructions": "Navigate to the thought journal and record a negative thought.",
        "success_criteria": "Thought is successfully recorded in the system.",
        "metrics": ["completion_time", "errors", "perceived_usefulness"]
    },
    {
        "id": "task4",
        "name": "Review Session Summary",
        "instructions": "End the session and review the session summary.",
        "success_criteria": "User can view summary that accurately reflects their session.",
        "metrics": ["perceived_accuracy", "perceived_usefulness"]
    }
]

# System Usability Scale (SUS) questions
SUS_QUESTIONS = [
    "I think that I would like to use this system frequently",
    "I found the system unnecessarily complex",
    "I thought the system was easy to use",
    "I think that I would need the support of a technical person to use this system",
    "I found the various functions in this system were well integrated",
    "I thought there was too much inconsistency in this system",
    "I would imagine that most people would learn to use this system very quickly",
    "I found the system very cumbersome to use",
    "I felt very confident using the system",
    "I needed to learn a lot of things before I could get going with this system"
]

# Therapeutic Effectiveness questions (custom)
THERAPEUTIC_QUESTIONS = [
    "The chatbot understood my concerns",
    "The chatbot's responses were empathetic",
    "The chatbot helped me think about my situation differently",
    "The chatbot asked relevant and thoughtful questions",
    "The tools (thought journal, etc.) were helpful",
    "I would use this system as a supplement to therapy",
    "I learned something useful about my thoughts or feelings",
    "The language used by the chatbot felt natural",
    "I felt comfortable sharing my concerns with the chatbot",
    "The session summary accurately captured our conversation"
]

def record_user_test_results(participant_id, demographics, task_results, sus_scores, therapeutic_scores, qualitative_feedback):
    """
    Record results from user testing
    
    Parameters:
    - participant_id: Anonymous identifier for the participant
    - demographics: Basic demographic information
    - task_results: Results for each task
    - sus_scores: System Usability Scale scores (1-5 for each question)
    - therapeutic_scores: Therapeutic effectiveness scores (1-5)
    - qualitative_feedback: Open-ended comments
    """
    result = {
        "participant_id": participant_id,
        "timestamp": datetime.now().isoformat(),
        "demographics": demographics,
        "task_results": task_results,
        "sus_scores": sus_scores,
        "therapeutic_scores": therapeutic_scores,
        "qualitative_feedback": qualitative_feedback
    }
    
    # Calculate SUS score (0-100)
    sus_total = 0
    for i, score in enumerate(sus_scores):
        # For odd questions (0, 2, 4, 6, 8), score is (response - 1)
        # For even questions (1, 3, 5, 7, 9), score is (5 - response)
        if i % 2 == 0:
            sus_total += (score - 1)
        else:
            sus_total += (5 - score)
    
    result["sus_total"] = sus_total * 2.5  # Multiply by 2.5 to get 0-100 scale
    
    # Calculate therapeutic effectiveness score (average of all questions)
    result["therapeutic_total"] = sum(therapeutic_scores) / len(therapeutic_scores)
    
    # Create directory if it doesn't exist
    os.makedirs("tests/reports/user", exist_ok=True)
    
    # Save results to JSON file
    filename = f"tests/reports/user/participant_{participant_id}_{datetime.now().strftime('%Y%m%d%H%M')}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2)
    
    return filename

def analyze_user_testing_results():
    """Analyze all user testing results and generate visualizations"""
    results = []
    
    # Load all result files
    if not os.path.exists("tests/reports/user"):
        return {"error": "No user test results found"}
    
    for filename in os.listdir("tests/reports/user"):
        if filename.endswith(".json"):
            with open(os.path.join("tests/reports/user", filename)) as f:
                results.append(json.load(f))
    
    if not results:
        return {"error": "No user test results found"}
    
    # Create dataframe for analysis
    df = pd.DataFrame([{
        "participant_id": r["participant_id"],
        "age": r["demographics"].get("age", 0),
        "gender": r["demographics"].get("gender", "Unknown"),
        "tech_comfort": r["demographics"].get("tech_comfort", 0),
        "therapy_experience": r["demographics"].get("therapy_experience", 0),
        "sus_score": r["sus_total"],
        "therapeutic_score": r["therapeutic_total"],
        **{f"task_{t['id']}_time": t.get("completion_time", 0) for t in r["task_results"]},
        **{f"task_{t['id']}_errors": t.get("errors", 0) for t in r["task_results"]}
    } for r in results])
    
    # Generate summary statistics
    summary = {
        "participants": len(results),
        "avg_sus_score": df["sus_score"].mean(),
        "avg_therapeutic_score": df["therapeutic_score"].mean(),
        "task_completion_rates": {
            task["id"]: sum(1 for r in results if any(t["id"] == task["id"] and t.get("completed", False) for t in r["task_results"])) / len(results)
            for task in USER_TESTING_TASKS
        }
    }
    
    # Generate visualizations
    os.makedirs("tests/reports/figures", exist_ok=True)
    
    # SUS Score histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df["sus_score"], bins=10, alpha=0.7, color="skyblue")
    plt.axvline(x=df["sus_score"].mean(), color="red", linestyle="--", linewidth=2)
    plt.title("System Usability Scale (SUS) Scores")
    plt.xlabel("SUS Score (0-100)")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.savefig("tests/reports/figures/sus_scores.png", dpi=300, bbox_inches="tight")
    
    # Therapeutic effectiveness scores
    plt.figure(figsize=(12, 8))
    # Calculate average for each question
    question_avgs = []
    for i, question in enumerate(THERAPEUTIC_QUESTIONS):
        avg = sum(r["therapeutic_scores"][i] for r in results) / len(results)
        question_avgs.append(avg)
    
    plt.barh(THERAPEUTIC_QUESTIONS, question_avgs, color="lightgreen")
    plt.title("Therapeutic Effectiveness Scores")
    plt.xlabel("Average Score (1-5)")
    plt.tight_layout()
    plt.savefig("tests/reports/figures/therapeutic_scores.png", dpi=300, bbox_inches="tight")
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "visualizations": [
            "tests/reports/figures/sus_scores.png",
            "tests/reports/figures/therapeutic_scores.png"
        ],
        "raw_data": "tests/reports/user_testing_data.csv"
    }
    
    # Save dataframe for further analysis
    df.to_csv("tests/reports/user_testing_data.csv", index=False)
    
    # Save report
    with open(f"tests/reports/user_testing_report_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return report