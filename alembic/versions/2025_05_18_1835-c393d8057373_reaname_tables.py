"""rename tables

Revision ID: 6857f4da7681
Revises: f125c0c9ff34
Create Date: 2025-05-18 18:28:17.047592
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6857f4da7681'
down_revision = 'f125c0c9ff34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Drop FKs pointing at the old tables
    op.drop_constraint('video_comments_video_id_fkey', 'video_comments', type_='foreignkey')
    op.drop_constraint('video_tag_video_id_fkey',   'video_tag',      type_='foreignkey')
    op.drop_constraint('video_metadatas_id_fkey',   'video_metadatas',type_='foreignkey')

    # 2) Rename the tables in place
    op.rename_table('category',    'categories')
    op.rename_table('tag',         'tags')
    op.rename_table('video',       'videos')
    op.rename_table('video_tag',   'video_tags')

    # 3) Re-create FKs against the new names
    op.create_foreign_key(
        'video_comments_video_id_fkey',
        'video_comments', 'videos',
        ['video_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'video_tags_video_id_fkey',
        'video_tags', 'videos',
        ['video_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'video_metadatas_id_fkey',
        'video_metadatas', 'videos',
        ['id'], ['id'],
        ondelete='CASCADE'
    )

    # (If you also renamed the ENUM types, you can do that here too.)


def downgrade() -> None:
    # Reverse: drop new FKs, rename back, re-create old FKs
    op.drop_constraint('video_metadatas_id_fkey',   'video_metadatas',type_='foreignkey')
    op.drop_constraint('video_tags_video_id_fkey',  'video_tags',     type_='foreignkey')
    op.drop_constraint('video_comments_video_id_fkey','video_comments',type_='foreignkey')

    op.rename_table('videos',     'video')
    op.rename_table('video_tags', 'video_tag')
    op.rename_table('tags',       'tag')
    op.rename_table('categories', 'category')

    op.create_foreign_key(
        'video_comments_video_id_fkey',
        'video_comments', 'video',
        ['video_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'video_tag_video_id_fkey',
        'video_tag', 'video',
        ['video_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'video_metadatas_id_fkey',
        'video_metadatas', 'video',
        ['id'], ['id'],
        ondelete='CASCADE'
    )
