"""empty message

Revision ID: e7da2811be7a
Revises: 8a6626650c94
Create Date: 2025-02-25 16:05:19.873194

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e7da2811be7a'
down_revision = '8a6626650c94'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channels',
    sa.Column('unique_name', sa.String(length=255), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('avatar', sa.String(length=1000), nullable=True),
    sa.Column('subscribers_count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('unique_name'),
    sa.UniqueConstraint('unique_name')
    )
    op.create_table('courses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('channel_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('student_count', sa.Integer(), nullable=True),
    sa.Column('preview', sa.String(length=1000), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.unique_name'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('courses_structure',
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('structutre', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('course_id')
    )
    op.create_table('users_permissions',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('access_level', postgresql.ENUM('HIGH_MODERATOR', 'MODERATOR', 'STUDENT', name='access_level_enum'), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'course_id')
    )
    op.create_table('video_metadatas',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('video_id', sa.UUID(), nullable=False),
    sa.Column('views', sa.Integer(), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('dislikes', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('channel')
    op.add_column('video', sa.Column('preview', sa.String(length=1000), nullable=False))
    op.add_column('video', sa.Column('url', sa.String(), nullable=False))
    op.add_column('video', sa.Column('is_free', sa.Boolean(), nullable=True))
    op.add_column('video', sa.Column('is_public', sa.Boolean(), nullable=True))
    op.add_column('video', sa.Column('course_id', sa.UUID(), nullable=True))
    op.add_column('video', sa.Column('channel_name', sa.String(length=255), nullable=False))
    op.add_column('video', sa.Column('timeline', sa.Integer(), nullable=True))
    op.drop_constraint('video_user_id_fkey', 'video', type_='foreignkey')
    op.drop_constraint('video_category_id_fkey', 'video', type_='foreignkey')
    op.create_foreign_key(None, 'video', 'channels', ['channel_name'], ['unique_name'], ondelete='CASCADE')
    op.create_foreign_key(None, 'video', 'courses', ['course_id'], ['id'], ondelete='CASCADE')
    op.drop_column('video', 'category_id')
    op.drop_column('video', 'path')
    op.drop_column('video', 'likes')
    op.drop_column('video', 'dislikes')
    op.drop_column('video', 'views')
    op.drop_column('video', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('video', sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False))
    op.add_column('video', sa.Column('views', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('video', sa.Column('dislikes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('video', sa.Column('likes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('video', sa.Column('path', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('video', sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'video', type_='foreignkey')
    op.drop_constraint(None, 'video', type_='foreignkey')
    op.create_foreign_key('video_category_id_fkey', 'video', 'category', ['category_id'], ['id'])
    op.create_foreign_key('video_user_id_fkey', 'video', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_column('video', 'timeline')
    op.drop_column('video', 'channel_name')
    op.drop_column('video', 'course_id')
    op.drop_column('video', 'is_public')
    op.drop_column('video', 'is_free')
    op.drop_column('video', 'url')
    op.drop_column('video', 'preview')
    op.create_table('channel',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='channel_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='channel_pkey')
    )
    op.drop_table('video_metadatas')
    op.drop_table('users_permissions')
    op.drop_table('courses_structure')
    op.drop_table('courses')
    op.drop_table('channels')
    # ### end Alembic commands ###
