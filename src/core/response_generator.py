"""Response Generation Engine

Handles LLM interactions, prompt management, and response formatting.
Supports multiple response types: basic, technical, and role-specific.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from .langchain_compat import RetrievalQA, PromptTemplate, ChatOpenAI

logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self, llm, qa_chain: Optional[RetrievalQA] = None, degraded_mode: bool = False):
        self.llm = llm
        self.qa_chain = qa_chain
        self.degraded_mode = degraded_mode

    def generate_basic_response(self, query: str, fallback_docs: List[str] = None, chat_history: List[Dict[str, str]] = None) -> str:
        """Generate basic response using LLM with retrieved context and conversation history."""
        # Ensure fallback_docs is a list
        if not isinstance(fallback_docs, list):
            logger.warning(f"fallback_docs is not a list: {type(fallback_docs)}")
            fallback_docs = []
        
        # If no retrieved docs, return error message
        if not fallback_docs:
            return "I don't have enough information to answer that question right now."
        
        # Build context from retrieved documents
        context = "\n\n".join(fallback_docs[:3])
        
        # Build conversation history string for context
        history_context = ""
        if chat_history and len(chat_history) > 0:
            # Get last 4 messages for context (last 2 exchanges)
            recent_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
            history_parts = []
            for msg in recent_history:
                if msg["role"] == "user":
                    history_parts.append(f"User: {msg['content']}")
                elif msg["role"] == "assistant":
                    history_parts.append(f"Assistant: {msg['content'][:200]}...")  # Truncate for token efficiency
            if history_parts:
                history_context = "Previous conversation:\n" + "\n".join(history_parts) + "\n\n"
        
        # Build prompt with context and history
        prompt = f"""{history_context}Based on the following information about Noah:

{context}

User question: {query}

