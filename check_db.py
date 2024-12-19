# 创建文件 check_db.py
import asyncio
from sqlalchemy import text
from app.db.session import SessionLocal

async def check_database():
    async with SessionLocal() as session:
        try:
            # 检查文档数量
            result = await session.execute(text("SELECT COUNT(*) FROM document"))
            doc_count = result.scalar()
            print(f"\nDocuments count: {doc_count}")
            
            # 检查向量存储数量
            result = await session.execute(text("SELECT COUNT(*) FROM data_pg_vector_store"))
            vector_count = result.scalar()
            print(f"Vector store entries: {vector_count}")
            
            # 检查每个文档的向量数量
            query = """
            SELECT d.id as document_id, 
                   d.url,
                   COUNT(v.id) as vector_count,
                   MIN(v.text) as sample_text
            FROM document d
            LEFT JOIN data_pg_vector_store v ON v.metadata_->>'db_document_id' = d.id::text
            GROUP BY d.id, d.url
            ORDER BY COUNT(v.id) DESC
            """
            result = await session.execute(text(query))
            rows = result.fetchall()
            total_vectors = 0
            print("\nDocument vector counts:")
            for row in rows:
                print(f"\nDocument {row[0]}")
                print(f"  URL: {row[1]}")
                print(f"  Vector count: {row[2]}")
                if row[2] > 0:
                    print(f"  Sample text: {row[3][:100]}...")
                total_vectors += row[2]
            
            if total_vectors > 0:
                print(f"\nFound total {total_vectors} vectors")
            else:
                print("\nNo vectors found!")
                
                # 如果没有找到向量，检查一些额外信息
                print("\nChecking vector store content:")
                result = await session.execute(text("""
                    SELECT id, text, metadata_->>'db_document_id' as doc_id 
                    FROM data_pg_vector_store 
                    LIMIT 5
                """))
                rows = result.fetchall()
                for row in rows:
                    print(f"\nVector ID: {row[0]}")
                    print(f"Document ID: {row[2]}")
                    print(f"Text: {row[1][:100]}...")
            
            await session.commit()
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(check_database())