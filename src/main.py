import streamlit as st
import time
import uuid
from datetime import datetime
from core.rag_engine import RagEngine
from core.memory import Memory
from agents.role_router import RoleRouter
from agents.response_formatter import ResponseFormatter
from analytics.supabase_analytics import supabase_analytics, UserInteractionData
from config.supabase_config import supabase_settings

ROLE_OPTIONS = [
    "Hiring Manager (nontechnical)",
    "Hiring Manager (technical)",
    "Software Developer",
    "Just looking around",
    "Looking to confess crush"
]

def init_state():
    if "role" not in st.session_state:
        st.session_state.role = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # list[dict(role="user"/"assistant", content=str)]
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

def main():
    init_state()
    
    # Validate Supabase configuration
    supabase_settings.validate_configuration()
    
    memory = Memory()
    rag_engine = RagEngine(supabase_settings)
    role_router = RoleRouter()
    response_formatter = ResponseFormatter()

    st.title("Noah's AI Assistant")

    # One-time role selection (persisted)
    if st.session_state.role is None:
        st.write("Hello, I am Noah’s AI Assistant. To better provide assistance, which best describes you?")
        st.session_state.role = st.selectbox("Select your role:", ROLE_OPTIONS)
        st.button("Confirm Role", on_click=lambda: None)
        st.stop()
    else:
        st.sidebar.markdown(f"**Active Role:** {st.session_state.role}")
        if st.sidebar.button("Change Role"):
            st.session_state.role = None
            st.stop()

    # Display prior messages
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Chat input (multi-turn)
    user_input = st.chat_input("Ask a question...")
    if user_input:
        # Start timing for analytics
        start_time = time.time()
        
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            # Route + format
            raw_response = role_router.route(
                st.session_state.role,
                user_input,
                memory,
                rag_engine,
                chat_history=st.session_state.chat_history
            )
            formatted = response_formatter.format(raw_response)
            
            # Calculate response time and token usage
            response_time = time.time() - start_time
            latency_ms = int(response_time * 1000)
            
            # Determine query type
            query_type = "general"
            if any(keyword in user_input.lower() for keyword in ["code", "implementation", "architecture"]):
                query_type = "technical"
            elif any(keyword in user_input.lower() for keyword in ["career", "experience", "background"]):
                query_type = "career"
            elif any(keyword in user_input.lower() for keyword in ["mma", "fight", "fighting"]):
                query_type = "mma"
            
            # Log interaction to Supabase analytics
            interaction_data = UserInteractionData(
                session_id=st.session_state.session_id,
                role_mode=st.session_state.role,
                query=user_input,
                answer=formatted,
                query_type=query_type,
                latency_ms=latency_ms,
                tokens_prompt=None,  # TODO: Extract from OpenAI response
                tokens_completion=None,  # TODO: Extract from OpenAI response
                success=True
            )
            
            supabase_analytics.log_interaction(interaction_data)
            
            # Append assistant message
            st.session_state.chat_history.append({"role": "assistant", "content": formatted})

            with st.chat_message("assistant"):
                st.markdown(formatted)
                
        except Exception as e:
            # Log failed interaction
            response_time = time.time() - start_time
            latency_ms = int(response_time * 1000)
            
            interaction_data = UserInteractionData(
                session_id=st.session_state.session_id,
                role_mode=st.session_state.role,
                query=user_input,
                answer=f"Error: {str(e)}",
                query_type="error",
                latency_ms=latency_ms,
                success=False
            )
            
            supabase_analytics.log_interaction(interaction_data)
            
            st.error(f"Sorry, I encountered an error: {str(e)}")

    # Supabase Analytics panel
    with st.expander("System Health", expanded=False):
        health_status = supabase_analytics.health_check()
        if health_status["status"] == "healthy":
            st.success("✅ Analytics system healthy")
            st.metric("Total Messages", health_status["total_messages"])
            st.metric("Recent (24h)", health_status["recent_messages_24h"])
        else:
            st.error("❌ Analytics system unhealthy")
            st.error(health_status.get("error", "Unknown error"))

    # Simple clear chat
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []

    # Special UI for Confession role
    if st.session_state.role == "Looking to confess crush":
        st.subheader("Anonymous / Named Confession")
        st.markdown("Provide a message. Name is optional. We store only what you submit. No hidden PII capture.")
        with st.form("confession_form"):
            name = st.text_input("Name (optional)")
            message = st.text_area("Your message", max_chars=500, help="Max 500 characters")
            consent = st.checkbox("I consent to storing this submitted content.", value=False)
            submitted = st.form_submit_button("Submit Confession")
        if submitted:
            if not consent:
                st.warning("Consent required to store the message.")
            elif not message.strip():
                st.warning("Message cannot be empty.")
            else:
                import csv, os, datetime
                os.makedirs("data", exist_ok=True)
                path = "data/confessions.csv"
                write_header = not os.path.exists(path)
                with open(path, "a", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    if write_header:
                        w.writerow(["timestamp", "name", "message", "consent"])
                    w.writerow([datetime.datetime.utcnow().isoformat(), name.strip(), message.strip(), "yes"])
                st.success("Confession stored. 💌")
        st.stop()

if __name__ == "__main__":
    main()