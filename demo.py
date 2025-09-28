import streamlit as st
import os
from typing import Dict, List, Any
from datetime import datetime
import random

# Mock AI Engine for demonstration
class MockAIEngine:
    """Mock AI engine for demonstration without OpenAI API key"""
    
    def __init__(self):
        self.total_tokens_used = 0
        self.total_cost = 0.0
    
    def generate_response(self, user_query: str, system_prompt: str = "") -> str:
        """Generate mock AI response"""
        
        # Track usage
        self.total_tokens_used += random.randint(50, 200)
        self.total_cost += random.uniform(0.001, 0.01)
        
        # Mock responses based on query content
        query_lower = user_query.lower()
        
        if "resume" in query_lower or "cv" in query_lower:
            return """**Noah's Resume Summary**

**Skills:** Python, JavaScript, AI/ML, Streamlit, LangChain
**Experience:** 3+ years in software development
**Key Projects:** 
- AI chatbot with role-based adaptation
- FAISS vector search implementation
- Streamlit applications for data visualization

**Strengths:** Strong problem-solving skills, excellent communication, quick learner"""
        
        elif "code" in query_lower or "programming" in query_lower:
            return """Here's an example of Noah's coding approach:

```python
def role_based_response(user_role, query):
    \"\"\"Generate role-specific AI response\"\"\"
    config = get_role_config(user_role)
    prompt = build_system_prompt(config)
    
    # Use AI engine to generate response
    response = ai_engine.generate(query, prompt)
    
    # Add role-specific enhancements
    return enhance_response(response, user_role)
```

This demonstrates clean, documented code with separation of concerns and role-based logic."""
        
        elif "mma" in query_lower or "fight" in query_lower:
            return """🥊 Speaking of fights, here's a fun fact: The UFC was founded in 1993, and the first event had no weight classes, time limits, or rules against eye gouging! 

Modern MMA is much safer with comprehensive rules and regulations. The sport has evolved into one of the most technical and athletic competitions in the world."""
        
        elif "crush" in query_lower or "anonymous" in query_lower:
            return """💕 This is a safe, anonymous space where you can share your thoughts without judgment. 

Whether you're nervous about expressing feelings, need advice, or just want to talk through emotions, I'm here to listen and provide supportive guidance.

Remember: Your privacy is protected, and there's no pressure to share more than you're comfortable with."""
        
        elif any(word in query_lower for word in ["hello", "hi", "hey"]):
            return f"""Hello! 👋 Welcome to Noah's AI Assistant!

I'm here to provide role-adapted responses based on your needs:
- **Hiring Managers**: Get résumé summaries and candidate insights
- **Technical Managers**: Access architecture details and stack information  
- **Developers**: Receive code examples and GitHub links
- **Casual Users**: Enjoy fun facts and entertainment
- **Crush Mode**: Share thoughts anonymously in a supportive space

What would you like to know?"""
        
        else:
            return f"""Thanks for your question! Based on the selected role and your query, I would provide tailored information including:

• Relevant context from Noah's background
• Role-appropriate technical depth
• Proper citations and references
• Additional resources when applicable

*Note: This is a demo response. With a real OpenAI API key, responses would be more dynamic and contextually aware.*"""
    
    def get_usage_stats(self) -> Dict[str, Any]:
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_cost": round(self.total_cost, 4),
            "average_tokens_per_request": round(self.total_tokens_used / max(1, len(st.session_state.get('messages', [])) // 2), 2),
            "request_count": len(st.session_state.get('messages', [])) // 2
        }

def initialize_session_state():
    """Initialize session state variables"""
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = MockAIEngine()
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = True

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
    
    # Demo mode notice
    st.info("🚀 **Demo Mode**: This is running without OpenAI API. Real deployment would use GPT models for dynamic responses.")

def render_role_selection():
    """Render role selection interface"""
    st.sidebar.header("Select Your Role")
    
    roles = {
        "nontechnical_hiring": "👔 Non-Technical Hiring Manager",
        "technical_manager": "🏗️ Technical Manager", 
        "developer": "💻 Developer",
        "casual": "😊 Casual User",
        "crush": "💕 Crush"
    }
    
    selected_role = st.sidebar.selectbox(
        "Choose your role to get tailored responses:",
        options=list(roles.keys()),
        format_func=lambda x: roles[x],
        index=None,
        placeholder="Select a role..."
    )
    
    if selected_role:
        if st.sidebar.button("Set Role", type="primary"):
            st.session_state.role = selected_role
            st.rerun()
    
    if st.session_state.role:
        st.sidebar.success(f"Current role: {roles[st.session_state.role]}")
        if st.sidebar.button("Change Role"):
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()

def render_role_info():
    """Render role-specific information"""
    if not st.session_state.role:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Role Features")
        st.sidebar.markdown("""
        **👔 Non-Technical Hiring**: Résumé summaries, candidate insights
        
        **🏗️ Technical Manager**: Architecture details, stack analysis  
        
        **💻 Developer**: Code examples, GitHub links, file:line citations
        
        **😊 Casual**: Fun facts, entertainment, MMA fight links
        
        **💕 Crush**: Anonymous sharing, supportive environment
        """)
        return
        
    st.sidebar.markdown("---")
    
    role_info = {
        "nontechnical_hiring": {
            "title": "👔 Hiring Manager Mode",
            "description": "Get concise résumé summaries and candidate overviews with business-focused insights.",
            "features": ["Bullet-point summaries", "Skills highlighting", "Cultural fit assessment"]
        },
        "technical_manager": {
            "title": "🏗️ Technical Manager Mode", 
            "description": "Access detailed technical stack information and architecture insights.",
            "features": ["Architecture patterns", "Technology trade-offs", "Performance analytics links"]
        },
        "developer": {
            "title": "💻 Developer Mode",
            "description": "Get code examples, GitHub links, and detailed technical analysis.",
            "features": ["Code examples with syntax highlighting", "File:line citations", "GitHub repository links"]
        },
        "casual": {
            "title": "😊 Casual Mode",
            "description": "Enjoy fun facts, interesting content, and entertainment links!",
            "features": ["Fun facts", "MMA fight links", "Engaging conversation"]
        },
        "crush": {
            "title": "💕 Crush Mode",
            "description": "Share thoughts anonymously in a supportive environment.",
            "features": ["Anonymous sharing", "Privacy protection", "Emotional support"]
        }
    }
    
    info = role_info.get(st.session_state.role)
    if info:
        st.sidebar.markdown(f"### {info['title']}")
        st.sidebar.info(info['description'])
        
        with st.sidebar.expander("Features"):
            for feature in info['features']:
                st.markdown(f"• {feature}")

def render_usage_stats():
    """Render AI usage statistics"""
    if st.session_state.ai_engine and hasattr(st.session_state.ai_engine, 'get_usage_stats'):
        stats = st.session_state.ai_engine.get_usage_stats()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Usage Stats")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Requests", stats['request_count'])
            st.metric("Avg Tokens", stats['average_tokens_per_request'])
        
        with col2:
            st.metric("Total Tokens", stats['total_tokens_used'])
            st.metric("Cost", f"${stats['total_cost']}")

