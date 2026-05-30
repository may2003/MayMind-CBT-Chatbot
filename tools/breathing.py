import streamlit as st
import time
from datetime import datetime

def breathing_exercise():
    """Interactive breathing exercise for relaxation."""
    st.markdown("""
    ## 🧘 Breathing Exercise

    Use this guided breathing exercise to help you relax and reduce stress. This technique can help:
    - Reduce anxiety and stress
    - Improve focus
    - Promote relaxation
    - Manage difficult emotions
    """)
    
    # Customization options
    st.subheader("Customize Your Exercise")
    
    # Fixed breathing pattern values
    inhale_duration = 4
    hold_duration = 4
    exhale_duration = 6
    
    num_cycles = st.slider("Number of Cycles", min_value=3, max_value=10, value=5)
    
    # Fixed instructions for standard breathing pattern
    instruction_text = """
    ### Instructions:
    - Inhale deeply through your nose for 4 seconds
    - Hold your breath for 4 seconds
    - Exhale slowly through your mouth for 6 seconds
    - Repeat for the selected number of cycles
    """
    
    st.markdown(instruction_text)

    # Start button
    if st.button("Start Breathing Exercise", use_container_width=True):
        st.info("Follow the instructions below and focus on your breathing.")
        
        # Create placeholder for text
        text_placeholder = st.empty()
        
        # Track start time for reporting
        start_time = time.time()

        # Perform breathing cycles
        for cycle in range(num_cycles):
            st.write(f"Cycle {cycle + 1} of {num_cycles}")
            
            # INHALE
            text_placeholder.markdown("### **Inhale...**")
            time.sleep(inhale_duration)
            
            # HOLD
            text_placeholder.markdown("### **Hold...**")
            time.sleep(hold_duration)
            
            # EXHALE
            text_placeholder.markdown("### **Exhale...**")
            time.sleep(exhale_duration)
            
            # Add a progress bar for visualization
            progress = (cycle + 1) / num_cycles
            st.progress(progress)
        
        # Calculate total time
        duration = round(time.time() - start_time)
        minutes, seconds = divmod(duration, 60)
        time_str = f"{minutes} minute{'s' if minutes != 1 else ''}" if minutes > 0 else f"{seconds} seconds"
        
        # Clear text placeholder
        text_placeholder.empty()
        
        st.success(f"✅ Breathing exercise complete! ({time_str})")

        # Save exercise to session state for progress tracking
        if "breathing_exercises" not in st.session_state:
            st.session_state.breathing_exercises = []
        st.session_state.breathing_exercises.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cycles": num_cycles,
            "duration": duration
        })

