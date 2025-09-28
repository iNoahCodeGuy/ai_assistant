from streamlit import selectbox, session_state

def role_selector():
    roles = [
        "Hiring Manager (nontechnical)",
        "Hiring Manager (technical)",
        "Software Developer",
        "Just looking around",
        "Looking to confess crush"
    ]
    
    selected_role = selectbox("Hello, I am Noah's AI Assistant. To better provide assistance, which best describes you?", roles)
    
    # Store the selected role in session state for later use
    session_state.selected_role = selected_role

    return selected_role