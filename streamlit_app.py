#!/usr/bin/env python3
"""
Finance Assistant Chatbot - Streamlit UI
Simple ChatGPT-like interface with persistent chat memory
"""

import datetime
import json
import os

import streamlit as st

from finance_chatbot import FinanceChatbot

# Page configuration
st.set_page_config(
    page_title="ABC Housing Finance Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Simple custom CSS for brand colors only
st.markdown(
    """
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Brand colors only for buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Simple input styling */
    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Chat session styling */
    .chat-session {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .chat-session:hover {
        background: #e2e8f0;
        border-color: #667eea;
    }
    
    .chat-session.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
</style>
""",
    unsafe_allow_html=True,
)


def initialize_chatbot():
    """Initialize the finance chatbot."""
    try:
        return FinanceChatbot()
    except Exception as e:
        st.error(f"Failed to initialize chatbot: {str(e)}")
        return None


def save_chat_session(session_id, messages, title):
    """Save chat session to file."""
    try:
        # Create chats directory if it doesn't exist
        os.makedirs("chats", exist_ok=True)

        chat_data = {
            "session_id": session_id,
            "title": title,
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "messages": messages,
        }

        file_path = f"chats/{session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        st.error(f"Failed to save chat: {str(e)}")
        return False


def load_chat_session(session_id):
    """Load chat session from file."""
    try:
        file_path = f"chats/{session_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
    except Exception as e:
        st.error(f"Failed to load chat: {str(e)}")
        return None


def list_chat_sessions():
    """List all available chat sessions."""
    try:
        if not os.path.exists("chats"):
            return []

        sessions = []
        for filename in os.listdir("chats"):
            if filename.endswith(".json"):
                file_path = f"chats/{filename}"
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        session_data = json.load(f)
                        sessions.append(session_data)
                except:
                    continue

        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        return sessions
    except Exception as e:
        st.error(f"Failed to list chats: {str(e)}")
        return []


def delete_chat_session(session_id):
    """Delete a chat session."""
    try:
        file_path = f"chats/{session_id}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        st.error(f"Failed to delete chat: {str(e)}")
        return False


def generate_chat_title(first_message):
    """Generate a title for the chat based on the first message."""
    if len(first_message) > 50:
        return first_message[:50] + "..."
    return first_message


def main():
    """Main Streamlit application."""

    # Initialize session state
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_title" not in st.session_state:
        st.session_state.chat_title = "New Chat"

    # Simple header with brand colors
    st.markdown("---")
    st.title("🏦 ABC Housing Finance Assistant")
    st.markdown("Your AI-powered guide to housing finance and home loans")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        # Logo
        st.image(
            "Screenshot_2025-07-16_at_6.34.27_PM-removebg-preview copy.png", width=150
        )
        st.markdown("---")

        # Chatbot status
        chatbot = initialize_chatbot()
        if chatbot:
            st.success("✅ Chatbot Connected")
            st.info(f"📊 Index: {chatbot.index_name}")
            st.info(f"🏷️ Namespace: {chatbot.namespace}")
        else:
            st.error("❌ Chatbot Unavailable")
            st.stop()

        st.markdown("---")

        # Chat Management
        st.header("💾 Chat History")

        # New Chat Button
        if st.button("🆕 New Chat", use_container_width=True, type="primary"):
            st.session_state.current_session_id = None
            st.session_state.messages = []
            st.session_state.chat_title = "New Chat"
            st.rerun()

        st.markdown("---")

        # List existing chat sessions
        chat_sessions = list_chat_sessions()

        if chat_sessions:
            st.subheader("📚 Previous Chats")

            for session in chat_sessions:
                session_id = session["session_id"]
                title = session["title"]
                updated_at = session.get("updated_at", "")

                # Format date
                try:
                    dt = datetime.datetime.fromisoformat(updated_at)
                    date_str = dt.strftime("%b %d, %H:%M")
                except:
                    date_str = "Unknown"

                # Check if this is the active session
                is_active = session_id == st.session_state.current_session_id

                # Display chat session
                col1, col2 = st.columns([4, 1])

                with col1:
                    if st.button(
                        f"💬 {title}",
                        key=f"chat_{session_id}",
                        use_container_width=True,
                        help=f"Last updated: {date_str}",
                    ):
                        # Load this chat session
                        loaded_session = load_chat_session(session_id)
                        if loaded_session:
                            st.session_state.current_session_id = session_id
                            st.session_state.messages = loaded_session["messages"]
                            st.session_state.chat_title = loaded_session["title"]
                            st.rerun()

                with col2:
                    if st.button("🗑️", key=f"del_{session_id}", help="Delete this chat"):
                        if delete_chat_session(session_id):
                            st.rerun()
        else:
            st.info("No previous chats found. Start a new conversation!")

        st.markdown("---")

        # Quick suggestions
        st.header("💡 Quick Questions")

        suggestions = [
            "What home loan products does ABC Housing Finance offer?",
            "What are the interest rates for home loans?",
            "How does the construction loan work?",
            "What are the eligibility requirements?",
            "How do I apply for a home loan?",
        ]

        for suggestion in suggestions:
            if st.button(
                suggestion, key=f"sugg_{suggestion[:20]}", use_container_width=True
            ):
                st.session_state.suggestion_clicked = suggestion
                st.rerun()

    # Main chat area
    if st.session_state.messages:
        # Chat header with title
        st.header(f"💬 {st.session_state.chat_title}")

        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                # User message with brand colors
                st.markdown("**You:**")
                st.markdown(
                    f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 1rem;
                    border-radius: 15px;
                    margin: 0.5rem 0 1rem 0;
                    text-align: right;
                ">
                    {message["content"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                # Assistant message
                st.markdown("**Assistant:**")
                st.markdown(
                    f"""
                <div style="
                    background: #f8f9fa;
                    color: #333;
                    padding: 1rem;
                    border-radius: 15px;
                    margin: 0.5rem 0 1rem 0;
                    border-left: 4px solid #667eea;
                ">
                    {message["response"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Show source documents if available
                if (
                    message.get("relevant_chunks")
                    and len(message["relevant_chunks"]) > 0
                ):
                    with st.expander("📖 View Source Documents", expanded=False):
                        st.markdown("**Relevant information from documents:**")
                        for i, chunk in enumerate(message["relevant_chunks"][:3], 1):
                            st.markdown(f"**Document {i}:** {chunk['text'][:200]}...")

    # Welcome message if no chat history
    if not st.session_state.messages:
        st.markdown("---")
        st.title("🎉 Welcome to your Finance Assistant!")
        st.markdown(
            "I'm here to help you with questions about housing finance, home loans, and financial planning"
        )

        # Feature grid using Streamlit columns
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🏠 Home Loans")
            st.markdown("Get information about home loan products and rates")

            st.markdown("### 💰 Interest Rates")
            st.markdown("Current rates and how they affect your loan")

        with col2:
            st.markdown("### 📋 Requirements")
            st.markdown("Eligibility criteria and required documents")

            st.markdown("### 📊 Loan Types")
            st.markdown("Different loan options and their features")

        st.markdown("---")
        st.markdown(
            "*Start by asking a question or use the quick suggestions in the sidebar!*"
        )

    # Simple chat input area
    st.markdown("---")
    st.header("💬 Ask a Question")

    # Input and button
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        user_input = st.text_input(
            "Type your question here...",
            key="user_input",
            value=st.session_state.get("suggestion_clicked", ""),
            placeholder="Ask about home loans, interest rates, requirements...",
            label_visibility="collapsed",
        )

        if user_input:
            send_button = st.button("🚀 Send Message", use_container_width=True)
        else:
            send_button = st.button(
                "🚀 Send Message", use_container_width=True, disabled=True
            )

    # Process message
    if send_button and user_input:
        # Generate or get session ID
        if not st.session_state.current_session_id:
            st.session_state.current_session_id = (
                f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            st.session_state.chat_title = generate_chat_title(user_input)

        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Clear the suggestion after sending
        if "suggestion_clicked" in st.session_state:
            st.session_state.suggestion_clicked = None

        # Show processing
        with st.spinner("🤔 Finance Assistant is thinking..."):
            try:
                # Get response from chatbot
                response = chatbot.chat(user_input)

                # Add assistant response to chat
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response["response"],
                        "response": response["response"],
                        "response_source": response.get("response_source", "general"),
                        "confidence": response.get("confidence", "medium"),
                        "context_chunks": response.get("context_chunks", 0),
                        "relevant_chunks": response.get("relevant_chunks", []),
                    }
                )

                # Save chat session
                save_chat_session(
                    st.session_state.current_session_id,
                    st.session_state.messages,
                    st.session_state.chat_title,
                )

                # Rerun to display new messages
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"I apologize, but I encountered an error: {str(e)}",
                        "response": f"I apologize, but I encountered an error: {str(e)}",
                        "response_source": "error",
                        "confidence": "low",
                        "context_chunks": 0,
                        "relevant_chunks": [],
                    }
                )

                # Save chat session even with error
                save_chat_session(
                    st.session_state.current_session_id,
                    st.session_state.messages,
                    st.session_state.chat_title,
                )

                st.rerun()


if __name__ == "__main__":
    main()
