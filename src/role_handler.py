from typing import Dict, List, Any, Optional
import streamlit as st
from datetime import datetime
import random

class RoleHandler:
    """Handles role-specific response generation and formatting"""
    
    def __init__(self, role: str):
        self.role = role
        self.role_configs = {
            "nontechnical_hiring": {
                "persona": "professional hiring manager",
                "style": "concise and business-focused",
                "focus": "candidate evaluation and résumé summaries"
            },
            "technical_manager": {
                "persona": "technical team lead",
                "style": "detailed technical explanations",
                "focus": "technology stacks, architecture, and code quality"
            },
            "developer": {
                "persona": "software engineer",
                "style": "code-heavy with examples",
                "focus": "implementation details, code examples, and best practices"
            },
            "casual": {
                "persona": "friendly companion",
                "style": "fun and engaging",
                "focus": "interesting facts and entertainment"
            },
            "crush": {
                "persona": "confidential friend",
                "style": "supportive and understanding",
                "focus": "emotional support and anonymous sharing"
            }
        }
    
    def generate_response(self, user_query: str, ai_engine, data_loader) -> Dict[str, Any]:
        """Generate role-specific response to user query"""
        
        # Get role configuration
        config = self.role_configs.get(self.role, self.role_configs["casual"])
        
        # Build role-specific prompt
        system_prompt = self._build_system_prompt(config)
        
        # Generate base response using AI engine
        base_response = ai_engine.generate_response(user_query, system_prompt)
        
        # Add role-specific enhancements
        enhanced_response = self._enhance_response(base_response, user_query, data_loader)
        
        return enhanced_response
    
    def _build_system_prompt(self, config: Dict[str, str]) -> str:
        """Build system prompt based on role configuration"""
        
        base_prompt = f"""You are Noah's AI Assistant acting as a {config['persona']}. 
        Your communication style should be {config['style']} and focus on {config['focus']}.
        
        Always provide helpful, accurate information while maintaining the specified persona.
        """
        
        role_specific_prompts = {
            "nontechnical_hiring": """
            When discussing candidates or résumés:
            - Provide clear, jargon-free summaries
            - Focus on skills, experience, and cultural fit
            - Highlight key achievements and qualifications
            - Use bullet points for easy scanning
            """,
            "technical_manager": """
            When discussing technical topics:
            - Explain technology choices and trade-offs
            - Provide architectural insights
            - Include performance and scalability considerations
            - Reference industry best practices
            - Always include relevant citations when possible
            """,
            "developer": """
            When providing technical help:
            - Include code examples with proper syntax highlighting
            - Provide file:line citations when referencing code
            - Include GitHub repository links when relevant
            - Explain implementation details thoroughly
            - Suggest alternative approaches
            """,
            "casual": """
            Keep responses:
            - Light-hearted and engaging
            - Include fun facts when relevant
            - Use emojis appropriately
            - Make learning enjoyable
            """,
            "crush": """
            Be:
            - Supportive and non-judgmental
            - Respectful of privacy and anonymity
            - Encouraging and understanding
            - Professional while being friendly
            """
        }
        
        return base_prompt + role_specific_prompts.get(self.role, "")
    
    def _enhance_response(self, base_response: str, user_query: str, data_loader) -> Dict[str, Any]:
        """Add role-specific enhancements to base response"""
        
        response_data = {
            "content": base_response,
            "citations": [],
            "extras": []
        }
        
        # Add role-specific enhancements
        if self.role == "nontechnical_hiring":
            response_data = self._enhance_hiring_response(response_data, user_query)
        
        elif self.role == "technical_manager":
            response_data = self._enhance_technical_manager_response(response_data, user_query, data_loader)
        
        elif self.role == "developer":
            response_data = self._enhance_developer_response(response_data, user_query, data_loader)
        
        elif self.role == "casual":
            response_data = self._enhance_casual_response(response_data, user_query)
        
        elif self.role == "crush":
            response_data = self._enhance_crush_response(response_data, user_query)
        
        return response_data
    
    def _enhance_hiring_response(self, response_data: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Enhance response for non-technical hiring managers"""
        
        # Add résumé-related citations if query mentions résumé/CV
        if any(word in user_query.lower() for word in ["resume", "résumé", "cv", "candidate"]):
            response_data["citations"].extend([
                "Based on standard industry hiring practices",
                "Reference: Common résumé evaluation criteria"
            ])
        
        return response_data
    
    def _enhance_technical_manager_response(self, response_data: Dict[str, Any], user_query: str, data_loader) -> Dict[str, Any]:
        """Enhance response for technical managers"""
        
        # Add technical stack explanations and citations
        response_data["citations"].extend([
            "Technical documentation references available",
            "Architecture patterns from industry standards"
        ])
        
        # Add mock analytics link for demonstration
        if "performance" in user_query.lower() or "analytics" in user_query.lower():
            response_data["extras"].append({
                "type": "link",
                "label": "View Performance Analytics",
                "url": "https://example.com/analytics"
            })
        
        return response_data
    
    def _enhance_developer_response(self, response_data: Dict[str, Any], user_query: str, data_loader) -> Dict[str, Any]:
        """Enhance response for developers"""
        
        # Add code citations
        if any(word in user_query.lower() for word in ["code", "function", "class", "method"]):
            response_data["citations"].extend([
                "app.py:15-25 - Main application setup",
                "src/role_handler.py:45-60 - Role configuration logic"
            ])
        
        # Add GitHub link
        response_data["extras"].append({
            "type": "link", 
            "label": "View on GitHub",
            "url": "https://github.com/iNoahCodeGuy/NoahsAIAssistant-"
        })
        
        return response_data
    
    def _enhance_casual_response(self, response_data: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Enhance response for casual users"""
        
        # Add fun facts
        fun_facts = [
            "🎯 Fun fact: The term 'chatbot' was coined in 1994!",
            "🤖 Did you know? AI assistants process millions of conversations daily!",
            "💡 Interesting: Machine learning algorithms can recognize patterns humans miss!",
            "🌟 Cool fact: Natural language processing helps computers understand human emotions!"
        ]
        
        if random.random() < 0.3:  # 30% chance to add a fun fact
            response_data["content"] += f"\n\n{random.choice(fun_facts)}"
        
        # Add MMA fight link as specified in requirements
        response_data["extras"].append({
            "type": "link",
            "label": "Watch Epic MMA Fight! 🥊",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Classic placeholder
        })
        
        return response_data
    
    def _enhance_crush_response(self, response_data: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Enhance response for crush users"""
        
        # Add anonymous confession support
        response_data["content"] += "\n\n💕 *Remember, this is a safe space for anonymous sharing. Your privacy is protected.*"
        
        # Add supportive messaging
        if any(word in user_query.lower() for word in ["nervous", "scared", "worried", "anxious"]):
            response_data["content"] += "\n\n🤗 It's completely normal to feel this way. Take your time and trust yourself."
        
        return response_data