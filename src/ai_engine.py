import os
from typing import Dict, List, Any, Optional
import openai
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback
import streamlit as st
import pandas as pd

class AIEngine:
    """Handles AI model interactions using OpenAI and LangChain"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
            st.stop()
        
        # Initialize OpenAI client
        openai.api_key = self.openai_api_key
        
        # Initialize LangChain ChatOpenAI
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=self.openai_api_key
        )
        
        # Track token usage for observability
        self.total_tokens_used = 0
        self.total_cost = 0.0
    
    def generate_response(self, user_query: str, system_prompt: str = "") -> str:
        """Generate AI response using LangChain"""
        
        try:
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.append(HumanMessage(content=user_query))
            
            # Generate response with token tracking
            with get_openai_callback() as cb:
                response = self.llm(messages)
                
                # Update usage tracking
                self.total_tokens_used += cb.total_tokens
                self.total_cost += cb.total_cost
                
                # Log usage for observability
                self._log_usage(cb)
            
            return response.content
            
        except Exception as e:
            st.error(f"Error generating AI response: {str(e)}")
            return self._get_fallback_response(user_query)
    
    def _log_usage(self, callback_data):
        """Log AI usage for observability"""
        usage_info = {
            "timestamp": str(pd.Timestamp.now()),
            "tokens_used": callback_data.total_tokens,
            "prompt_tokens": callback_data.prompt_tokens,
            "completion_tokens": callback_data.completion_tokens,
            "cost": callback_data.total_cost
        }
        
        # In a production environment, you'd log this to a proper logging service
        # For now, we'll just store it in session state for demonstration
        if 'ai_usage_logs' not in st.session_state:
            st.session_state.ai_usage_logs = []
        
        st.session_state.ai_usage_logs.append(usage_info)
    
    def _get_fallback_response(self, user_query: str) -> str:
        """Provide fallback response when AI fails"""
        fallback_responses = {
            "greeting": "Hello! I'm Noah's AI Assistant. How can I help you today?",
            "technical": "I'd be happy to help with technical questions. Could you provide more details?",
            "general": "I'm here to assist you. Could you please rephrase your question?",
            "error": "I apologize, but I'm having trouble processing your request right now. Please try again."
        }
        
        # Simple keyword matching for fallback
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ["hello", "hi", "hey", "greetings"]):
            return fallback_responses["greeting"]
        elif any(word in query_lower for word in ["code", "programming", "technical", "developer"]):
            return fallback_responses["technical"] 
        else:
            return fallback_responses["general"]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
            "average_tokens_per_request": self.total_tokens_used / max(1, len(st.session_state.get('ai_usage_logs', []))),
            "request_count": len(st.session_state.get('ai_usage_logs', []))
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.total_tokens_used = 0
        self.total_cost = 0.0
        if 'ai_usage_logs' in st.session_state:
            st.session_state.ai_usage_logs = []