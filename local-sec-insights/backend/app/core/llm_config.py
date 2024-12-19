from enum import Enum
from typing import Optional
from pydantic import BaseSettings

class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"

class LLMSettings(BaseSettings):
    PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_EMBEDDING_DIM: int = 4096
    
    # 保留OpenAI配置用于后续可能的切换
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_prefix = "LLM__"

llm_settings = LLMSettings() 