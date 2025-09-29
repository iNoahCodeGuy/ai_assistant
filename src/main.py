from streamlit import st
from core.rag_engine import RagEngine
from core.memory import Memory
from agents.role_router import RoleRouter
from agents.response_formatter import ResponseFormatter
from analytics.metrics_collector import MetricsCollector
from config.settings import Settings

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

def main():
    init_state()
    settings = Settings()
    memory = Memory()
    rag_engine = RagEngine(settings)
    role_router = RoleRouter()
    response_formatter = ResponseFormatter()
    metrics_collector = MetricsCollector()

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
        # Append user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Metrics
        metrics_collector.log_interaction(st.session_state.role, user_input)

        # Route + format
        raw_response = role_router.route(
            st.session_state.role,
            user_input,
            memory,
            rag_engine,
            chat_history=st.session_state.chat_history  # pass history if router supports it
        )
        formatted = response_formatter.format(raw_response)

        # Append assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": formatted})

        with st.chat_message("assistant"):
            st.markdown(formatted)

    # Analytics panel
    with st.expander("Analytics", expanded=False):
        metrics_collector.display_metrics()

    # Simple clear chat
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []

if __name__ == "__main__":
    main()