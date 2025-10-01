"""Example integration of Common Questions system with existing Streamlit app.

This file shows how to integrate the common questions functionality
into Noah's AI Assistant main application.
"""
import streamlit as st
from typing import Optional

# Existing imports (your current main.py imports)
# from src.core.rag_engine import RagEngine
# from src.core.memory import Memory
# from src.agents.role_router import RoleRouter

# New imports for common questions
from src.integration.common_questions_integration import (
    CommonQuestionsIntegration,
    init_common_questions_session_state,
    setup_questions_integration,
    display_question_metrics_sidebar
)


def initialize_common_questions_system(rag_engine, memory_system, role_router):
    """Initialize the common questions system with existing components."""
    
    # Initialize session state for common questions
    init_common_questions_session_state()
    
    # Set up the integration
    integration = setup_questions_integration(
        rag_engine=rag_engine,
        memory_system=memory_system,
        role_router=role_router
    )
    
    return integration


def display_welcome_section(integration: CommonQuestionsIntegration, user_role: str) -> Optional[str]:
    """Display welcome section with common questions for the selected role."""
    
    st.markdown("---")
    
    # Main common questions display
    selected_question = integration.display_welcome_questions(user_role)
    
    # Show trending questions if available
    trending = integration.get_trending_questions(days=7)
    if trending:
        with st.expander("🔥 Trending This Week", expanded=False):
            for q_data in trending[:3]:
                question = q_data['question']
                frequency = q_data['frequency']
                
                if st.button(f"❓ {question}", key=f"trending_{question}"):
                    selected_question = question
                
                st.caption(f"Asked {frequency} times recently")
    
    return selected_question


def enhanced_chat_interface(integration: CommonQuestionsIntegration, user_role: str):
    """Enhanced chat interface with common questions integration."""
    
    # Sidebar suggestions
    sidebar_question = integration.display_sidebar_suggestions(user_role)
    
    # Main chat interface
    st.subheader("💬 Chat with Noah's AI Assistant")
    
    # Get session history for personalization
    chat_history = st.session_state.get('chat_history', [])
    previous_questions = [msg['content'] for msg in chat_history if msg['role'] == 'user']
    
    # Personalized suggestions based on history
    if len(previous_questions) > 0:
        personalized = integration.get_personalized_suggestions(
            role=user_role,
            session_history=previous_questions
        )
        
        if personalized:
            st.markdown("**💡 You might also ask:**")
            cols = st.columns(len(personalized))
            
            for i, suggestion in enumerate(personalized):
                with cols[i]:
                    if st.button(suggestion, key=f"personalized_{i}", use_container_width=True):
                        return suggestion
    
    # Regular chat input
    user_input = st.chat_input("Ask me anything about Noah...")
    
    # Return selected question (from sidebar, personalized, or manual input)
    return sidebar_question or user_input


def process_user_query(integration: CommonQuestionsIntegration, 
                      user_role: str, query: str, session_id: str):
    """Process user query with analytics tracking."""
    
    try:
        # Get current chat history
        chat_history = st.session_state.get('chat_history', [])
        
        # Process with full tracking
        response = integration.process_question_with_tracking(
            session_id=session_id,
            user_role=user_role,
            query=query,
            chat_history=chat_history
        )
        
        # Display response
        with st.chat_message("assistant"):
            st.write(response.get('response', 'Sorry, I had trouble processing that question.'))
            
            # Show metadata if available
            metadata = response.get('_metadata', {})
            if metadata:
                with st.expander("ℹ️ Response Details", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Response Time", f"{metadata.get('response_time', 0):.2f}s")
                    
                    with col2:
                        st.metric("Query Type", metadata.get('query_type', 'unknown').title())
                    
                    with col3:
                        st.metric("Turn #", metadata.get('conversation_turn', 1))
        
        # Update chat history
        chat_history.extend([
            {"role": "user", "content": query},
            {"role": "assistant", "content": response.get('response', '')}
        ])
        st.session_state.chat_history = chat_history
        
        return response
        
    except Exception as e:
        st.error(f"Error processing query: {e}")
        return None


def display_admin_analytics(integration: CommonQuestionsIntegration):
    """Display admin analytics dashboard."""
    
    if st.sidebar.checkbox("📊 Show Analytics", value=False):
        with st.sidebar:
            st.markdown("---")
            display_question_metrics_sidebar()
        
        # Main analytics dashboard
        with st.expander("📈 Detailed Analytics Dashboard", expanded=False):
            insights = integration.display_analytics_dashboard()
            
            if insights:
                st.success("Analytics data loaded successfully!")
            else:
                st.info("No analytics data available yet. Start chatting to generate insights!")


def main():
    """Main application with integrated common questions system."""
    
    st.set_page_config(
        page_title="Noah's AI Assistant",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Noah's AI Assistant")
    st.markdown("Get to know Noah through AI-powered conversations!")
    
    # Initialize your existing systems (replace with actual initialization)
    # rag_engine = RagEngine()
    # memory_system = Memory()
    # role_router = RoleRouter()
    
    # For demo purposes, we'll use None (the system handles this gracefully)
    rag_engine = None
    memory_system = None
    role_router = None
    
    # Initialize common questions system
    integration = initialize_common_questions_system(
        rag_engine=rag_engine,
        memory_system=memory_system,
        role_router=role_router
    )
    
    # Role selection (your existing role selection UI)
    user_role = st.selectbox(
        "👤 Select your role:",
        [
            "Just looking around",
            "Hiring Manager (nontechnical)",
            "Hiring Manager (technical)",
            "Software Developer"
        ]
    )
    
    # Session ID (you might already have this)
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    
    # Display welcome section with common questions
    st.markdown("### 🚀 Getting Started")
    selected_question = display_welcome_section(integration, user_role)
    
    # Enhanced chat interface
    st.markdown("---")
    user_query = enhanced_chat_interface(integration, user_role)
    
    # Process query (from welcome questions or chat input)
    query_to_process = selected_question or user_query
    
    if query_to_process:
        # Add user message to chat
        with st.chat_message("user"):
            st.write(query_to_process)
        
        # Process and display response
        process_user_query(
            integration=integration,
            user_role=user_role,
            query=query_to_process,
            session_id=st.session_state.session_id
        )
        
        # Rerun to update the interface
        st.rerun()
    
    # Display chat history
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        
        for message in st.session_state.chat_history[-6:]:  # Show last 6 messages
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Admin analytics (optional)
    display_admin_analytics(integration)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "*This assistant uses advanced RAG technology to provide accurate, "
        "up-to-date information about Noah's background and projects.*"
    )


if __name__ == "__main__":
    main()