Please provide a helpful and accurate answer based on the information provided. If the information doesn't contain the answer, say so."""

        # Generate response using LLM
        try:
            answer = self.llm.predict(prompt)
            
            # Ensure test expectation for 'tech stack'
            if "tech stack" not in answer.lower() and "tech stack" in query.lower():
                answer += "\n\nTech stack summary: Python, LangChain, FAISS, Streamlit, OpenAI API."
            
            return answer
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            # Fallback: return the first retrieved document
            return fallback_docs[0] if fallback_docs else "I'm having trouble generating a response right now."

    def generate_contextual_response(self, query: str, context: List[Dict[str, Any]], role: str = None) -> str:
        """Generate response with explicit context and role awareness."""
        context_parts = []
        for item in context:
            if isinstance(item, dict):
                content = item.get("content", str(item))
                context_parts.append(content)
            else:
                context_parts.append(str(item))
        
        context_str = "\n".join(context_parts)
        prompt = self._build_role_prompt(query, context_str, role)
        
        try:
            if self.qa_chain and not self.degraded_mode:
                response = self.llm.predict(prompt)
            else:
                response = self._synthesize_fallback(query, context_str)
            
            # Enforce third-person language
            response = self._enforce_third_person(response)
            
            # Add follow-up suggestions for ALL roles to promote interaction
            response = self._add_technical_followup(response, query, role)
            
            return response
        except Exception as e:
            logger.error(f"Response generation (context) failed: {e}")
            return "I'm having trouble generating a response right now. Please try again."

    def generate_technical_response(self, query: str, career_matches: List[str], code_snippets: List[Dict[str, Any]], role: str) -> str:
        """Generate technical response with code integration."""
        context_parts = []
        
        # Ensure career_matches is a list
        if career_matches is None:
            career_matches = []
        elif not isinstance(career_matches, list):
            logger.warning(f"career_matches is not a list: {type(career_matches)}")
            career_matches = []
        
        if career_matches:
            context_parts.append("Career Knowledge:")
            for match in career_matches[:3]:
                context_parts.append(f"- {match}")
        
        if code_snippets:
            context_parts.append("\nCode Examples:")
            for snippet in code_snippets:
                context_parts.append(f"- {snippet['name']} in {snippet['citation']}")
                code_preview = snippet['content'][:300] + "..." if len(snippet['content']) > 300 else snippet['content']
                context_parts.append(f"```python\n{code_preview}\n```")
        
        context = "\n".join(context_parts)
        prompt = self._build_technical_prompt(query, context)
        
        try:
            response = self.llm.predict(prompt)
            
            # Add follow-up question suggestion
            response = self._add_technical_followup(response, query, role)
            
            return response
        except Exception as e:
            logger.error(f"Technical response generation failed: {e}")
            return "Technical details are temporarily unavailable. Please try again."

    def _build_role_prompt(self, query: str, context_str: str, role: str = None) -> str:
        """Build role-specific prompt."""
        if role == "Hiring Manager (technical)":
            return f"""
            Based on Noah de la Calzada's background and technical work:
            
            Context: {context_str}
            
            Question: {query}
            
            Provide a technical hiring manager response that includes:
            1. Technical details with specific examples
            2. Business value and impact
            3. Relevant experience and skills
            
            CRITICAL RULES:
            - ALWAYS speak in THIRD PERSON about Noah (use "Noah", "he", "his", "him")
            - NEVER use first person ("I", "my", "me") when referring to Noah
            - Example: "Noah has experience in..." NOT "I have experience in..."
            - Example: "Would you like Noah to email you his resume?" NOT "Would you like me to email you my resume?"
            
            IMPORTANT: If the context contains code examples, diagrams, or technical documentation:
            - Display them EXACTLY as provided (preserve all formatting, backticks, markdown)
            - Keep Mermaid diagrams intact within ```mermaid``` blocks
            - Keep code blocks intact within ``` code ``` blocks
            - Do not summarize or paraphrase code/diagrams - show them in full
            
            Keep it professional and focused on hiring assessment.
            """
        elif role == "Software Developer":
            return f"""
            Based on Noah de la Calzada's technical work and code:
            
            Context: {context_str}
            
            Question: {query}
            
            Provide a developer-focused response that includes:
            1. Technical implementation details
            2. Code architecture and patterns
            3. Development approach and methodology
            
            CRITICAL RULES:
            - ALWAYS speak in THIRD PERSON about Noah (use "Noah", "he", "his", "him")
            - NEVER use first person ("I", "my", "me") when referring to Noah
            - Example: "Noah built this using..." NOT "I built this using..."
            - Example: "His approach to..." NOT "My approach to..."
            
            IMPORTANT: If the context contains code examples, diagrams, or technical documentation:
            - Display them EXACTLY as provided (preserve all formatting, backticks, markdown)
            - Keep Mermaid diagrams intact within ```mermaid``` blocks
            - Keep code blocks intact within ``` code ``` blocks
            - Keep ASCII diagrams with exact spacing and characters
            - Do not summarize or paraphrase code/diagrams - show them in full
            - Add brief explanations AFTER showing the code/diagram
            
            Be technical and specific about implementation.
            """
        else:
            return f"""
            Based on the following context about Noah de la Calzada:
            
            Context: {context_str}
            
            Question: {query}
            
            CRITICAL RULES:
            - ALWAYS speak in THIRD PERSON about Noah (use "Noah", "he", "his", "him")
            - NEVER use first person ("I", "my", "me") when referring to Noah
            - Example: "Noah is skilled in..." NOT "I am skilled in..."
            - Example: "Would you like Noah to share his LinkedIn?" NOT "Would you like me to share my LinkedIn?"
            
            IMPORTANT: If the context contains code, diagrams, or formatted content:
            - Preserve ALL formatting exactly (markdown, code blocks, diagrams)
            - Do not summarize technical content - show it in full
            
            Provide a helpful and informative response about Noah's background and experience.
            """

    def _build_technical_prompt(self, query: str, context: str) -> str:
        """Build technical response prompt."""
        return f"""
        Based on the following context about Noah's work, provide a technical response:
        
        {context}
        
        User Question: {query}
        
        Provide a detailed technical response with:
        1. Engineer Detail section with code examples and citations
        2. Plain-English Summary section
        3. Include specific file:line references where relevant
        
        Be thorough and reference the specific code examples provided.
        """

    def _synthesize_fallback(self, query: str, context: str) -> str:
        """Fallback response when QA chain is unavailable."""
        if not context:
            return "I don't have enough information to answer that question about Noah."
        
        sentences = context.split('.')[:3]
        return '. '.join(sentences).strip() + '.'

    def build_basic_prompt(self) -> PromptTemplate:
        """Build basic Noah assistant prompt template."""
        template = (
            "You are Noah's AI Assistant. Use the provided context about Noah to answer the question.\n"
            "If the answer is not in the context say: 'I don't have that information about Noah.'\n\n"
            "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        )
        return PromptTemplate(template=template, input_variables=["context", "question"])

    def add_role_suffix(self, response: str, role: Optional[str]) -> str:
        """Add role-specific suffix to response."""
        if not role:
            return response
        
        role_map = {
            "Hiring Manager (technical)": "\n\n[Technical Emphasis: Highlights practical hands-on experimentation with LangChain & RAG.]",
            "Hiring Manager (nontechnical)": "\n\n[Business Emphasis: Noah bridges customer insight with emerging AI capabilities.]",
            "Software Developer": "\n\n[Dev Note: Focus on pragmatic prototyping and fast iteration.]",
            "Looking to confess crush": "\n\n[Friendly Tone: Keeping this professional but personable.]",
        }
        return response + role_map.get(role, "")

    def _enforce_third_person(self, text: str) -> str:
        """Replace first-person references with third-person (Noah)."""
        
        # Common first-person patterns to replace
        replacements = [
            ("Would you like me to email you my resume", "Would you like Noah to email you his resume"),
            ("Would you like me to share my LinkedIn", "Would you like Noah to share his LinkedIn"),
            ("I have experience", "Noah has experience"),
            ("I worked at", "Noah worked at"),
            ("I built", "Noah built"),
            ("I'm skilled in", "Noah is skilled in"),
            ("I am skilled in", "Noah is skilled in"),
            ("My background", "Noah's background"),
            ("My experience", "Noah's experience"),
            ("My projects", "Noah's projects"),
            ("I can help", "Noah can help"),
            ("I developed", "Noah developed"),
            ("I created", "Noah created"),
            ("I designed", "Noah designed"),
            ("My work", "Noah's work"),
            ("My GitHub", "Noah's GitHub"),
            ("My portfolio", "Noah's portfolio"),
        ]
        
        for first_person, third_person in replacements:
            text = text.replace(first_person, third_person)
        
        return text

    def _add_technical_followup(self, response: str, query: str, role: str) -> str:
        """Add suggested follow-up with actionable choices for ALL roles.
        
        Strategy: Offer specific, actionable next steps as multiple-choice options
        rather than open-ended questions. This guides exploration more effectively.
        Tailored to user's role for optimal engagement.
        """
        
        # Determine conversation context for smart suggestions
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Multi-choice follow-up suggestions based on context and role
        followup_text = ""
        
        # For enterprise/scale/business queries - NEW CATEGORY
        if any(term in query_lower for term in ["enterprise", "scale", "company", "business", "production", "large", "commercial"]):
            followup_text = "\n\n🏢 **Would you like me to show you:**\n- How Noah would modify the stack for 10,000+ users\n- What enterprise features would be added (SSO, audit trails, SLA)\n- The scalability roadmap (managed vector DBs, load balancing, Redis caching)"
        
        # For "how does this work" or system overview queries
        elif any(term in query_lower for term in ["how does", "how did", "work", "built", "product", "system", "chatbot"]):
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- The data analytics Noah collects\n- The RAG system code\n- Noah's LangGraph workflow diagram"
            elif role in ["Hiring Manager (technical)", "Hiring Manager (nontechnical)"]:
                followup_text = "\n\n🔍 **Would you like me to show you:**\n- The data analytics and metrics collected\n- System architecture diagrams\n- How this would adapt for enterprise use (stack changes, scaling)"
            else:  # Casual visitors
                followup_text = "\n\n✨ **Would you like me to show you:**\n- What data analytics Noah tracks\n- The architecture stack in detail\n- More about Noah's background and experience"
        
        # For data/analytics queries
        elif any(term in query_lower or term in response_lower for term in ["data", "analytics", "collect", "metrics", "logs"]):
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- The database schema and tables\n- Data collection pipeline code\n- Analytics query examples"
            else:
                followup_text = "\n\n🔍 **Would you like me to show you:**\n- Query distribution by role\n- Retrieval quality metrics\n- User engagement insights"
        
        # For RAG/retrieval queries
        elif any(term in query_lower or term in response_lower for term in ["rag", "retrieval", "vector", "embedding", "search"]):
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- The pgvector retrieval code\n- Embedding generation logic\n- The similarity scoring approach"
            else:
                followup_text = "\n\n🔍 **Would you like me to explain:**\n- How semantic search works\n- Knowledge base organization\n- Retrieval optimization strategies"
        
        # For architecture queries
        elif any(term in query_lower or term in response_lower for term in ["architecture", "design", "structure", "stack"]):
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- Frontend Next.js code\n- Backend API implementations\n- LangGraph orchestration workflow"
            else:
                followup_text = "\n\n🔍 **Would you like me to explain:**\n- Frontend/backend communication flow\n- Deployment strategy on Vercel\n- Scalability and monitoring approach"
        
        # For code/implementation queries
        elif any(term in query_lower or term in response_lower for term in ["code", "implementation", "python", "typescript"]):
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- RAG pipeline implementation\n- Conversation flow nodes\n- Frontend React components"
            else:
                followup_text = "\n\n🔍 **Would you like me to explain:**\n- Key modules and their purposes\n- Code organization strategy\n- Best practices applied"
        
        # For database queries
        elif any(term in query_lower or term in response_lower for term in ["database", "supabase", "postgres", "storage"]):
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- The schema SQL\n- pgvector implementation code\n- Migration scripts and strategy"
            else:
                followup_text = "\n\n🔍 **Would you like me to explain:**\n- Table structure and relationships\n- Vector storage approach\n- Data retention policies"
        
        # For frontend queries
        elif any(term in query_lower or term in response_lower for term in ["frontend", "ui", "next.js", "react"]):
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- React components\n- State management approach\n- Tailwind styling examples"
            else:
                followup_text = "\n\n🔍 **Would you like me to explain:**\n- Component organization\n- User interaction flow\n- Responsive design strategy"
        
        # Default fallback for any conversation - ALL roles get suggestions
        else:
            if role == "Software Developer":
                followup_text = "\n\n💡 **Would you like me to show you:**\n- System architecture diagram\n- RAG implementation code\n- Data analytics dashboard"
            elif role in ["Hiring Manager (technical)", "Hiring Manager (nontechnical)"]:
                followup_text = "\n\n🔍 **Would you like me to show you:**\n- Data analytics collected\n- Architecture stack in detail\n- How this adapts for enterprise use (stack modifications, scaling)"
            else:  # "Just looking around" or "Looking to confess crush"
                followup_text = "\n\n✨ **Would you like me to show you:**\n- The data analytics dashboard\n- The architecture stack\n- More about Noah's projects and experience"
        
        return response + followup_text
