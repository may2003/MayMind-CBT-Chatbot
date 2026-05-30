import streamlit as st
from datetime import datetime
import pandas as pd
import altair as alt

def track_mood():
    """Interactive mood tracking tool."""
    col1, col2 = st.columns([3, 1])

    with col1:
        today_mood = st.slider("How are you feeling today?", 1, 10, 5, 
                              help="1 = Very low, 10 = Excellent")
        mood_notes = st.text_input("Any notes about your mood? (optional)")

    with col2:
        if st.button("Save Mood", use_container_width=True):
            if "mood_history" not in st.session_state:
                st.session_state.mood_history = []

            st.session_state.mood_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "score": today_mood,
                "notes": mood_notes
            })
            st.success("Mood saved!")
            st.rerun()

    # Show mood history if available
    if "mood_history" in st.session_state and st.session_state.mood_history:
        st.subheader("Your Mood History")

        # Create plot data
        mood_data = pd.DataFrame([
            {
                "date": datetime.strptime(m["timestamp"], "%Y-%m-%d %H:%M"),
                "score": m["score"]
            }
            for m in st.session_state.mood_history
        ])

        # Create line chart
        chart = alt.Chart(mood_data).mark_line(point=True).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('score:Q', title='Mood (1-10)', scale=alt.Scale(domain=[1, 10])),
            tooltip=['date:T', 'score:Q']
        ).properties(
            height=200
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # Summary statistics
        if len(st.session_state.mood_history) >= 3:
            st.subheader("Mood Insights")

            avg_mood = sum(m["score"] for m in st.session_state.mood_history) / len(st.session_state.mood_history)
            recent_trend = st.session_state.mood_history[-1]["score"] - st.session_state.mood_history[0]["score"]

            # Calculate 7-day average if enough data
            recent_moods = [m for m in st.session_state.mood_history 
                           if datetime.strptime(m["timestamp"], "%Y-%m-%d %H:%M") > 
                           datetime.now() - pd.Timedelta(days=7)]

            if recent_moods:
                recent_avg = sum(m["score"] for m in recent_moods) / len(recent_moods)

                st.write(f"Your average mood: **{avg_mood:.1f}/10**")
                st.write(f"Your 7-day average: **{recent_avg:.1f}/10**")

                if recent_trend > 0:
                    st.success(f"Your mood has improved by {recent_trend:.1f} points since you started tracking!")
                elif recent_trend < 0:
                    st.info(f"Your mood has decreased by {abs(recent_trend):.1f} points since you started tracking.")
                else:
                    st.info("Your mood has remained stable overall.")

        # Display mood entries in expandable sections
        st.subheader("Detailed Mood Log")

        for i, mood in enumerate(reversed(st.session_state.mood_history)):
            with st.expander(f"{mood['timestamp']}: {mood['score']}/10"):
                st.write(f"**Score:** {mood['score']}/10")
                if mood.get("notes"):
                    st.write(f"**Notes:** {mood['notes']}")

                # Delete entry button
                if st.button("Delete Entry", key=f"delete_mood_{i}"):
                    st.session_state.mood_history.remove(mood)
                    st.success("Entry deleted!")
                    st.rerun()