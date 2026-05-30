# this is the main file for the MayMind CBT Assistant app that ties everything together.
# Standard library imports
import os
from pathlib import Path 
import streamlit as st #UI library
import openai
from dotenv import load_dotenv

# Local application imports
from helpers.utils import init_session_state
from ai.therapist import get_ai_response, generate_session_summary, create_therapist_prompt
from helpers.safety import check_crisis_risk
from helpers.assessment import display_phq9_gad7_assessment
from helpers.ui import display_chat_header, display_welcome_screen, display_mood_tracker
from tools.thought_journal import thought_journal
from tools.activity_scheduler import activity_scheduler
from tools.breathing import breathing_exercise
from export.pdf_generator import generate_session_report_pdf, download_pdf
from export.transcript import generate_chat_transcript_pdf

# Load environment variables and set API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up page configuration
st.set_page_config(
    page_title="MayMind CBT Assistant",
    page_icon="assets/robot-icon.PNG", # Robot icon for the app 
    layout="wide"
)

# Initialize session state
if "session_state_initialized" not in st.session_state:
    init_session_state()
    st.session_state.session_state_initialized = True

# load css file for styling (pink theme for MayMind)
css_path = "styles/maymind.css"
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def display_main_interface():
    """Display the main application interface with tabs"""
    st.title(f"Welcome to your CBT session, {st.session_state.user_name}") #greet user by their name 
    
    # Show anxiety and depression assessment results 
    if st.session_state.phq9_total > 0 or st.session_state.gad7_total > 0:
        with st.expander("💡 Your Assessment Results", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                phq9_severity = get_severity_label("phq9", st.session_state.phq9_total)
                st.metric("Depression (PHQ-9)", f"{st.session_state.phq9_total}/27", help="Lower scores are better")
                st.caption(f"Severity: {phq9_severity}")
                
            with col2:
                gad7_severity = get_severity_label("gad7", st.session_state.gad7_total)
                st.metric("Anxiety (GAD-7)", f"{st.session_state.gad7_total}/21", help="Lower scores are better")
                st.caption(f"Severity: {gad7_severity}")

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Chat with May", "CBT Tools", "Progress", "Export Session"])

    # Tab 1: Chat Interface (therapist chat)
    with tab1:
        display_chat_interface()

    # Tab 2: CBT Tools 
    with tab2:
        display_tools()
    
    # Tab 3: Progress Tracking
    with tab3:
        display_progress_tracking()

    # Tab 4: Export pdf Options for users 
    with tab4:
        display_export_options()

def display_chat_interface():
    """Display the chat interface"""
    # Chat title 
    display_chat_header()

    # Mood tracker
    display_mood_tracker()

    # Display chat messages
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            try:
                st.chat_message("assistant", avatar="assets/robot-icon.PNG").write(msg["content"]) #set avatar to our robot icon 
            except Exception:
                st.chat_message("assistant").write(msg["content"]) #incase of error

    # Chat input
    user_input = st.chat_input("what's on your mind?....") #user input space
    if user_input:
        # Check for crisis risk (suicidal inputs) if detected stop session
        if check_crisis_risk(user_input):
            st.stop()

        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get AI response
        ai_response = get_ai_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        st.rerun()

    # End session button 
    if st.button("End Session", use_container_width=True):
        if not st.session_state.session_summary_given: # check for summary
            summary = generate_session_summary()
            st.session_state.chat_history.append({"role": "assistant", "content": summary}) # add to chat history 
            st.session_state.session_summary_given = True
            st.rerun()

def display_tools(): #define the tools tab with 3 cbt tools 
    """Display the CBT tools interface"""
    tool_tabs = st.tabs(["Thought Journal", "📅 Activity Planner", "Breathing Exercise"])

    with tool_tabs[0]:
        thought_journal()

    with tool_tabs[1]:
        activity_scheduler()

    with tool_tabs[2]:
        breathing_exercise()

def display_progress_tracking():  # to track user progress, visualise data 
    """Display progress tracking and visualizations"""
    st.header("Your Progress")
    
    # Check if we have any data to show
    has_mood_data = "mood_history" in st.session_state and len(st.session_state.mood_history) > 0
    has_thought_records = "thought_records" in st.session_state and len(st.session_state.thought_records) > 0
    has_breathing_data = "breathing_exercises" in st.session_state and len(st.session_state.breathing_exercises) > 0
    
    if not has_mood_data and not has_thought_records and not has_breathing_data:
        st.info("Your progress data will appear here as you use the app. Try tracking your mood in the chat tab or using the CBT tools.")
        return
    
    # Mood tracking visualization
    if has_mood_data:
        display_mood_visualization()
    
    # Activity completion stats
    if "activity_schedule" in st.session_state and st.session_state.activity_schedule:
        display_activity_stats()
    
    # Thought journal insights
    if has_thought_records:
        display_thought_journal_insights()
    
    # Breathing exercise stats
    if has_breathing_data:
        display_breathing_exercise_stats()

def display_mood_visualization():
    """Display mood tracking visualization and statistics"""
    st.subheader("Mood Tracking")
    
    # Import visualization libraries only where needed
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    
    # Create dataframe from mood history
    mood_data = pd.DataFrame([
        {"timestamp": m["timestamp"], "score": m["score"]} for m in st.session_state.mood_history
    ])
    mood_data["timestamp"] = pd.to_datetime(mood_data["timestamp"])
    mood_data.set_index("timestamp", inplace=True)
    
    # Plot mood over time
    fig, ax = plt.subplots(figsize=(10, 4))
    mood_data.plot(ax=ax, marker='o', linestyle='-', color='purple')
    ax.set_ylim(0, 10)
    ax.set_ylabel("Mood (0-10)")
    ax.set_title("Your Mood Over Time")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    st.pyplot(fig)
    
    # Calculate statistics only if we have enough data 
    if len(mood_data) > 1:
        avg_mood = mood_data["score"].mean()
        # Convert numpy types to Python native types for better compatibility
        mood_trend_value = float(mood_data["score"].iloc[-1] - mood_data["score"].iloc[0])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Mood", f"{avg_mood:.1f}/10")
        with col2:
            st.metric("Overall Trend", f"{mood_trend_value:+.1f}", delta=float(mood_trend_value))

def display_activity_stats():
    """Display activity completion statistics"""
    st.subheader("Activities")
    
    activities = st.session_state.activity_schedule
    total = len(activities)
    completed = sum(1 for a in activities if a.get("completed", False))
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    st.progress(completion_rate / 100)
    st.write(f"You've completed {completed} out of {total} planned activities ({completion_rate:.1f}%)")

def display_thought_journal_insights():
    """Display simplified insights from thought journal entries"""
    st.subheader("Thought Journal Insights")
    
    records = st.session_state.thought_records
    total_records = len(records)
    
    st.write(f"You've created {total_records} thought {('record' if total_records == 1 else 'records')}")
    
    # Only show emotional improvement stats if available
    improvements = []
    for record in records:
        if "emotion_intensity" in record and "new_emotion_intensity" in record:
            improvement = record["emotion_intensity"] - record["new_emotion_intensity"]
            if improvement > 0:
                improvements.append(improvement)
    
    if improvements:
        positive_records = len(improvements)
        if positive_records > 0:
            avg_improvement = sum(improvements) / positive_records
            st.write(f"{positive_records} {('entry' if positive_records == 1 else 'entries')} showed emotional improvement with an average decrease of {avg_improvement:.1f}% in emotional intensity")

def display_breathing_exercise_stats():
    """Display statistics on breathing exercises"""
    st.subheader("Breathing Exercises")
    st.write(f"You've completed {len(st.session_state.breathing_exercises)} breathing exercises")
    
    # Get feeling change data
    feeling_changes = []
    for exercise in st.session_state.breathing_exercises:
        if "before_feeling" in exercise and "after_feeling" in exercise:
            feelings = ["Very tense", "Tense", "Neutral", "Calm", "Very calm"]
            before_idx = feelings.index(exercise["before_feeling"])
            after_idx = feelings.index(exercise["after_feeling"])
            change = after_idx - before_idx
            feeling_changes.append(change)
    
    if feeling_changes:
        positive_changes = sum(1 for c in feeling_changes if c > 0)
        pct_positive = (positive_changes / len(feeling_changes)) * 100
        st.write(f"{positive_changes} exercises ({pct_positive:.1f}%) resulted in improved feelings")

def get_severity_label(assessment_type, score):
    """Return severity label based on assessment score"""
    if assessment_type == "phq9":
        if score <= 4:
            return "Minimal"
        elif score <= 9:
            return "Mild"
        elif score <= 14:
            return "Moderate"
        elif score <= 19:
            return "Moderately Severe"
        else:
            return "Severe"
    elif assessment_type == "gad7":
        if score <= 4:
            return "Minimal"
        elif score <= 9:
            return "Mild"
        elif score <= 14:
            return "Moderate"
        else:
            return "Severe"
    return "Unknown"

def display_export_options():
    """Display the export options"""
    st.header("Export Session")

    # Only allow export if there's been conversation
    if len(st.session_state.chat_history) > 1:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Full Session Report")
            st.write("Includes assessment results, chat transcript, journal entries, and activities")
            if st.button("Generate Full Report", use_container_width=True):
                pdf = generate_session_report_pdf(st.session_state.user_name)
                download_pdf(pdf, "MayMind_Full_Report")

        with col2:
            st.subheader("Chat Transcript Only")
            st.write("Includes only your conversation with May")
            if st.button("Generate Chat Transcript", use_container_width=True):
                pdf = generate_chat_transcript_pdf(st.session_state.user_name)
                download_pdf(pdf, "MayMind_Chat")
    else:
        st.info("Have a conversation with May first before exporting your session.")

    # Reset session option
    st.divider()
    st.subheader("Start New Session")
    st.warning("This will clear your current chat history. Your journal entries and activities will be saved.")
    if st.button("Start New Session", key="new_session"):
        # Reset key session variables but keep assessment results and tools data
        st.session_state.chat_history = []
        st.session_state.session_summary_given = False
        st.rerun()

def main():
    """Main application logic"""
    if not st.session_state.session_started:
        display_welcome_screen()
    elif st.session_state.phq9_total == 0 and st.session_state.gad7_total == 0:
        display_phq9_gad7_assessment()
    else:
        display_main_interface()

if __name__ == "__main__":
    main()