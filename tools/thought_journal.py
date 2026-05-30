import streamlit as st
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def thought_journal():
    """Interactive thought record tool for identifying and challenging negative thoughts."""
    st.markdown("""
    ### 📝 Thought Journal

    Use this tool to record and challenge unhelpful thoughts. This is a key CBT skill that helps you:
    - Notice patterns in your thinking
    - Identify how thoughts affect your emotions
    - Develop more balanced perspectives
    """)

    # Create tabs for adding new entries and viewing past entries
    tab1, tab2 = st.tabs(["New Entry", "Past Entries"])

    # Tab 1: Add new thought record entry
    with tab1:
        with st.form("thought_record_form"):
            st.subheader("New Thought Record")

            # Situation
            situation = st.text_area("Situation: What was happening? Where were you? Who were you with?", 
                                   placeholder="e.g., Meeting with my boss about project deadline")

            # Emotions - now with common emotion suggestions
            col1, col2 = st.columns(2)
            with col1:
                # Suggested emotions with autocomplete
                common_emotions = [
                    "Anxiety", "Sadness", "Anger", "Guilt", "Shame", "Fear", 
                    "Frustration", "Embarrassment", "Helplessness", "Loneliness", 
                    "Irritation", "Overwhelm", "Disappointment", "Worry"
                ]
                emotion_input = st.text_input("Emotion(s)", 
                                          placeholder="Type or select emotion(s)")
                
                emotion_selection = st.multiselect(
                    "Or select from common emotions:",
                    options=common_emotions,
                    default=[]
                )
                
                # Combine manual input with selections
                emotion = emotion_input
                if emotion_selection:
                    if emotion:
                        emotion += ", " + ", ".join(emotion_selection)
                    else:
                        emotion = ", ".join(emotion_selection)
                
            with col2:
                emotion_intensity = st.slider("Intensity (0-100%)", 0, 100, 50)

            # Automatic thoughts
            negative_thought = st.text_area("Automatic Thought: What went through your mind?", 
                                         placeholder="e.g., My boss thinks I'm incompetent")

            # Cognitive distortions with tooltips
            distortion_descriptions = {
                "All-or-Nothing Thinking": "Seeing things in black and white categories",
                "Overgeneralization": "Viewing a negative event as a never-ending pattern",
                "Mental Filter": "Focusing on a negative detail while ignoring positives",
                "Disqualifying the Positive": "Rejecting positive experiences",
                "Jumping to Conclusions": "Making negative interpretations without facts",
                "Magnification or Minimization": "Exaggerating negatives or minimizing positives",
                "Emotional Reasoning": "Assuming feelings reflect reality",
                "Should Statements": "Criticizing with 'should' and 'must' statements",
                "Labeling": "Attaching a negative label to yourself or others",
                "Personalization": "Blaming yourself for events not entirely under your control",
                "Catastrophizing": "Expecting disaster; 'what if' thinking",
                "Mind Reading": "Assuming you know what others are thinking"
            }
            
            st.write("Thinking Patterns (select all that apply):")
            col1, col2 = st.columns(2)
            
            # Create checkboxes with tooltips in two columns
            selected_distortions = []
            distortion_keys = list(distortion_descriptions.keys())
            mid_point = len(distortion_keys) // 2
            
            with col1:
                for pattern in distortion_keys[:mid_point]:
                    if st.checkbox(pattern, help=distortion_descriptions[pattern]):
                        selected_distortions.append(pattern)
                        
            with col2:
                for pattern in distortion_keys[mid_point:]:
                    if st.checkbox(pattern, help=distortion_descriptions[pattern]):
                        selected_distortions.append(pattern)

            # Evidence sections
            col1, col2 = st.columns(2)
            with col1:
                evidence_for = st.text_area("Evidence Supporting the Thought", 
                                         placeholder="What facts/evidence support this thought?")
            with col2:
                evidence_against = st.text_area("Evidence Against the Thought", 
                                             placeholder="What facts/evidence contradict this thought?")

            # Alternative thought
            balanced_thought = st.text_area("Alternative, More Balanced Thought", 
                                         placeholder="e.g., Having one deadline issue doesn't make me incompetent")

            # Re-rate emotion
            new_emotion_intensity = st.slider("Emotion Intensity After (0-100%)", 0, 100, 30)
            
            # Additional reflection section
            st.write("**Reflection (Optional)**")
            reflection = st.text_area(
                "What did you learn from this exercise?",
                placeholder="e.g., I noticed that I tend to catastrophize small mistakes at work..."
            )

            # Submit button
            submitted = st.form_submit_button("Save Entry")

        if submitted:
            if not situation or not emotion or not negative_thought:
                st.error("Please fill in at least the situation, emotion, and thought fields.")
            else:
                # Initialize thought records list if it doesn't exist
                if "thought_records" not in st.session_state:
                    st.session_state.thought_records = []

                # Add the entry to thought records
                st.session_state.thought_records.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M"),
                    "situation": situation,
                    "emotion": emotion,
                    "emotion_intensity": emotion_intensity,
                    "thought": negative_thought,
                    "distortions": selected_distortions,
                    "evidence_for": evidence_for,
                    "evidence_against": evidence_against,
                    "balanced_thought": balanced_thought,
                    "new_emotion_intensity": new_emotion_intensity,
                    "reflection": reflection
                })

                st.success("Thought record saved!")
                improvement = emotion_intensity - new_emotion_intensity
                if improvement > 0:
                    st.info(f"Great job! Your emotional intensity decreased by {improvement} points.")
                    
                # Display a relevant tip based on the cognitive distortions
                display_cognitive_distortion_tip(selected_distortions)

    # Tab 2: View past thought records
    with tab2:
        if "thought_records" in st.session_state and st.session_state.thought_records:
            st.subheader("Your Thought Records")
            
            # Sort by timestamp, newest first
            sorted_records = sorted(
                st.session_state.thought_records,
                key=lambda x: x["timestamp"],
                reverse=True
            )

            # Display each record in an expander
            for i, record in enumerate(sorted_records):
                # Create summary for expander header
                header_date = record["date"]
                header_thought = record.get("thought", "")  # Use get() to avoid KeyError
                if not header_thought and "negative_thought" in record:
                    header_thought = record["negative_thought"]  # For backward compatibility
                
                if len(header_thought) > 40:
                    header_thought = header_thought[:40] + "..."

                with st.expander(f"{header_date}: {header_thought}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Situation:**  \n{record['situation']}")
                        st.markdown(f"**Emotion:**  \n{record['emotion']} ({record['emotion_intensity']}%)")
                        st.markdown(f"**Thought:**  \n{header_thought}")

                    with col2:
                        st.markdown(f"**Alternative Thought:**  \n{record['balanced_thought']}")
                        st.markdown(f"**New Emotion Intensity:**  \n{record['new_emotion_intensity']}%")

                        improvement = record['emotion_intensity'] - record['new_emotion_intensity']
                        if improvement > 0:
                            st.markdown(f"**Improvement:**  \n{improvement}% decrease")

                    # Thinking patterns identified
                    if record.get('distortions'):
                        st.markdown(f"**Thinking Patterns Identified:**  \n{', '.join(record['distortions'])}")

                    # Evidence sections (if filled)
                    if record.get('evidence_for') or record.get('evidence_against'):
                        st.markdown("**Evidence:**")
                        ev_col1, ev_col2 = st.columns(2)
                        with ev_col1:
                            st.markdown(f"Supporting:  \n{record.get('evidence_for', '')}")
                        with ev_col2:
                            st.markdown(f"Contradicting:  \n{record.get('evidence_against', '')}")
                                
                    # Reflection (if filled)
                    if record.get('reflection'):
                        st.markdown(f"**Reflection:**  \n{record['reflection']}")

                    # Delete button
                    if st.button("Delete Entry", key=f"delete_thought_{i}"):
                        st.session_state.thought_records.remove(record)
                        st.success("Entry deleted")
                        st.rerun()
        else:
            st.info("No thought records yet. Add your first entry in the 'New Entry' tab.")

