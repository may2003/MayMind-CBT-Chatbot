import streamlit as st
from fpdf import FPDF
import base64
import os
from datetime import datetime
import re

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

def generate_chat_transcript_pdf(user_name):
    """Generate a PDF with just the chat conversation"""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Add logo if available
    try:
        logo_path = "assets/app-name.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, 10, 8, 40)
    except Exception as e:
        print(f"Error adding logo: {str(e)}")
    
    # Add header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MayMind CBT Conversation Transcript", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"User: {user_name}", ln=True, align="C")
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%B %d, %Y')}", ln=True, align="C")
    pdf.ln(5)
    
    # Add conversation
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Conversation", ln=True)
    pdf.set_font("Arial", "", 12)
    
    if not st.session_state.chat_history:
        pdf.multi_cell(0, 8, "No conversation recorded.")
        return pdf
    
    # Format conversation for PDF
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            # User message with slight indent
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"{user_name}:", ln=True)
            pdf.set_font("Arial", "", 12)
            
            # Clean formatting and remove emojis
            content = re.sub(r'#+\s+', '', msg['content'])  # Remove headers
            content = re.sub(r'\*\*|\*', '', content)  # Remove bold/italic
            content = remove_emojis(content)  # Remove emojis
            
            pdf.multi_cell(0, 8, content)
            pdf.ln(5)
        else:
            # AI message with slight indent
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "May:", ln=True)
            pdf.set_font("Arial", "", 12)
            
            # Clean formatting and remove emojis
            content = re.sub(r'#+\s+', '', msg['content'])  # Remove headers
            content = re.sub(r'\*\*|\*', '', content)  # Remove bold/italic
            content = remove_emojis(content)  # Remove emojis
            
            pdf.multi_cell(0, 8, content)
            pdf.ln(5)
    
    return pdf

def download_transcript(user_name, format_type="pdf"):
    """Generate and provide download for transcript in specified format"""
    if format_type == "pdf":
        pdf = generate_chat_transcript_pdf(user_name)
        download_pdf(pdf, f"{user_name}_CBT_Transcript")
    elif format_type == "text":
        transcript_text = generate_text_transcript(user_name)
        download_text(transcript_text, f"{user_name}_CBT_Transcript")
    else:
        st.error("Unknown format type requested")

def generate_text_transcript(user_name):
    """Generate a plain text transcript"""
    if not st.session_state.chat_history:
        return "No conversation recorded."
    
    transcript = f"MayMind CBT Conversation Transcript\n"
    transcript += f"User: {user_name}\n"
    transcript += f"Date: {datetime.now().strftime('%B %d, %Y')}\n\n"
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            transcript += f"{user_name}: {msg['content']}\n\n"
        else:
            transcript += f"May: {msg['content']}\n\n"
    
    return transcript

def download_text(text_content, filename="CBT_Transcript"):
    """Create a download button for text content"""
    b64 = base64.b64encode(text_content.encode()).decode()
    
    # Create a download button
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}.txt">Download Text File</a>'
    
    return st.markdown(href, unsafe_allow_html=True)

def download_pdf(pdf, filename="CBT_Transcript"):
    """Create a download button for the PDF using file-based approach"""
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
            pass
            
        return True
    except Exception as e:
        st.error(f"There was an error generating the PDF: {str(e)}")
        st.info("Please try again or contact support if the issue persists.")
        return False