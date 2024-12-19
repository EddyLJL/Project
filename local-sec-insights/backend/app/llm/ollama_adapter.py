from typing import Any, List, Optional
from llama_index.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.embeddings import BaseEmbedding
from app.core.config import settings
import requests
import httpx
from pydantic import BaseModel, Field

class OllamaLLM(CustomLLM, BaseModel):
    """自定义 Ollama LLM 适配器"""
    
    base_url: str = Field(default_factory=lambda: settings.LLM.OLLAMA_BASE_URL)
    model: str = Field(default_factory=lambda: settings.LLM.OLLAMA_MODEL)
    
    def __init__(self, model: str = None, **kwargs) -> None:
        super().__init__(**kwargs)
        if model:
            self.model = model
        
    @property
    def metadata(self) -> LLMMetadata:
        """获取 LLM 元数据"""
        return LLMMetadata(
            context_window=4096,  # 根据实际模型调整
            num_output=1024,      # 根据需要调整
            model_name=self.model
        )
    
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """完成提示"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                **kwargs
            }
        )
        response.raise_for_status()
        
        return CompletionResponse(text=response.json()["response"])
    
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """流式完成提示"""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                **kwargs
            },
            stream=True
        )
        response.raise_for_status()
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                full_response += line.decode()
                
        return CompletionResponse(text=full_response)

class OllamaAdapter(BaseEmbedding, BaseModel):
    """Ollama Embedding 适配器"""
    
    model: str = Field(default_factory=lambda: settings.LLM.OLLAMA_MODEL)
    base_url: str = Field(default_factory=lambda: settings.LLM.OLLAMA_BASE_URL)
    dim: int = Field(default_factory=lambda: settings.LLM.OLLAMA_EMBEDDING_DIM)

    def _get_embedding(self, text: str) -> List[float]:
        """获取单个文本的嵌入向量"""
        response = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": self.model,
                "prompt": text
            },
            timeout=30.0
        )
        response.raise_for_status()
        embedding = response.json()["embedding"]
        # 截取前1536维度
        return embedding[:1536]

    def _get_text_embedding(self, text: str) -> List[float]:
        return self._get_embedding(text)
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_embedding(text)
        
    def _get_query_embedding(self, query: str) -> List[float]:
        return self._get_embedding(query)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_embedding(query)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量获取文本嵌入"""
        embeddings = []
        for text in texts:
            embedding = self._get_embedding(text)
            embeddings.append(embedding)
        return embeddings

class OllamaEmbedding(BaseModel):
    dim: int = Field(default=1536)  # 保持1536维度