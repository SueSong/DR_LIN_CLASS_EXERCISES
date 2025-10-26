"""
Configuration settings for Exercise 6 RAG Chatbot
Handles environment variables and application settings
"""

import os
from typing import List, Optional, Any, Dict
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    app_name: str = Field(default="RAG Chatbot", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    database_url: str = Field(
        default="postgresql+asyncpg://rag_user:rag_password_2024@localhost:5433/rag_chatbot",
        env="DATABASE_URL"
    )
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, env="DB_POOL_TIMEOUT")
    
    # =============================================================================
    # VECTOR DATABASE SETTINGS
    # =============================================================================
    chromadb_host: str = Field(default="localhost", env="CHROMADB_HOST")
    chromadb_port: int = Field(default=8000, env="CHROMADB_PORT")
    chromadb_collection_name: str = Field(default="rag_documents", env="CHROMADB_COLLECTION_NAME")
    
    # =============================================================================
    # REDIS SETTINGS
    # =============================================================================
    redis_url: str = Field(
        default="redis://rag_redis_2024@localhost:6380/0",
        env="REDIS_URL"
    )
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    enable_query_cache: bool = Field(default=True, env="ENABLE_QUERY_CACHE")
    enable_embedding_cache: bool = Field(default=True, env="ENABLE_EMBEDDING_CACHE")
    
    # =============================================================================
    # LLM API SETTINGS
    # =============================================================================
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_embedding_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # =============================================================================
    # EMBEDDING SETTINGS
    # =============================================================================
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    embedding_dimension: int = Field(default=384, env="EMBEDDING_DIMENSION")
    embedding_batch_size: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    use_openai_embeddings: bool = Field(default=False, env="USE_OPENAI_EMBEDDINGS")
    
    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================
    max_file_size: str = Field(default="50MB", env="MAX_FILE_SIZE")
    allowed_file_types: List[str] = Field(
        default=["pdf", "txt", "docx", "md"],
        env="ALLOWED_FILE_TYPES"
    )
    upload_directory: str = Field(default="./uploads", env="UPLOAD_DIRECTORY")
    temp_directory: str = Field(default="./temp", env="TEMP_DIRECTORY")
    
    # =============================================================================
    # RAG PIPELINE SETTINGS
    # =============================================================================
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    min_chunk_size: int = Field(default=100, env="MIN_CHUNK_SIZE")
    max_chunks_per_document: int = Field(default=1000, env="MAX_CHUNKS_PER_DOCUMENT")
    
    max_retrieved_chunks: int = Field(default=5, env="MAX_RETRIEVED_CHUNKS")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    rerank_top_k: int = Field(default=3, env="RERANK_TOP_K")
    
    max_response_length: int = Field(default=2000, env="MAX_RESPONSE_LENGTH")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    top_p: float = Field(default=0.9, env="TOP_P")
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    secret_key: str = Field(
        default="your_secret_key_here_change_in_production",
        env="SECRET_KEY"
    )
    jwt_secret_key: str = Field(
        default="your_jwt_secret_key_here",
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # =============================================================================
    # CORS SETTINGS
    # =============================================================================
    cors_origins: List[str] = Field(
        default=["*"],  # Allow all origins for student class
        env="CORS_ORIGINS"
    )
    
    # =============================================================================
    # PERFORMANCE SETTINGS
    # =============================================================================
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # =============================================================================
    # WEBSOCKET SETTINGS
    # =============================================================================
    enable_websocket: bool = Field(default=True, env="ENABLE_WEBSOCKET")
    websocket_url: str = Field(default="ws://localhost:8002/ws", env="WEBSOCKET_URL")
    
    # =============================================================================
    # MONITORING & AGENT CONTROL SETTINGS (Exercise 7)
    # =============================================================================
    enable_metrics: bool = Field(default=False, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    # Failure injection knobs
    fail_rate: float = Field(default=0.35, env="FAIL_RATE")
    inject_timeout_ms: int = Field(default=800, env="INJECT_TIMEOUT_MS")
    cache_hit_rate: float = Field(default=0.7, env="CACHE_HIT_RATE")

    # Budget & model
    budget_usd: float = Field(default=0.05, env="BUDGET_USD")
    model: str = Field(default="gpt-4o-mini", env="MODEL")

    # Retry & circuit breaker
    max_retries: int = Field(default=2, env="MAX_RETRIES")
    circuit_failures_threshold: int = Field(default=3, env="CIRCUIT_FAILURES_THRESHOLD")
    circuit_window_seconds: int = Field(default=60, env="CIRCUIT_WINDOW_SECONDS")
    circuit_cooldown_seconds: int = Field(default=60, env="CIRCUIT_COOLDOWN_SECONDS")

    # Prompt AB
    prompt_ab_v2_percent: float = Field(default=0.10, env="PROMPT_AB_V2_PERCENT")

    # Trading agent integration
    trading_agent_url: str = Field(default="http://localhost:8001", env="TRADING_AGENT_URL")
    
    # =============================================================================
    # VALIDATORS
    # =============================================================================
    
    @field_validator('cors_origins', mode='before')
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @field_validator('allowed_file_types', mode='before')
    def parse_allowed_file_types(cls, v):
        if isinstance(v, str):
            return [file_type.strip() for file_type in v.split(',')]
        return v
    
    @field_validator('max_file_size')
    def parse_max_file_size(cls, v):
        """Convert file size string to bytes"""
        if isinstance(v, str):
            v = v.upper()
            if v.endswith('MB'):
                return int(float(v[:-2]) * 1024 * 1024)
            elif v.endswith('KB'):
                return int(float(v[:-2]) * 1024)
            elif v.endswith('GB'):
                return int(float(v[:-2]) * 1024 * 1024 * 1024)
            else:
                return int(v)
        return v
    
    @field_validator('environment')
    def validate_environment(cls, v):
        allowed_envs = ['development', 'testing', 'staging', 'production']
        if v not in allowed_envs:
            raise ValueError(f'Environment must be one of: {allowed_envs}')
        return v
    
    @field_validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {allowed_levels}')
        return v.upper()
    
    # =============================================================================
    # COMPUTED PROPERTIES
    # =============================================================================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    @property
    def chromadb_url(self) -> str:
        """Get ChromaDB connection URL"""
        return f"http://{self.chromadb_host}:{self.chromadb_port}"
    
    @property
    def max_file_size_mb(self) -> float:
        """Get max file size in MB"""
        return self.max_file_size / (1024 * 1024)
    
    @property
    def rag_embedding_model(self) -> str:
        """Get the embedding model to use (prioritize OpenAI)"""
        return self.openai_embedding_model
    
    @property
    def max_chunks_per_query(self) -> int:
        """Get max chunks per query"""
        return self.max_retrieved_chunks
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary"""
        return {
            "url": self.database_url,
            "pool_size": self.db_pool_size,
            "max_overflow": self.db_max_overflow,
            "pool_timeout": self.db_pool_timeout,
        }
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration dictionary"""
        return {
            "openai": {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "embedding_model": self.openai_embedding_model,
            },
            "anthropic": {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
            },
            "generation": {
                "max_response_length": self.max_response_length,
                "temperature": self.temperature,
                "top_p": self.top_p,
            }
        }
    
    def get_rag_config(self) -> Dict[str, Any]:
        """Get RAG pipeline configuration dictionary"""
        return {
            "chunking": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "min_chunk_size": self.min_chunk_size,
                "max_chunks_per_document": self.max_chunks_per_document,
            },
            "retrieval": {
                "max_retrieved_chunks": self.max_retrieved_chunks,
                "similarity_threshold": self.similarity_threshold,
                "rerank_top_k": self.rerank_top_k,
            },
            "embedding": {
                "model": self.embedding_model,
                "dimension": self.embedding_dimension,
                "batch_size": self.embedding_batch_size,
                "use_openai": self.use_openai_embeddings,
            }
        }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
