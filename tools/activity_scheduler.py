import streamlit as st
from datetime import datetime
import pandas as pd

def activity_scheduler():
    """Interactive activity scheduling tool for behavioral activation."""
    st.markdown("""
    ### 📅 Activity Scheduler

    Use this tool to plan and schedule activities that bring you joy or a sense of accomplishment.
    Behavioral activation is a key CBT technique to improve mood and motivation.
    """)

    # Create tabs for adding new activities and viewing the schedule
    tab1, tab2 = st.tabs(["New Activity", "Scheduled Activities"])

    # Tab 1: Add new activity
    with tab1:
        with st.form("activity_form"):
            st.subheader("Plan a New Activity")

            # Activity details
            activity_name = st.text_input("Activity Name", placeholder="e.g., Go for a walk")
            activity_date = st.date_input("Date", min_value=datetime.now().date())
            activity_time = st.time_input("Time")
            activity_notes = st.text_area("Notes (optional)", placeholder="e.g., Bring a water bottle")

            # Submit button
            submitted = st.form_submit_button("Add Activity")

        if submitted:
            if not activity_name:
                st.error("Please provide a name for the activity.")
            else:
                # Initialize activity schedule if it doesn't exist
                if "activity_schedule" not in st.session_state:
                    st.session_state.activity_schedule = []

                # Add the activity to the schedule
                st.session_state.activity_schedule.append({
                    "name": activity_name,
                    "date": activity_date.strftime("%Y-%m-%d"),
                    "time": activity_time.strftime("%H:%M"),
                    "notes": activity_notes,
                    "completed": False
                })

                st.success("Activity added to your schedule!")

    # Tab 2: View scheduled activities
    with tab2:
        if "activity_schedule" in st.session_state and st.session_state.activity_schedule:
            st.subheader("Your Scheduled Activities")

            # Convert schedule to DataFrame for display
            schedule_df = pd.DataFrame(st.session_state.activity_schedule)

            # Sort by date and time
            schedule_df["datetime"] = pd.to_datetime(schedule_df["date"] + " " + schedule_df["time"])
            schedule_df = schedule_df.sort_values(by="datetime").drop(columns="datetime")

            # Display activities
            for i, activity in schedule_df.iterrows():
                with st.expander(f"{activity['date']} {activity['time']}: {activity['name']}"):
                    st.markdown(f"**Name:** {activity['name']}")
                    st.markdown(f"**Date:** {activity['date']}")
                    st.markdown(f"**Time:** {activity['time']}")
                    if activity['notes']:
                        st.markdown(f"**Notes:** {activity['notes']}")

                    # Mark as completed button
                    if not activity['completed']:
                        if st.button("Mark as Completed", key=f"complete_{i}"):
                            st.session_state.activity_schedule[i]["completed"] = True
                            st.success("Activity marked as completed!")
                            st.rerun()

                    # Delete activity button
                    if st.button("Delete Activity", key=f"delete_{i}"):
                        st.session_state.activity_schedule.pop(i)
                        st.success("Activity deleted!")
                        st.rerun()
        else:
            st.info("No activities scheduled yet. Add your first activity in the 'New Activity' tab.")

def get_activities_for_pdf():
    """Return formatted activity schedule for PDF export."""
    if "activity_schedule" not in st.session_state or not st.session_state.activity_schedule:
        return "No activities scheduled."

    # Format as text
    activities_text = "Scheduled Activities:\n\n"
    for activity in st.session_state.activity_schedule:
        activities_text += f"Name: {activity['name']}\n"
        activities_text += f"Date: {activity['date']}\n"
        activities_text += f"Time: {activity['time']}\n"
        if activity['notes']:
            activities_text += f"Notes: {activity['notes']}\n"
        activities_text += f"Completed: {'Yes' if activity['completed'] else 'No'}\n"
        activities_text += "\n---\n\n"

    return activities_text