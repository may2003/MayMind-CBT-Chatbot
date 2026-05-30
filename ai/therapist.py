import streamlit as st
import openai
from datetime import datetime

def get_ai_response(user_input, save_to_history=False):
    """
    Get AI response using OpenAI API with enhanced CBT therapeutic approach.
    Uses reflection, validation, and natural therapeutic guidance.

    Parameters:
    - user_input: The user's message
    - save_to_history: If True, save response directly to chat history

    Returns:
    - AI response text
    """
    # Get recent chat context (last 8 messages for better conversation flow)
    recent_messages = st.session_state.chat_history[-8:] if len(st.session_state.chat_history) > 0 else []
    
    # Format messages for OpenAI API
    formatted_messages = [{"role": "system", "content": create_therapist_prompt()}]
    
    # Add recent conversation messages in the proper format
    for msg in recent_messages:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current user message if not already in recent messages
    if not recent_messages or recent_messages[-1]["role"] != "user" or recent_messages[-1]["content"] != user_input:
        formatted_messages.append({"role": "user", "content": user_input})

    try:
        # Updated OpenAI API call for newer client versions (v1.0.0+)
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=formatted_messages,
            max_tokens=650,
            temperature=0.7
        )
        response_text = response.choices[0].message.content

        # Optionally save the response directly to chat history
        if save_to_history:
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})

        return response_text
    except Exception as e:
        error_response = f"I'm finding it hard to respond right now. Could we try approaching this a bit differently? (Error: {str(e)})"

        # Save error message to history if requested
        if save_to_history:
            st.session_state.chat_history.append({"role": "assistant", "content": error_response})

        return error_response

def create_therapist_prompt():
    # Get mood context
    mood_context = "No mood data available"
    if hasattr(st.session_state, 'mood_history') and st.session_state.mood_history:
        try:
            current_mood = st.session_state.mood_history[-1]["score"]
            mood_context = f"Current reported mood: {current_mood}/10"
            
            if len(st.session_state.mood_history) > 1:
                previous_mood = st.session_state.mood_history[-2]["score"]
                if current_mood > previous_mood:
                    mood_context += f" (improving from {previous_mood})"
                elif current_mood < previous_mood:
                    mood_context += f" (declining from {previous_mood})"
                else:
                    mood_context += " (stable)"
        except (IndexError, KeyError):
            pass
    
    # Get thought context safely
    thought_context = "No thought records available"
    try:
        if hasattr(st.session_state, 'thought_records') and st.session_state.thought_records:
            recent_thought = st.session_state.thought_records[-1]
            if "thought" in recent_thought:
                thought_context = f"Recent thoughts from journal: {recent_thought['thought']}"
    except (IndexError, KeyError):
        pass
    
    # Get user info safely
    user_name = getattr(st.session_state, 'user_name', 'User')
    phq9_total = getattr(st.session_state, 'phq9_total', 0)
    gad7_total = getattr(st.session_state, 'gad7_total', 0)
    
    # Create the prompt with all context
    prompt = f"""
    IMPORTANT DISCLAIMER: I am an AI assistant trained to provide CBT-based support, not a licensed therapist. Please seek professional help for clinical mental health concerns.

    You are May, a compassionate and skilled CBT therapist trained in the UK NHS/IAPT framework. 
    Your responses should feel genuinely therapeutic, warm, and personalized.
    
    LANGUAGE REQUIREMENTS:
    - Only respond in English
    - If user writes in another language, politely ask them to use English
    - Keep your language clear, accessible, and free of complex jargon
    
    THERAPEUTIC APPROACH:
    1. Begin responses by reflecting the client's emotions or experiences with genuine empathy
    6. Use evidence-based CBT methods to identify and challenge negative thought patterns
    7. Encourage behavioral activation when appropriate for the client's situation
    8. Collaboratively set realistic and measurable goals with the client
    9. Help clients identify connections between thoughts, feelings, and behaviors
    10. Provide psychoeducation about CBT principles when appropriate

    COMMUNICATION STRUCTURE (flow naturally between these elements):
    1. Emotional validation and reflection
    2. Gentle reframing or CBT insight
    3. Thoughtful follow-up question to deepen reflection
    4. Suggesting practical techniques or homework when appropriate

    AVOID:
    - Formulaic language like "I'm here to help" or "Let me guide you through"
    - Explicitly mentioning "CBT tools" or techniques by name
    - Generic responses that could apply to anyone
    - Switching topics abruptly without addressing emotional content
    - Giving advice without exploring the client's perspective first

    CLIENT DETAILS:
    - Name: {user_name}
    - PHQ-9 (Depression): {phq9_total}/27 
    - GAD-7 (Anxiety): {gad7_total}/21
    - {mood_context}
    - {thought_context}

    Respond with warm, insightful therapeutic dialogue that feels like a real therapist-client conversation.
    """
    return prompt

