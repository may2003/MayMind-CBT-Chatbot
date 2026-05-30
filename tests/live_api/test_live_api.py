"""
Live API tests for CBT Chatbot.
These tests use the actual OpenAI API and will incur charges.
Skip if no API key is available.
"""

import pytest
import os
import sys
import streamlit as st
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Get API key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")
skip_live_api = api_key is None

# All tests in this file require API key
pytestmark = pytest.mark.skipif(
    skip_live_api, 
    reason="No API key available for live testing"
)

@pytest.fixture
def mock_session_state():
    """Set up mock session state for testing"""
    # Store original session_state
    original_session_state = getattr(st, "session_state", None)
    
    # Create mock session state
    mock_state = MagicMock()
    
    # Set common attributes
    mock_state.user_name = "Test User"
    mock_state.phq9_total = 10
    mock_state.gad7_total = 8
    mock_state.chat_history = []
    mock_state.mood_history = [
        {"timestamp": "2023-05-01 10:00", "score": 5},
        {"timestamp": "2023-05-02 10:00", "score": 6}
    ]
    mock_state.thought_records = [
        {"thought": "I'm worried about my presentation tomorrow"}
    ]
    mock_state.activity_schedule = [
        {"name": "Morning walk", "completed": False}
    ]
    
    # Replace st.session_state with our mock
    st.session_state = mock_state
    
    yield mock_state
    
    # Restore original session state after test
    if original_session_state is not None:
        st.session_state = original_session_state

def test_live_api_single_response(mock_session_state):
    """Test a single response from the live API"""
    from ai.therapist import get_ai_response
    
    # Ensure API key is set
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Get a response
    response = get_ai_response("I've been feeling anxious lately")
    
    # Basic validation
    assert response is not None
    assert len(response) > 50
    
    # Check for therapeutic content
    therapeutic_terms = ["anxiety", "feel", "thoughts", "help", "understand"]
    assert any(term in response.lower() for term in therapeutic_terms)

def test_live_api_conversation_flow(mock_session_state):
    """Test a conversation flow with the live API"""
    from ai.therapist import get_ai_response
    
    # Ensure API key is set
    os.environ["OPENAI_API_KEY"] = api_key
    
    # First message
    mock_session_state.chat_history = []
    response1 = get_ai_response("I'm feeling stressed about work", save_to_history=True)
    
    # Second message - should reference the first
    response2 = get_ai_response("My boss is demanding too much", save_to_history=True)
    
    # Verify responses
    assert response1 is not None and response2 is not None
    assert len(response1) > 0 and len(response2) > 0
    
    # Second response should reference work context
    work_terms = ["work", "boss", "workplace", "stress", "demand"]
    assert any(term in response2.lower() for term in work_terms)