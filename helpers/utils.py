import streamlit as st
import re
from datetime import datetime
import base64
import os

def init_session_state():
    """Initialize session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "phq9_total" not in st.session_state:
        st.session_state.phq9_total = 0
    if "gad7_total" not in st.session_state:
        st.session_state.gad7_total = 0
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "session_started" not in st.session_state:
        st.session_state.session_started = False
    if "mood_history" not in st.session_state:
        st.session_state.mood_history = []
    if "thought_records" not in st.session_state:
        st.session_state.thought_records = []
    if "activity_schedule" not in st.session_state:
        st.session_state.activity_schedule = []
    if "session_summary_given" not in st.session_state:
        st.session_state.session_summary_given = False

def remove_emojis(text):
    """Remove emoji characters from text for PDF compatibility."""
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F700-\U0001F77F"  # alchemical symbols
                           u"\U0001F780-\U0001F7FF"  # Geometric Shapes
                           u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                           u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                           u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                           u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                           u"\U00002702-\U000027B0"  # Dingbats
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def clean_text(text):
    """Remove markdown formatting and emojis from text."""
    # Remove markdown formatting
    text = re.sub(r'#+\s+', '', text)  # Remove headers
    text = re.sub(r'\*\*|\*', '', text)  # Remove bold/italic markers
    # Remove emojis
    return remove_emojis(text)

def get_image_base64(image_path):
    """Get base64 encoded image with error handling."""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""
    except Exception:
        return ""

def format_timestamp(timestamp=None):
    """Format timestamp in a human-readable format."""
    if timestamp is None:
        timestamp = datetime.now()
    elif isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return timestamp

    return timestamp.strftime("%B %d, %Y at %I:%M %p")