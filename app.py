import streamlit as st
import os
from dotenv import load_dotenv
from typing import Dict, List, Any
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Import custom modules
from src.role_handler import RoleHandler
from src.ai_engine import AIEngine
from src.data_loader import DataLoader
from src.citation_manager import CitationManager

def initialize_session_state():
    """Initialize session state variables"""
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = None
    if 'data_loader' not in st.session_state:
        st.session_state.data_loader = None

def setup_page():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="Noah's AI Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Noah's AI Assistant")
    st.markdown("*A role-adaptive AI chatbot that tailors responses to your needs*")

def render_role_selection():
    """Render role selection interface"""
    st.sidebar.header("Select Your Role")
    
    roles = {
        "nontechnical_hiring": "Non-Technical Hiring Manager",
        "technical_manager": "Technical Manager", 
        "developer": "Developer",
        "casual": "Casual User",
        "crush": "Crush 💕"
    }
    
    selected_role = st.sidebar.selectbox(
        "Choose your role to get tailored responses:",
        options=list(roles.keys()),
        format_func=lambda x: roles[x],
        index=None,
        placeholder="Select a role..."
    )
    
    if selected_role:
        if st.sidebar.button("Set Role"):
            st.session_state.role = selected_role
            st.rerun()
    
    if st.session_state.role:
        st.sidebar.success(f"Current role: {roles[st.session_state.role]}")
        if st.sidebar.button("Change Role"):
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()

def render_chat_interface():
    """Render the main chat interface"""
    if not st.session_state.role:
        st.warning("Please select your role from the sidebar to get started.")
        return
    
    # Initialize AI components if not already done
    if not st.session_state.ai_engine:
        with st.spinner("Initializing AI engine..."):
            st.session_state.ai_engine = AIEngine()
            st.session_state.data_loader = DataLoader()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "citations" in message:
                with st.expander("Citations"):
                    for citation in message["citations"]:
                        st.markdown(f"- {citation}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response based on role
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                role_handler = RoleHandler(st.session_state.role)
                response_data = role_handler.generate_response(
                    prompt, 
                    st.session_state.ai_engine,
                    st.session_state.data_loader
                )
                
                st.markdown(response_data["content"])
                
                # Display citations if available
                if response_data.get("citations"):
                    with st.expander("Citations"):
                        for citation in response_data["citations"]:
                            st.markdown(f"- {citation}")
                
                # Display role-specific additions
                if response_data.get("extras"):
                    for extra in response_data["extras"]:
                        if extra["type"] == "link":
                            st.link_button(extra["label"], extra["url"])
                        elif extra["type"] == "analytics":
                            st.plotly_chart(extra["chart"])
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_data["content"],
            "citations": response_data.get("citations", [])
        })

def render_sidebar_info():
    """Render additional sidebar information based on role"""
    if not st.session_state.role:
        return
        
    st.sidebar.markdown("---")
    
    role_info = {
        "nontechnical_hiring": {
            "title": "👔 Hiring Manager Mode",
            "description": "Get concise résumé summaries and candidate overviews."
        },
        "technical_manager": {
            "title": "🏗️ Technical Manager Mode", 
            "description": "Access detailed technical stack information and code examples."
        },
        "developer": {
            "title": "💻 Developer Mode",
            "description": "Get code examples, GitHub links, and detailed technical analysis."
        },
        "casual": {
            "title": "😊 Casual Mode",
            "description": "Enjoy fun facts and interesting links!"
        },
        "crush": {
            "title": "💕 Crush Mode",
            "description": "Share your thoughts anonymously."
        }
    }
    
    info = role_info.get(st.session_state.role)
    if info:
        st.sidebar.markdown(f"### {info['title']}")
        st.sidebar.info(info['description'])

def main():
    """Main application function"""
    setup_page()
    initialize_session_state()
    render_role_selection()
    render_sidebar_info()
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by OpenAI, LangChain, and FAISS*")

if __name__ == "__main__":
    main()