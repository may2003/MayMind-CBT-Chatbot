import streamlit as st
from datetime import datetime
from helpers.utils import get_image_base64

def display_chat_header():
    """Display stylized chat header with mood indicator."""
    # Get current mood if available
    current_mood = None
    mood_emoji = "😊"
    mood_trend = ""

    if "mood_history" in st.session_state and st.session_state.mood_history:
        current_mood = st.session_state.mood_history[-1]["score"]

        # Set emoji based on mood score
        if current_mood <= 3:
            mood_emoji = "😔"
        elif current_mood <= 5:
            mood_emoji = "😐"
        elif current_mood <= 7:
            mood_emoji = "🙂"
        else:
            mood_emoji = "😊"

        # Show trend if we have more than one mood entry
        if len(st.session_state.mood_history) > 1:
            prev_mood = st.session_state.mood_history[-2]["score"]
            if current_mood > prev_mood:
                mood_trend = "↗️"  # Rising trend
            elif current_mood < prev_mood:
                mood_trend = "↘️"  # Falling trend
            else:
                mood_trend = "→"  # Stable trend

    # Create header container
    image_base64 = get_image_base64("assets/robot-icon.PNG")
    st.markdown(f"""
        <div style="display: flex; align-items: center; background-color: #F8E1EA; 
                    padding: 10px; border-radius: 10px; margin-bottom: 15px;">
            <div style="width: 40px; height: 40px; overflow: hidden; border-radius: 50%; margin-right: 12px;">
                <img src="data:image/png;base64,{image_base64}" width="40" height="40">
            </div>
            <div style="flex-grow: 1;">
                <div style="font-weight: 600; color: #D97D9F;">May</div>
                <div style="font-size: 0.9rem; color: #888;">CBT Assistant</div>
            </div>
            {f'<div style="text-align: right; font-size: 1.2rem;">{mood_emoji} {mood_trend}</div>' if current_mood else ""}
        </div>
    """, unsafe_allow_html=True)

def display_welcome_screen():
    """Display the welcome screen with logo and introduction."""
    # Display logo and title with improved layout and alignment
    col1, col2 = st.columns([1, 2])
    
    with col1:
        try:
            # Make the robot icon bigger and adjust vertical alignment
            robot_icon_base64 = get_image_base64("assets/robot-icon.PNG")
            if robot_icon_base64:
                st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center; height: 100%; padding-top: 20px;">
                        <img src="data:image/png;base64,{robot_icon_base64}" width="180" style="filter: drop-shadow(2px 2px 5px rgba(0,0,0,0.2));">
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.image("assets/robot-icon.PNG", width=180)
        except:
            st.info("Robot icon not found")
            
    with col2:
        try:
            app_name_base64 = get_image_base64("assets/app-name.png")
            if app_name_base64:
                st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center; height: 100%; padding-top: 30px;">
                        <img src="data:image/png;base64,{app_name_base64}" style="max-width: 100%; filter: drop-shadow(1px 1px 3px rgba(0,0,0,0.1));">
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.image("assets/app-name.png")
        except:
            st.title("MayMind CBT Assistant")

    # Add some space after the header images
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
    st.markdown("""
    ### Hi there! I'm May

    I'm here to help you explore your thoughts and emotions using proven Cognitive Behavioural Therapy techniques.
    Before we begin, I'd love to get your name, and we'll start with a short wellbeing check.
    """)

    with st.form("intro_form"):
        name = st.text_input("What is your name?")
        consent = st.checkbox("I understand this is not a substitute for professional therapy and agree to continue.")
        start = st.form_submit_button("Continue")

        if start:
            if not name:
                st.warning("Please enter your name to begin.")
            elif not consent:
                st.warning("Please provide consent to continue.")
            else:
                st.session_state.user_name = name
                st.session_state.session_started = True
                st.rerun()

def display_mood_tracker():
    """Display the mood tracker widget in an expander."""
    with st.expander("Mood Tracker"):
        col1, col2 = st.columns([3, 1])

        with col1:
            today_mood = st.slider("How are you feeling today?", 1, 10, 5, 
                                  help="1 = Very low, 10 = Excellent")

        with col2:
            if st.button("Save Mood", use_container_width=True):
                if "mood_history" not in st.session_state:
                    st.session_state.mood_history = []

                st.session_state.mood_history.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "score": today_mood
                })
                st.success("Mood saved!")
                st.rerun()

        # Show mood history if available
        if "mood_history" in st.session_state and st.session_state.mood_history:
            # Show last 5 mood entries
            mood_history = st.session_state.mood_history[-5:]

            st.write("Recent mood entries:")
            for i, mood in enumerate(reversed(mood_history)):
                st.write(f"• {mood['timestamp']}: {mood['score']}/10")