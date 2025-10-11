"""Supabase configuration for Noah's AI Assistant.

This module replaces Google Cloud Platform services with Supabase:
- Cloud SQL PostgreSQL → Supabase Postgres (with pgvector extension)
- Cloud Storage → Supabase Storage
- Secret Manager → Environment variables
- Pub/Sub → Direct database writes (simpler architecture)

Environment Variables Required:
- SUPABASE_URL: Your Supabase project URL
- SUPABASE_SERVICE_ROLE_KEY: Service role key (for server-side operations)
- SUPABASE_ANON_KEY: Anonymous key (for client-side operations, optional)
- OPENAI_API_KEY: OpenAI API key for embeddings and chat
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()


@dataclass
class SupabaseConfig:
    """Supabase configuration settings.
    
    This replaces the CloudConfig from GCP implementation.
    All configuration is driven by environment variables for
    compatibility with both local development and Vercel deployment.
    """
    
    # Supabase connection
    url: str
    service_role_key: str
    anon_key: Optional[str] = None
    
    # Storage buckets
    public_bucket: str = "public"  # For images, public assets
    private_bucket: str = "private"  # For resumes, CSVs, KB data
    
    # Database settings
    database_name: str = "postgres"  # Default Supabase database
    
    # Vector search settings
    vector_dimensions: int = 1536  # OpenAI ada-002 embedding size
    similarity_threshold: float = 0.7  # Minimum similarity for retrieval
    top_k: int = 3  # Number of KB chunks to retrieve
    
    def __post_init__(self):
        """Validate required configuration."""
        if not self.url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.service_role_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required")


class SupabaseSettings:
    """Global settings manager for Supabase integration.
    
    Why this approach:
    - Centralized configuration management
    - Easy environment detection (local vs production)
    - Backward compatible with existing Settings pattern
    - Clear separation between Supabase config and application config
    """
    
    def __init__(self):
        """Initialize settings from environment variables.
        
        This works seamlessly in:
        - Local development (.env file)
        - Vercel deployment (environment variables panel)
        - Testing (mocked environment variables)
        """
        # Detect environment
        self.is_production = os.getenv("VERCEL_ENV") == "production"
        self.is_vercel = os.getenv("VERCEL") == "1"
        
        # Supabase configuration (strip whitespace to prevent header issues)
        self.supabase_config = SupabaseConfig(
            url=os.getenv("SUPABASE_URL", "").strip(),
            service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip(),
            anon_key=os.getenv("SUPABASE_ANON_KEY", "").strip() if os.getenv("SUPABASE_ANON_KEY") else None
        )
        
        # OpenAI configuration (strip to prevent "Illegal header value" errors)
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo").strip()
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002").strip()
        
        # External services (for Next.js API routes)
        self.resend_api_key = os.getenv("RESEND_API_KEY", "").strip()
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        self.twilio_from_number = os.getenv("TWILIO_FROM", "").strip()
        
        # Application settings
        self.youtube_fight_link = os.getenv(
            "YOUTUBE_FIGHT_LINK", 
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        
        # Legacy compatibility (for existing code that expects these attributes)
        self.api_key = self.openai_api_key
        self.career_kb_path = "data/career_kb.csv"  # Still used for initial data load
        self.vector_store_path = "vector_stores/"  # Deprecated but kept for compatibility
    
    def validate_api_key(self):
        """Validate that OpenAI API key is present and properly formatted.
        
        This replaces cloud_settings.validate_api_key() from GCP version.
        Also checks for common issues like trailing newlines that cause HTTP header errors.
        """
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."
            )
        
        # Check for newlines that cause "Illegal header value" errors
        if '\n' in self.openai_api_key or '\r' in self.openai_api_key:
            raise ValueError(
                "OpenAI API key contains newline characters. "
                "This causes 'Illegal header value' errors in HTTP requests. "
                "Check your environment variables for trailing newlines."
            )
        
        return True
    
    def validate_supabase(self):
        """Validate that Supabase configuration is complete.
        
        Call this before any Supabase operations to ensure proper setup.
        Also checks for common issues like trailing newlines.
        """
        try:
            # Check if config exists and is valid
            self.supabase_config  # This will raise ValueError if invalid
            
            # Check for newlines or other non-printable characters
            if '\n' in self.supabase_config.url or '\r' in self.supabase_config.url:
                raise ValueError(
                    "Supabase URL contains newline characters. "
                    "Check your environment variables for trailing newlines."
                )
            if '\n' in self.supabase_config.service_role_key or '\r' in self.supabase_config.service_role_key:
                raise ValueError(
                    "Supabase service role key contains newline characters. "
                    "Check your environment variables for trailing newlines."
                )
            
            return True
        except ValueError as e:
            raise ValueError(
                f"Supabase configuration incomplete: {e}. "
                "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your .env file."
            )
    
    def validate_configuration(self) -> bool:
        """Validate all required configuration.
        
        This replaces cloud_settings.validate_configuration() from GCP version.
        """
        self.validate_api_key()
        self.validate_supabase()
        return True


# Global settings instance
# This replaces 'cloud_settings' from the GCP implementation
supabase_settings = SupabaseSettings()


# Helper function to get Supabase client (lazy initialization)
_supabase_client = None

def get_supabase_client():
    """Get or create Supabase client instance.
    
    Why lazy initialization:
    - Client creation might fail if environment vars are missing
    - Tests can mock this function easily
    - Allows for client recycling/pooling in the future
    
    Returns:
        supabase.Client: Authenticated Supabase client
    
    Example:
        from config.supabase_config import get_supabase_client
        
        supabase = get_supabase_client()
        result = supabase.table('messages').select('*').execute()
    """
    global _supabase_client
    
    if _supabase_client is None:
        try:
            from supabase import create_client, Client
            
            config = supabase_settings.supabase_config
            _supabase_client = create_client(
                config.url,
                config.service_role_key
            )
        except ImportError:
            raise ImportError(
                "Supabase Python client not installed. "
                "Run: pip install supabase"
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to create Supabase client: {e}. "
                "Check your SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
            )
    
    return _supabase_client