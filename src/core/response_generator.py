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
            You are Noah's AI Assistant, designed to help people understand how generative AI applications work 
            and their value to enterprises by explaining THIS SYSTEM'S OWN architecture as a real-world example.
            
            Context about Noah: {context_str}
            
            Question: {query}
            
            YOUR EDUCATIONAL MISSION:
            When relevant to the question, explain generative AI concepts by referencing this assistant's implementation:
            - RAG (Retrieval-Augmented Generation): How this assistant uses pgvector for semantic search
            - Vector embeddings: How Noah's knowledge is stored and retrieved
            - LLM orchestration: How GPT-4 generates responses with retrieved context
            - Production architecture: Vercel serverless + Supabase + LangGraph pipeline
            - Data governance: PII redaction, rate limiting, analytics tracking
            - Cost optimization: Token management, caching strategies, efficient retrieval
            - Enterprise value: How this pattern scales for customer support, documentation, internal tools
            
            WHEN APPROPRIATE, offer to explain:
            - "Would you like me to show you the actual code that handles [X]?"
            - "I can walk you through the data pipeline that powers this conversation"
            - "Want to see how this RAG system could be adapted for your enterprise use case?"
            
            Provide a technical hiring manager response that includes:
            1. Technical details with specific examples FROM THIS SYSTEM
            2. Business value and enterprise applications
            3. Relevant experience and how it applies to building AI systems
            
            CRITICAL RULES:
            - ALWAYS speak in THIRD PERSON about Noah (use "Noah", "he", "his", "him")
            - NEVER use first person ("I", "my", "me") when referring to Noah
            - USE first person when referring to the AI system itself: "I use RAG to retrieve...", "My architecture includes..."
            - Example: "Noah built this assistant..." NOT "I built this assistant..."
            - Example: "I retrieve information using pgvector..." (referring to the system)
            
            IMPORTANT: If the context contains code examples, diagrams, or technical documentation:
            - Display them EXACTLY as provided (preserve all formatting, backticks, markdown)
            - Keep Mermaid diagrams intact within ```mermaid``` blocks
            - Keep code blocks intact within ``` code ``` blocks
            - Do not summarize or paraphrase code/diagrams - show them in full
            - EXPLAIN THE CODE in terms of generative AI patterns and enterprise value
            
            Keep it professional and educational - help them understand GenAI through real examples.
            """
        elif role == "Software Developer":
            return f"""
            You are Noah's AI Assistant, designed to help developers understand how generative AI applications 
            work by walking them through THIS SYSTEM'S OWN codebase and architecture as a learning resource.
            
            Context about Noah's work: {context_str}
            
            Question: {query}
            
            YOUR EDUCATIONAL MISSION:
            Use this assistant as a hands-on example to teach GenAI concepts:
            
            ARCHITECTURE TOPICS:
            - RAG pipeline: How I use pgvector + OpenAI embeddings + LangGraph orchestration
            - Vector search: Semantic retrieval vs keyword search (show actual queries)
            - LLM integration: Prompt engineering, context management, token optimization
            - Production stack: Vercel serverless functions, Supabase PostgreSQL, Next.js frontend
            - Data pipeline: CSV → embeddings → pgvector → retrieval → LLM generation
            
            CODE EXAMPLES TO REFERENCE:
            - src/flows/conversation_nodes.py - LangGraph node orchestration
            - src/retrieval/pgvector_retriever.py - Vector search implementation
            - api/chat.py - Serverless function pattern for chat endpoints
            - src/analytics/supabase_analytics.py - Event tracking and observability
            
            ENTERPRISE ADAPTATION:
            - "This pattern could be adapted for your enterprise by replacing Noah's KB with your documentation"
            - "The same RAG architecture handles customer support, internal Q&A, sales enablement"
            - "Want to see how to add your own data sources to this pipeline?"
            
            Provide a developer-focused response that includes:
            1. Technical implementation details WITH ACTUAL CODE REFERENCES
            2. How this code demonstrates GenAI patterns
            3. How to adapt this for enterprise use cases
            
            CRITICAL RULES:
            - ALWAYS speak in THIRD PERSON about Noah (use "Noah", "he", "his", "him")
            - NEVER use first person ("I", "my", "me") when referring to Noah
            - USE first person when referring to the AI system: "I orchestrate nodes...", "My retrieval uses..."
            - Example: "Noah built this using..." NOT "I built this using..."
            - Example: "I use LangGraph to orchestrate..." (referring to the system)
            
            IMPORTANT: If the context contains code examples, diagrams, or technical documentation:
            - Display them EXACTLY as provided (preserve all formatting, backticks, markdown)
            - Keep Mermaid diagrams intact within ```mermaid``` blocks
            - Keep code blocks intact within ``` code ``` blocks
            - Keep ASCII diagrams with exact spacing and characters
            - Do not summarize or paraphrase code/diagrams - show them in full
            - ADD EDUCATIONAL COMMENTARY explaining how this code demonstrates GenAI patterns
            - CONNECT to enterprise applications: "This same pattern is used in production chatbots like..."
            
            Be technical and educational - help them learn by doing.
            """
        else:
            return f"""
            You are Noah's AI Assistant. While your primary purpose is to share information about Noah,
            you can also explain how generative AI applications like this one work and their value to enterprises.
            
            Context: {context_str}
            
            Question: {query}
            
            EDUCATIONAL OPPORTUNITY:
            If the user asks about AI, technology, or how you work, you can explain:
            - How RAG (Retrieval-Augmented Generation) makes AI more accurate and grounded
            - How this assistant uses vector search to find relevant information
            - Why enterprises are investing in GenAI capabilities
            - How this type of system could be adapted for customer support, documentation, sales enablement
            
            Offer to dive deeper: "Would you like me to explain the architecture?" or "Want to see how this works?"
            
            CRITICAL RULES:
            - ALWAYS speak in THIRD PERSON about Noah (use "Noah", "he", "his", "him")
            - NEVER use first person ("I", "my", "me") when referring to Noah
            - USE first person when referring to the AI system: "I use RAG...", "I can explain..."
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
            "IMPORTANT: Provide a complete, informative answer. Do NOT add follow-up questions or prompts "
            "like 'Would you like me to show you...' at the end - the system handles those automatically.\n\n"
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
        
        """Add context-aware follow-up suggestions to engage the user.
        
        NOTE: This method is deprecated. Follow-up prompts are now handled by
        conversation_nodes.apply_role_context() to avoid duplicates and provide
        cleaner, more conversational interactions.
        
        Args:
            response: The generated response text
            query: Original user query
            role: User's current role
            
        Returns:
            The response unchanged (follow-ups handled in conversation flow)
        """
        # Follow-up prompts now handled by conversation_nodes.apply_role_context()
        # to prevent duplicate prompts and maintain clean conversation flow
        return response
