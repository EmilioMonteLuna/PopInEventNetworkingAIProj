# Configuration Settings for Event Networking AI System
"""
Centralized configuration management using Pydantic settings.
Loads configuration from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Database Configuration
    database_url: str = "sqlite:///./event_networking.db"
    database_echo: bool = False  # Set to True for SQL query logging
    
    # Security
    secret_key: str = "event-networking-ai-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Configuration
    api_version: str = "v1"
    debug: bool = True
    
    # Machine Learning Model Settings
    min_similarity_threshold: float = 0.1
    max_recommendations: int = 10
    default_clustering_algorithm: str = "louvain"
    
    # Text Processing Settings
    tfidf_max_features: int = 1000
    tfidf_ngram_range_min: int = 1
    tfidf_ngram_range_max: int = 2
    
    # Clustering Settings
    similarity_threshold_for_edges: float = 0.3
    min_cluster_size: int = 2
    
    # Performance Settings
    max_attendees_per_event: int = 1000
    recommendation_cache_ttl: int = 300  # 5 minutes in seconds
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # LinkedIn API Configuration
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_redirect_uri: str = "http://localhost:8000/api/v1/linkedin/callback"
    
    # External Services (for future use)
    redis_url: Optional[str] = None
    tableau_server_url: Optional[str] = None
    
    # Email Settings (for notifications)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Feature Flags
    enable_recommendation_caching: bool = True
    enable_clustering: bool = True
    enable_analytics: bool = True
    enable_data_export: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def get_database_url(self) -> str:
        """
        Get the complete database URL with proper formatting
        """
        if self.database_url.startswith("sqlite"):
            # Ensure SQLite path is absolute
            if not os.path.isabs(self.database_url.replace("sqlite:///", "")):
                return f"sqlite:///{os.path.abspath(self.database_url.replace('sqlite:///', ''))}"
        return self.database_url
    
    def is_production(self) -> bool:
        """
        Check if running in production environment
        """
        return not self.debug
    
    def get_tfidf_config(self) -> dict:
        """
        Get TF-IDF vectorizer configuration
        """
        return {
            "max_features": self.tfidf_max_features,
            "ngram_range": (self.tfidf_ngram_range_min, self.tfidf_ngram_range_max),
            "stop_words": "english"
        }
    
    def get_clustering_config(self) -> dict:
        """
        Get clustering algorithm configuration
        """
        return {
            "algorithm": self.default_clustering_algorithm,
            "min_cluster_size": self.min_cluster_size,
            "similarity_threshold": self.similarity_threshold_for_edges
        }

# Global settings instance
settings = Settings()

# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    database_echo: bool = True
    log_level: str = "DEBUG"

class ProductionSettings(Settings):
    """Production environment settings"""
    debug: bool = False
    database_echo: bool = False
    log_level: str = "INFO"
    secret_key: str = "CHANGE-THIS-IN-PRODUCTION"

class TestingSettings(Settings):
    """Testing environment settings"""
    database_url: str = "sqlite:///./test_event_networking.db"
    debug: bool = True
    log_level: str = "DEBUG"

def get_settings() -> Settings:
    """
    Factory function to get settings based on environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()

# Export the configured settings
settings = get_settings()

# Configuration validation
def validate_settings():
    """
    Validate critical settings
    """
    if settings.is_production() and settings.secret_key == "CHANGE-THIS-IN-PRODUCTION":
        raise ValueError("Secret key must be changed in production environment")
    
    if settings.min_similarity_threshold < 0 or settings.min_similarity_threshold > 1:
        raise ValueError("Similarity threshold must be between 0 and 1")
    
    if settings.max_recommendations < 1 or settings.max_recommendations > 50:
        raise ValueError("Max recommendations must be between 1 and 50")

# Run validation on import
validate_settings()