def enhance_response_for_role(base_response: str, role: str, query: str) -> Dict[str, Any]:
    """Enhance response based on role"""
    
    response_data = {
        "content": base_response,
        "citations": [],
        "extras": []
    }
    
    # Add role-specific enhancements
    if role == "nontechnical_hiring":
        if any(word in query.lower() for word in ["resume", "candidate", "hire"]):
            response_data["citations"] = [
                "📄 noah_resume.pdf:1-10 - Professional summary",
                "📄 noah_resume.pdf:15-25 - Technical skills section"
            ]
    
    elif role == "technical_manager":
        response_data["citations"] = [
            "🏗️ Architecture documentation - System design patterns",
            "📊 Performance metrics - Scalability analysis"
        ]
        response_data["extras"].append({
            "type": "link",
            "label": "View Performance Dashboard 📊",
            "url": "https://example.com/performance-dashboard"
        })
    
    elif role == "developer":
        response_data["citations"] = [
            "💻 [app.py:1-50](https://github.com/iNoahCodeGuy/NoahsAIAssistant-/blob/main/app.py#L1-L50) - Main application",
            "💻 [src/role_handler.py:45-80](https://github.com/iNoahCodeGuy/NoahsAIAssistant-/blob/main/src/role_handler.py#L45-L80) - Role logic"
        ]
        response_data["extras"].append({
            "type": "link",
            "label": "View on GitHub 🔗",
            "url": "https://github.com/iNoahCodeGuy/NoahsAIAssistant-"
        })
    
    elif role == "casual":
        response_data["extras"].append({
            "type": "link",
            "label": "Watch Epic MMA Fight! 🥊",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        })
    
    elif role == "crush":
        response_data["content"] += "\n\n💕 *This conversation is completely private and anonymous.*"
    
    return response_data

def render_chat_interface():
    """Render the main chat interface"""
    if not st.session_state.role:
        st.markdown("### 🎯 Welcome to Noah's AI Assistant!")
        st.markdown("Please select your role from the sidebar to get started and receive tailored responses.")
        
        # Show example interactions
        st.markdown("### 💡 Example Interactions by Role")
        
        examples = {
            "👔 Hiring Manager": "Tell me about Noah's background and qualifications",
            "🏗️ Technical Manager": "Explain Noah's technical architecture approach",  
            "💻 Developer": "Show me some of Noah's code examples",
            "😊 Casual": "Tell me something fun about Noah",
            "💕 Crush": "I want to share something anonymously"
        }
        
        for role, example in examples.items():
            with st.expander(f"{role} Example"):
                st.code(example)
        
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show citations if available
            if message.get("citations"):
                with st.expander("📚 Sources & Citations"):
                    for citation in message["citations"]:
                        st.markdown(f"- {citation}")
            
            # Show extras (links, etc.)
            if message.get("extras"):
                for extra in message["extras"]:
                    if extra["type"] == "link":
                        st.link_button(extra["label"], extra["url"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything!"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Generate base response
                base_response = st.session_state.ai_engine.generate_response(prompt)
                
                # Enhance for role
                enhanced = enhance_response_for_role(base_response, st.session_state.role, prompt)
                
                # Display response
                st.markdown(enhanced["content"])
                
                # Display citations
                if enhanced["citations"]:
                    with st.expander("📚 Sources & Citations"):
                        for citation in enhanced["citations"]:
                            st.markdown(f"- {citation}")
                
                # Display extras
                if enhanced["extras"]:
                    for extra in enhanced["extras"]:
                        if extra["type"] == "link":
                            st.link_button(extra["label"], extra["url"])
                
                # Add to message history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": enhanced["content"],
                    "citations": enhanced["citations"],
                    "extras": enhanced["extras"]
                })

def main():
    """Main application function"""
    setup_page()
    initialize_session_state()
    
    # Sidebar
    render_role_selection()
    render_role_info()
    render_usage_stats()
    
    # Main chat interface
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by OpenAI, LangChain, and FAISS | Built with ❤️ by Noah*")

if __name__ == "__main__":
    main()