"""add extensions on video table

Revision ID: f125c0c9ff34
Revises: d05c712973c3
Create Date: 2025-05-18 18:17:12.947168

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f125c0c9ff34'
down_revision = 'd05c712973c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    video_extensions_enum = postgresql.ENUM(
        'MP4',
        name='video_extensions_enum'
    )
    video_extensions_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('video', sa.Column('video_ext', video_extensions_enum, nullable=False))



    op.add_column('video', sa.Column('user_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'video', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('video', 'url')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('video', sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'video', type_='foreignkey')
    op.drop_column('video', 'video_ext')
    op.drop_column('video', 'user_id')
    # ### end Alembic commands ###