def generate_session_summary(for_pdf=False):
    """Generate enhanced therapeutic end-of-session summary."""
    # Extract key information safely
    key_themes = set()

    # Setup safe defaults
    chat_history = []
    mood_text = "Mood not recorded"
    mood_trend = ""
    upcoming_activities = []

    # Safely access chat history
    if hasattr(st.session_state, 'chat_history'):
        chat_history = getattr(st.session_state, 'chat_history', [])
        
        # Analyze conversation for themes
        for msg in chat_history:
            content = msg["content"].lower()
            
            # Extract common themes
            for theme in ["anxiety", "depression", "relationships", "work", "health", 
                         "family", "sleep", "stress", "self-esteem"]:
                if theme in content:
                    key_themes.add(theme)

    # Get current mood and trend safely
    if hasattr(st.session_state, 'mood_history') and st.session_state.mood_history:
        try:
            moods = [m["score"] for m in st.session_state.mood_history]
            current_mood = moods[-1]
            mood_text = f"Current mood: {current_mood}/10"

            if len(moods) > 1:
                first_mood = moods[0]
                if current_mood > first_mood:
                    mood_trend = f"Mood has improved from {first_mood} to {current_mood}"
                elif current_mood < first_mood:
                    mood_trend = f"Mood has decreased from {first_mood} to {current_mood}"
                else:
                    mood_trend = f"Mood has remained stable at {current_mood}"
        except (IndexError, KeyError):
            pass

    # Get scheduled activities safely
    if hasattr(st.session_state, 'activity_schedule') and st.session_state.activity_schedule:
        try:
            upcoming_activities = [a["name"] for a in st.session_state.activity_schedule if not a["completed"]]
        except (KeyError, TypeError):
            pass

    # Get user name safely
    user_name = getattr(st.session_state, 'user_name', 'User')

    # Choose proper formatting based on destination
    if for_pdf:
        # PDF-safe version
        summary = f"""Session Summary

Thank you for sharing today, {user_name}. Let's review what we covered:

Progress
* {mood_text}
{f"* {mood_trend}" if mood_trend else ""}

Key Themes Discussed
{', '.join(key_themes) if key_themes else 'We had a general therapeutic conversation today.'}

Next Steps
* {'We planned these activities: ' + ', '.join(upcoming_activities) if upcoming_activities else 'Consider scheduling activities that could improve your mood.'}
* Continue practicing the skills we discussed today.
* Notice your thought patterns and how they affect your mood.

Remember, small consistent steps lead to meaningful change. Your engagement today shows your commitment to your wellbeing.
"""
    else:
        # Regular version with emojis for display
        summary = f"""### Session Summary

Thank you for sharing today, {user_name}. Here's a recap of our session:

#### Progress
* {mood_text}
{f"* {mood_trend}" if mood_trend else ""}

#### Key Themes
{', '.join(key_themes) if key_themes else 'We had a general therapeutic conversation today.'}

#### Next Steps
* {'We planned these activities: ' + ', '.join(upcoming_activities) if upcoming_activities else 'Consider scheduling activities that could improve your mood.'}
* Continue practicing the skills we discussed today.
* Notice your thought patterns and how they affect your mood.

Remember, small consistent steps lead to meaningful change. Your engagement today shows your commitment to your wellbeing.

Would you like to download a copy of our session?
"""

    return summary