def display_cognitive_distortion_tip(distortions):
    """Display a helpful tip for one of the cognitive distortions identified."""
    if not distortions:
        return
    
    # Choose a random distortion from those selected
    import random
    distortion = random.choice(distortions)
    
    # Display the tip
    st.write("**Helpful Tip:**")
    st.info(get_distortion_tips(distortion))

def get_distortion_tips(distortion):
    """Return helpful tips for specific cognitive distortions."""
    tips = {
        "All-or-Nothing Thinking": "Try looking for the gray areas. Instead of seeing things as complete success or total failure, consider: Where on a 0-100 scale would this situation actually fall?",
        
        "Overgeneralization": "Notice words like 'always' or 'never' in your thoughts. Challenge them by finding exceptions: 'When was a time this wasn't true?'",
        
        "Mental Filter": "Deliberately look for positive elements you might be filtering out. What went well? What are you discounting?",
        
        "Disqualifying the Positive": "Practice accepting compliments and acknowledging successes without dismissing them. Keep a 'success journal' of things you've done well.",
        
        "Jumping to Conclusions": "Test your predictions by asking: 'What evidence do I actually have for this conclusion? What are alternative explanations?'",
        
        "Magnification or Minimization": "Use a scale from 0-10 to rate how significant this situation really is. Will this matter in a week? A month? A year?",
        
        "Emotional Reasoning": "Remind yourself: 'Just because I feel this way doesn't mean it's true.' Feelings aren't facts.",
        
        "Should Statements": "Replace rigid words like 'should,' 'must,' and 'have to' with more flexible language like 'prefer,' 'would like,' or 'it would be helpful if.'",
        
        "Labeling": "Separate behaviors from identity. Instead of 'I'm a failure,' try 'I didn't succeed at this specific task.'",
        
        "Personalization": "Consider all the factors that might contribute to a situation, not just your actions. What else could explain what happened?",
        
        "Catastrophizing": "Ask yourself: 'What's the most likely outcome? What's the worst that could happen? How would I cope if it did?'",
        
        "Mind Reading": "Rather than assuming you know what others think, practice checking it out: 'I notice you seemed quiet in the meeting. What were you thinking?'"
    }
    
    return tips.get(distortion, "Practice noticing and questioning your thoughts regularly.")

