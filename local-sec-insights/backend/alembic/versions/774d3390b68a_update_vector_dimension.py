"""update_vector_dimension

Revision ID: 774d3390b68a
Revises: 663b3fea3024
Create Date: 2024-12-19 01:25:32.966004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '774d3390b68a'
down_revision = '663b3fea3024'
branch_labels = None
depends_on = None


def upgrade():
    # 首先创建 vector 扩展
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # 然后创建表
    op.execute("""
    CREATE TABLE public.data_pg_vector_store (
        id uuid DEFAULT uuid_generate_v4() NOT NULL,
        text VARCHAR NOT NULL,
        metadata_ JSON,
        node_id VARCHAR NOT NULL,
        embedding VECTOR(1536),
        PRIMARY KEY (id)
    )
    """)

def downgrade():
    op.execute('DROP TABLE IF EXISTS public.data_pg_vector_store')
    op.execute('DROP EXTENSION IF EXISTS vector')