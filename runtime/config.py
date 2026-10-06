from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELYRA_", extra="ignore")

    app_name: str = "ELYRA Edge AI Runtime"
    version: str = "1.0.0"
    env: str = "development"
    
    # Local Inference / Ollama
    ollama_base_url: str = "http://localhost:11434"
    default_local_model: str = "qwen2.5:3b"
    fallback_cloud_model: str = "llama-3.3-70b"
    cloud_api_url: str = "https://api.openai.com/v1"
    cloud_api_key: str = "optional-cloud-key"

    # Edge Memory Management
    max_context_tokens: int = 4096
    sliding_window_tokens: int = 2048
    memory_prune_threshold_pct: float = 0.85

    # Telemetry Sampling
    telemetry_interval_sec: float = 1.0
    anomaly_z_score_threshold: float = 2.5


settings = Settings()
