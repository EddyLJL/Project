from typing import List
import asyncio
from tempfile import TemporaryDirectory
from pathlib import Path
from fire import Fire
import s3fs
from app.core.config import settings
import upsert_db_sec_documents
import download_sec_pdf
from download_sec_pdf import DEFAULT_CIKS, DEFAULT_FILING_TYPES
import seed_storage_context
import boto3
import os
from botocore.config import Config


def copy_to_s3(dir_path: str, s3_bucket: str = settings.S3_ASSET_BUCKET_NAME):
    """
    Copy all files in dir_path to S3.
    """
    s3 = s3fs.S3FileSystem(
        key=settings.AWS_KEY,
        secret=settings.AWS_SECRET,
        endpoint_url=settings.S3_ENDPOINT_URL,
    )

    if not (settings.RENDER or s3.exists(s3_bucket)):
        s3.mkdir(s3_bucket)

    s3.put(dir_path, s3_bucket, recursive=True)


def upload_to_s3(local_path: str, s3_key: str) -> str:
    """Upload a file to S3 and return the URL"""
    s3_client = boto3.client(
        's3',
        endpoint_url='http://localhost:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name='us-east-1',
        config=Config(
            retries = dict(
                max_attempts = 10
            )
        )
    )
    
    bucket_name = os.getenv('S3_ASSET_BUCKET_NAME', 'sec-insights-assets-local')
    
    try:
        print(f"Local file exists: {os.path.exists(local_path)}")
        print(f"Local file size: {os.path.getsize(local_path)}")
        print(f"Uploading {local_path} to s3://{bucket_name}/{s3_key}")
        s3_client.upload_file(local_path, bucket_name, s3_key)
        url = f"http://localhost:4566/{bucket_name}/{s3_key}"
        print(f"Uploaded {local_path} to {url}")
        return url
    except Exception as e:
        print(f"Error uploading {local_path} to S3: {e}")
        raise


async def async_seed_db(
    ciks: List[str] = DEFAULT_CIKS, filing_types: List[str] = DEFAULT_FILING_TYPES
):
    with TemporaryDirectory() as temp_dir:
        print("Downloading SEC filings")
        download_sec_pdf.main(
            output_dir=temp_dir,
            ciks=ciks,
            file_types=filing_types,
        )

        print("Copying downloaded SEC filings to S3")
        uploaded_files = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.pdf'):
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, os.path.join(temp_dir, "sec-edgar-filings"))
                    s3_key = f"sec-edgar-filings/{relative_path}"
                    url = upload_to_s3(local_path, s3_key)
                    uploaded_files.append((local_path, url))

        print("Upserting records of downloaded SEC filings into database")
        await upsert_db_sec_documents.async_upsert_documents_from_filings(
            url_base=settings.CDN_BASE_URL,
            doc_dir=temp_dir,
            uploaded_files=uploaded_files
        )

        print("Seeding storage context")
        await seed_storage_context.async_main_seed_storage_context()
        print(
            """
Done! 🏁
\t- SEC PDF documents uploaded to the S3 assets bucket ✅
\t- Documents database table has been populated ✅
\t- Vector storage table has been seeded with embeddings ✅
        """.strip()
        )


def seed_db(
    ciks: List[str] = DEFAULT_CIKS, filing_types: List[str] = DEFAULT_FILING_TYPES
):
    asyncio.run(async_seed_db(ciks, filing_types))


if __name__ == "__main__":
    Fire(seed_db)
