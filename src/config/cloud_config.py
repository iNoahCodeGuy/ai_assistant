"""Cloud configuration management for Google Cloud Platform."""

import os
from typing import Optional
from google.cloud import secretmanager
from dataclasses import dataclass


@dataclass
class CloudConfig:
    """Google Cloud Platform configuration."""
    project_id: str
    region: str = "us-central1"
    
    # Database Configuration
    cloud_sql_instance: str = ""
    database_name: str = "noah_analytics"
    db_user: str = "analytics_user"
    
    # Vector AI Configuration
    vertex_ai_location: str = "us-central1"
    vector_search_index_endpoint: str = ""
    
    # Pub/Sub Configuration
    analytics_topic: str = "analytics-events"
    
    # Redis/Memorystore Configuration
    redis_host: str = ""
    redis_port: int = 6379
    
    # Secret Manager Configuration
    openai_secret_name: str = "openai-api-key"
    db_password_secret_name: str = "db-password"


class CloudSecretManager:
    """Secure secret management using Google Cloud Secret Manager."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()
    
    def get_secret(self, secret_name: str, version: str = "latest") -> str:
        """Retrieve a secret from Secret Manager."""
        try:
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/{version}"
            response = self.client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            # Fallback to environment variables for local development
            env_var = secret_name.upper().replace("-", "_")
            value = os.getenv(env_var)
            if not value:
                raise ValueError(f"Secret {secret_name} not found in Secret Manager or environment")
            return value
    
    def create_secret(self, secret_name: str, secret_value: str) -> str:
        """Create a new secret in Secret Manager."""
        parent = f"projects/{self.project_id}"
        
        # Create the secret
        secret = self.client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_name,
                "secret": {"replication": {"automatic": {}}},
            }
        )
        
        # Add the secret version
        version = self.client.add_secret_version(
            request={
                "parent": secret.name,
                "payload": {"data": secret_value.encode("UTF-8")},
            }
        )
        
        return version.name


class CloudSettings:
    """Enhanced settings with cloud integration."""
    
    def __init__(self):
        # Determine if running in cloud environment
        self.is_cloud_environment = self._detect_cloud_environment()
        
        # Initialize cloud configuration
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "noah-ai-assistant")
        self.cloud_config = CloudConfig(project_id=self.project_id)
        
        # Initialize secret manager if in cloud
        if self.is_cloud_environment:
            self.secret_manager = CloudSecretManager(self.project_id)
        else:
            self.secret_manager = None
        
        # Load configuration
        self._load_configuration()
    
    def _detect_cloud_environment(self) -> bool:
        """Detect if running in Google Cloud environment."""
        return (
            os.getenv("GAE_ENV") is not None or  # App Engine
            os.getenv("K_SERVICE") is not None or  # Cloud Run
            os.getenv("GOOGLE_CLOUD_PROJECT") is not None  # General GCP
        )
    
    def _load_configuration(self):
        """Load configuration from environment or Secret Manager."""
        # OpenAI Configuration
        if self.secret_manager:
            self.openai_api_key = self.secret_manager.get_secret("openai-api-key")
            self.db_password = self.secret_manager.get_secret("db-password")
        else:
            # Local development fallback
            from dotenv import load_dotenv
            load_dotenv()
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.db_password = os.getenv("DB_PASSWORD", "local_dev_password")
        
        # Model Configuration
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        
        # Database Configuration
        if self.is_cloud_environment:
            # Cloud SQL connection
            self.database_url = self._build_cloud_sql_url()
        else:
            # Local PostgreSQL for development
            self.database_url = os.getenv(
                "DATABASE_URL", 
                f"postgresql://postgres:{self.db_password}@localhost/noah_analytics_dev"
            )
        
        # Redis Configuration
        if self.is_cloud_environment:
            self.redis_url = f"redis://{self.cloud_config.redis_host}:{self.cloud_config.redis_port}"
        else:
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Vector Storage Configuration
        if self.is_cloud_environment:
            self.use_vertex_ai = True
            self.vertex_ai_project = self.project_id
            self.vertex_ai_location = self.cloud_config.vertex_ai_location
        else:
            self.use_vertex_ai = False
            # Keep local FAISS for development
            self.vector_store_path = "vector_stores/"
        
        # Legacy compatibility
        self.api_key = self.openai_api_key
        self.analytics_db = self.database_url
    
    def _build_cloud_sql_url(self) -> str:
        """Build Cloud SQL connection URL."""
        return (
            f"postgresql+psycopg2://{self.cloud_config.db_user}:{self.db_password}@"
            f"/{self.cloud_config.database_name}?"
            f"host=/cloudsql/{self.cloud_config.cloud_sql_instance}"
        )
    
    def validate_configuration(self) -> bool:
        """Validate that all required configuration is available."""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        if not self.database_url:
            raise ValueError("Database URL not configured")
        
        if self.is_cloud_environment:
            if not self.project_id:
                raise ValueError("Google Cloud project ID not configured")
        
        return True


# Global settings instance
cloud_settings = CloudSettings()