def get_thought_records_for_pdf():
    """Return formatted thought records for PDF export."""
    if "thought_records" not in st.session_state or not st.session_state.thought_records:
        return "No thought records created."

    # Sort by timestamp
    sorted_records = sorted(
        st.session_state.thought_records,
        key=lambda x: x["timestamp"]
    )

    # Format as text
    records_text = "Thought Journal Entries:\n\n"
    for record in sorted_records:
        records_text += f"Date: {record['date']}\n"
        records_text += f"Situation: {record['situation']}\n"
        records_text += f"Emotion: {record['emotion']} ({record['emotion_intensity']}%)\n"
        
        # Handle compatibility with both old and new record formats
        thought_text = record.get("thought", record.get("negative_thought", ""))
        records_text += f"Automatic Thought: {thought_text}\n"

        if record.get('distortions'):
            records_text += f"Thinking Patterns: {', '.join(record['distortions'])}\n"

        if record.get('evidence_for'):
            records_text += f"Evidence For: {record['evidence_for']}\n"

        if record.get('evidence_against'):
            records_text += f"Evidence Against: {record['evidence_against']}\n"

        records_text += f"Alternative Thought: {record['balanced_thought']}\n"
        records_text += f"New Emotion Intensity: {record['new_emotion_intensity']}%\n"

        improvement = record['emotion_intensity'] - record['new_emotion_intensity']
        if improvement > 0:
            records_text += f"Improvement: {improvement}% decrease in intensity\n"
            
        if record.get('reflection'):
            records_text += f"Reflection: {record['reflection']}\n"

        records_text += "\n---\n\n"

    return records_text