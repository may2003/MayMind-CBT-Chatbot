import streamlit as st
from fpdf import FPDF
import base64
import io
from datetime import datetime
import re
import os
import unicodedata

class CBTReportPDF(FPDF):
    """PDF generator class for CBT reports"""
    def __init__(self, user_name):
        super().__init__()
        self.user_name = user_name
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
        # Add logo in top-left corner
        try:
            # Check if logo exists
            logo_path = "assets/app-name.png"
            if os.path.exists(logo_path):
                # Add logo at position (10, 8), with width 40mm
                self.image(logo_path, 10, 8, 40)
            else:
                # If image doesn't exist, log the issue but continue
                print(f"Logo file not found at {logo_path}")
        except Exception as e:
            # If there's any error with the image, log it but continue
            print(f"Error adding logo: {str(e)}")
        
        # Add header text
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "MayMind CBT Session Report", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Generated for: {user_name}", ln=True, align="C")
        self.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True, align="C")
        self.ln(5)

    def add_section(self, title, content, height=10):
        """Add a titled section to the PDF"""
        self.set_font("Arial", "B", 14)
        self.cell(0, height, title, ln=True)
        self.set_font("Arial", "", 12)
        # Sanitize content to remove emojis and non-latin1 characters
        sanitized_content = remove_emojis(content)
        self.multi_cell(0, 8, sanitized_content)
        self.ln(5)

    def add_assessment_results(self):
        """Add PHQ-9 and GAD-7 assessment results"""
        phq9_score = st.session_state.phq9_total
        gad7_score = st.session_state.gad7_total
        
        # Map scores to severity
        def get_phq9_severity(score):
            if score < 5: return "Minimal or none"
            elif score < 10: return "Mild"
            elif score < 15: return "Moderate"
            elif score < 20: return "Moderately severe"
            else: return "Severe"
            
        def get_gad7_severity(score):
            if score < 5: return "Minimal anxiety"
            elif score < 10: return "Mild anxiety"
            elif score < 15: return "Moderate anxiety"
            else: return "Severe anxiety"
        
        content = f"Depression (PHQ-9): {phq9_score}/27 - {get_phq9_severity(phq9_score)}\n"
        content += f"Anxiety (GAD-7): {gad7_score}/21 - {get_gad7_severity(gad7_score)}\n\n"
        content += "These scores represent your self-reported symptoms at the beginning of your session."
        
        self.add_section("Assessment Results", content)
        
    def add_thought_records(self):
        """Add thought records to the PDF"""
        # Import function from thought_journal
        from tools.thought_journal import get_thought_records_for_pdf
        thought_records = get_thought_records_for_pdf()
        self.add_section("Thought Journal", thought_records)
        
    def add_activities(self):
        """Add scheduled activities to the PDF"""
        # Import function from activity_scheduler
        from tools.activity_scheduler import get_activities_for_pdf
        activities = get_activities_for_pdf()
        self.add_section("Activity Schedule", activities)

def remove_emojis(text):
    """Remove emojis and any other characters that can't be encoded in latin-1"""
    if not text:
        return ""
        
    # Replace specific emojis with text alternatives
    text = text.replace('📊', 'Chart')
    text = text.replace('💡', 'Idea')
    text = text.replace('🌟', 'Star')
    text = text.replace('📝', 'Note')
    text = text.replace('📅', 'Calendar')
    text = text.replace('🔍', 'Search')
    
    # Use regex pattern for comprehensive emoji removal
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
    
    text = emoji_pattern.sub('', text)
    
    # Remove any remaining characters that can't be encoded in latin-1
    return ''.join(c for c in text if ord(c) < 256)

def generate_session_report_pdf(user_name):
    """Generate a complete session report PDF"""
    pdf = CBTReportPDF(user_name)
    
    # Add assessment results
    pdf.add_assessment_results()
    
    # Add summary section
    from ai.therapist import generate_session_summary
    summary = generate_session_summary(for_pdf=True)
    pdf.add_section("Session Summary", summary)
    
    # Add thought records
    pdf.add_thought_records()
    
    # Add activities
    pdf.add_activities()
    
    return pdf

def generate_session_summary_pdf(user_name):
    """Generate a brief summary PDF without the full conversation"""
    pdf = CBTReportPDF(user_name)
    
    # Add assessment results
    pdf.add_assessment_results()
    
    # Add summary section
    from ai.therapist import generate_session_summary
    summary = generate_session_summary(for_pdf=True)
    pdf.add_section("Session Summary", summary)
    
    # Add thought records
    pdf.add_thought_records()
    
    # Add activities
    pdf.add_activities()
    
    return pdf

def download_pdf(pdf, filename="CBT_Session_Report"):
    """Create a download button for the PDF"""
    try:
        # Generate filename with date and user
        safe_name = st.session_state.user_name.replace(" ", "_")
        pdf_filename = f"{filename}_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Save PDF to file instead of using BytesIO
        pdf.output(pdf_filename)
        
        # Create download button
        with open(pdf_filename, "rb") as f:
            pdf_bytes = f.read()
            st.download_button(
                label=f"Download {filename}",
                data=pdf_bytes,
                file_name=pdf_filename,
                mime="application/pdf"
            )
        
        # Clean up file after download option is presented
        if os.path.exists(pdf_filename):
            # Don't remove yet - the file needs to stay until the user downloads it
            # We'd need a callback to remove it after download
            pass
            
        return True
    except Exception as e:
        st.error(f"There was an error generating the PDF: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")
        return False