from app.chat.engine import get_service_context, build_doc_id_to_index_map
from app.db.session import get_async_session
from app.api import crud
from fsspec.asyn import AsyncFileSystem
import logging
import asyncio

logger = logging.getLogger(__name__)

async def async_main_seed_storage_context(fs: AsyncFileSystem = None):
    """
    使用 Ollama 作为 embedding 模型来构建存储上下文
    """
    async for session in get_async_session():
        # 使用 session 进行操作
        service_context = get_service_context()
        
        # 获取所有文档
        docs = await crud.fetch_documents(session)
        
    # 为每个文档构建索引
    for doc in docs:
        try:
            await build_doc_id_to_index_map(service_context, [doc], fs=fs)
        except Exception as e:
            logger.error(f"Error building index for document {doc.id}: {e}")
            raise

def main_seed_storage_context():
    asyncio.run(async_main_seed_storage_context())

if __name__ == "__main__":
    Fire(main_seed_storage_context)
