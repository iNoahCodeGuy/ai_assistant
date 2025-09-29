import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        
        # Legacy support
        self.api_key = self.openai_api_key  # For backward compatibility
        
        # Database Configuration
        self.db_connection_string = os.getenv("DB_CONNECTION_STRING")
        self.analytics_db = os.getenv("ANALYTICS_DB", "sqlite:///analytics.db")
        
        # File Paths
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "vector_stores/")
        self.career_kb_path = os.getenv("CAREER_KB_PATH", "data/career_kb.csv")
        self.code_index_path = os.getenv("CODE_INDEX_PATH", "vector_stores/code_index/")
        self.mma_kb_path = os.getenv("MMA_KB_PATH", "data/mma_kb.csv")
    
    def validate_api_key(self):
        """Validate that OpenAI API key is set."""
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."
            )
        return True

settings = Settings()