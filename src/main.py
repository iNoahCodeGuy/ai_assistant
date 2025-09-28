from streamlit import st
from core.rag_engine import RagEngine
from core.memory import Memory
from agents.role_router import RoleRouter
from agents.response_formatter import ResponseFormatter
from analytics.metrics_collector import MetricsCollector
from config.settings import Settings

def main():
    # Initialize settings
    settings = Settings()
    
    # Initialize components
    memory = Memory()
    rag_engine = RagEngine(settings)
    role_router = RoleRouter()
    response_formatter = ResponseFormatter()
    metrics_collector = MetricsCollector()

    # Streamlit UI setup
    st.title("Noah's AI Assistant")
    
    # Role selection
    role = st.selectbox("Select your role:", ["Hiring Manager (nontechnical)", "Hiring Manager (technical)", "Software Developer", "Just looking around", "Looking to confess crush"])
    
    # User input
    user_input = st.text_input("Ask a question:")
    
    if st.button("Submit"):
        # Collect metrics
        metrics_collector.log_interaction(role, user_input)
        
        # Process input based on role
        response = role_router.route(role, user_input, memory, rag_engine)
        
        # Format response
        formatted_response = response_formatter.format(response)
        
        # Display response
        st.write(formatted_response)

    # Analytics panel
    if st.checkbox("Show Analytics"):
        metrics_collector.display_metrics()

if __name__ == "__main__":
    main()