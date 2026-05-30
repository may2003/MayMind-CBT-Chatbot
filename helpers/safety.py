import streamlit as st

def check_crisis_risk(message):
    """Check for crisis keywords in user messages."""
    crisis_keywords = {
        "suicide", "kill myself", "end it all", "better off dead",
        "hurting myself", "self harm", "cut myself", "overdose",
        "can't go on", "want to die", "no reason to live"
    }

    message_lower = message.lower()

    if any(word in message_lower for word in crisis_keywords):
        show_crisis_resources()
        return True
    return False

def show_crisis_resources():
    """Display crisis resources and support information."""
    st.error("🚨 Your safety is important. Please contact these 24/7 services:")
    st.markdown("""
    ### Immediate Support Available
    - **Samaritans**: 116 123 (Free, 24/7)
    - **Crisis Text Line**: Text SHOUT to 85258
    - **Emergency Services**: 999
    - **NHS Direct**: 111

    These services are here to help, and you deserve support.
    """)

def assess_phq9_risk(responses):
    """Assess suicide risk based on PHQ-9 responses."""
    # Check question 9 (suicidal thoughts)
    if responses and len(responses) >= 9:
        suicide_question_response = responses[8]
        if suicide_question_response >= 1:  # Any non-zero response indicates risk
            return True
    return False