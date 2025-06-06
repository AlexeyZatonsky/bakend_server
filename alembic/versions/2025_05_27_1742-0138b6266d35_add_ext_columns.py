"""add ext columns

Revision ID: 0138b6266d35
Revises: e4168cd38d83
Create Date: 2025-05-27 17:42:48.013527

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0138b6266d35'
down_revision = 'e4168cd38d83'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channels', sa.Column('preview_ext', postgresql.ENUM('PNG', 'JPEG', 'WEBP', 'SVG', name='image_extensions_enum'), nullable=True))
    op.add_column('courses', sa.Column('preview_ext', postgresql.ENUM('PNG', 'JPEG', 'WEBP', 'SVG', name='image_extensions_enum'), nullable=True))
    op.drop_column('courses', 'preview')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses', sa.Column('preview', sa.VARCHAR(length=1000), autoincrement=False, nullable=True))
    op.drop_column('courses', 'preview_ext')
    op.drop_column('channels', 'preview_ext')
    # ### end Alembic commands ###
