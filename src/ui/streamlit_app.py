from streamlit import st
from components.chat_interface import ChatInterface
from components.role_selector import RoleSelector
from components.analytics_panel import AnalyticsPanel

def main():
    st.title("Noah's AI Assistant")
    
    # Role selection
    role = RoleSelector().select_role()
    
    # Chat interface
    chat_interface = ChatInterface(role)
    chat_interface.run_chat()
    
    # Analytics panel
    analytics_panel = AnalyticsPanel()
    analytics_panel.display_metrics()

if __name__ == "__main__":
    main()