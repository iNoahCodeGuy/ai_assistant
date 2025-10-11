"""
Vercel serverless function for chat API endpoint.
Executes LangGraph conversation flow and returns response.
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.flows.conversation_flow import run_conversation_flow
from src.flows.conversation_state import ConversationState
from src.core.rag_engine import RagEngine


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for /api/chat endpoint."""
    
    def do_POST(self):
        """Handle POST request with chat message."""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)
            
            # Validate required fields
            if 'query' not in data:
                self._send_error(400, "Missing required field: query")
                return
            
            # Extract parameters
            query = data.get('query')
            role = data.get('role', 'Just looking around')
            session_id = data.get('session_id', 'default')
            chat_history = data.get('chat_history', [])
            user_email = data.get('user_email')
            user_name = data.get('user_name')
            user_phone = data.get('user_phone')
            
            # Initialize RAG engine
            rag_engine = RagEngine()
            
            # Create conversation state
            state = ConversationState(
                role=role,
                query=query,
                chat_history=chat_history
            )
            
            # Add session_id and user context to extras
            state.stash('session_id', session_id)
            if user_email:
                state.stash('user_email', user_email)
            if user_name:
                state.stash('user_name', user_name)
            if user_phone:
                state.stash('user_phone', user_phone)
            
            # Run conversation flow
            result_state = run_conversation_flow(state, rag_engine, session_id=session_id)
            
            # Build response
            response = {
                'success': True,
                'answer': result_state.answer,
                'role': result_state.role,
                'session_id': result_state.fetch('session_id', session_id),
                'analytics': result_state.analytics_metadata,
                'actions_taken': [
                    action.get('type') for action in result_state.pending_actions
                ],
                'retrieved_chunks': len(result_state.retrieved_chunks)
            }
            
            # Send success response
            self._send_json(200, response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            self._send_error(400, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            logger.error(traceback.format_exc())
            self._send_error(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight request."""
        self._send_cors_headers()
        self.send_response(200)
        self.end_headers()
    
    def _send_json(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response with CORS headers."""
        self._send_cors_headers()
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, status_code: int, message: str):
        """Send error response."""
        self._send_json(status_code, {
            'success': False,
            'error': message
        })
    
    def _send_cors_headers(self):
        """Add CORS headers for cross-origin requests."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
