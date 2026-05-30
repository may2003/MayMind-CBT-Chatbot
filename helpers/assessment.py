import streamlit as st
from helpers.safety import assess_phq9_risk, show_crisis_resources

def display_phq9_gad7_assessment():
    """Display PHQ-9 and GAD-7 assessment questionnaires."""
    st.header(f"Wellbeing Check - Hi {st.session_state.user_name}!")
    st.markdown("Please complete this short questionnaire before we begin.")

    # Assessment questions
    phq9_questions = [
        "Little interest or pleasure in doing things?",
        "Feeling down, depressed, or hopeless?",
        "Trouble falling or staying asleep, or sleeping too much?",
        "Feeling tired or having little energy?",
        "Poor appetite or overeating?",
        "Feeling bad about yourself, or that you're a failure?",
        "Trouble concentrating on things?",
        "Moving or speaking slowly, or being fidgety/restless?",
        "Thoughts that you'd be better off dead or hurting yourself?"
    ]

    gad7_questions = [
        "Feeling nervous, anxious or on edge?",
        "Not being able to stop or control worrying?",
        "Worrying too much about different things?",
        "Trouble relaxing?",
        "Being so restless it's hard to sit still?",
        "Becoming easily annoyed or irritable?",
        "Feeling afraid something awful might happen?"
    ]

    # Score options
    options = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
    scores = {option: i for i, option in enumerate(options)}

    # Display questionnaires in tabs
    tab1, tab2 = st.tabs(["Depression Assessment (PHQ-9)", "Anxiety Assessment (GAD-7)"])

    with tab1:
        phq9_total = 0
        phq9_responses = []

        for i, question in enumerate(phq9_questions):
            response = st.radio(question, options, key=f"phq9_{i}")
            score = scores[response]
            phq9_total += score
            phq9_responses.append(score)

    with tab2:
        gad7_total = 0
        gad7_responses = []

        for i, question in enumerate(gad7_questions):
            response = st.radio(question, options, key=f"gad7_{i}")
            score = scores[response]
            gad7_total += score
            gad7_responses.append(score)

    # Submit scores
    if st.button("Submit Assessment"):
        # Check for crisis risk
        if assess_phq9_risk(phq9_responses):
            show_crisis_resources()
            st.warning("Based on your response about thoughts of self-harm, I strongly recommend speaking with a healthcare professional.")

        st.session_state.phq9_total = phq9_total
        st.session_state.gad7_total = gad7_total

        # Create first message from May based on assessment results
        welcome_msg = f"Hi {st.session_state.user_name}, thank you for completing the assessment. "

        # Personalize based on scores
        if phq9_total >= 15 or gad7_total >= 15:
            welcome_msg += "I can see you've been going through a difficult time lately. Thank you for your honesty - it takes courage to acknowledge these feelings. I'm here to listen and work with you on some strategies that might help."
        elif phq9_total >= 10 or gad7_total >= 10:
            welcome_msg += "It seems like you've been experiencing some challenges lately. I appreciate your openness. Let's explore what's been going on for you and discuss some approaches that might help."
        elif phq9_total >= 5 or gad7_total >= 5:
            welcome_msg += "You seem to be experiencing some mild difficulties. I'm glad you've reached out to talk. Let's explore what's on your mind and think together about what might help."
        else:
            welcome_msg += "Based on your responses, it seems like you're doing fairly well overall, though I'm sure you have specific things you'd like to discuss. What brings you here today?"

        welcome_msg += "\n\nWhat's been on your mind recently that you'd like to talk about?"

        # Add welcome message to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})

        st.success(f"Assessment complete: PHQ-9: {phq9_total}/27, GAD-7: {gad7_total}/21")
        st.rerun()