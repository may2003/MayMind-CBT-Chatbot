import pytest
import sys
import os
from unittest.mock import MagicMock, patch
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.therapist import get_ai_response, create_therapist_prompt

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

@patch('openai.OpenAI')
def test_context_window_management(mock_openai, mock_session_state):
    """Test that context window correctly limits message history"""
    # Configure mock
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Test response"
    mock_client.chat.completions.create.return_value = mock_response
    
    # Create long message history (more than 8 messages)
    mock_session_state.chat_history = []
    for i in range(12):
        mock_session_state.chat_history.append({
            "role": "user" if i % 2 == 0 else "assistant",
            "content": f"Message {i+1}"
        })
    
    # Call function
    get_ai_response("New message")
    
    # Verify context window implementation
    call_args = mock_client.chat.completions.create.call_args[1]
    messages = call_args['messages']
    
    # Check that messages are limited correctly
    user_assistant_messages = [m for m in messages if m['role'] in ('user', 'assistant')]
    assert len(user_assistant_messages) <= 9  # 8 from history + 1 new message
    
    # Verify we have the most recent messages
    assert any(m['content'] == "Message 12" for m in messages)
    assert any(m['content'] == "Message 11" for m in messages)
    
    # Verify we don't have the oldest messages
    assert not any(m['content'] == "Message 1" for m in messages)
    assert not any(m['content'] == "Message 2" for m in messages)

def test_mood_trend_detection(mock_session_state):
    """Test mood trend detection logic in prompt creation"""
    # Test improving mood
    mock_session_state.mood_history = [
        {"timestamp": "2023-05-01 10:00", "score": 3},
        {"timestamp": "2023-05-02 10:00", "score": 6}
    ]
    prompt = create_therapist_prompt()
    assert "improving from 3" in prompt
    
    # Test declining mood
    mock_session_state.mood_history = [
        {"timestamp": "2023-05-01 10:00", "score": 7},
        {"timestamp": "2023-05-02 10:00", "score": 4}
    ]
    prompt = create_therapist_prompt()
    assert "declining from 7" in prompt
    
    # Test stable mood
    mock_session_state.mood_history = [
        {"timestamp": "2023-05-01 10:00", "score": 5},
        {"timestamp": "2023-05-02 10:00", "score": 5}
    ]
    prompt = create_therapist_prompt()
    assert "stable" in prompt