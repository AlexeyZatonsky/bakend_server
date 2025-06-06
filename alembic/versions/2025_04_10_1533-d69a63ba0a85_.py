"""empty message

Revision ID: d69a63ba0a85
Revises: 
Create Date: 2025-04-10 15:33:09.322051

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd69a63ba0a85'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('avatar', sa.String(length=1000), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('channels',
    sa.Column('id', sa.String(length=255), nullable=False),
    sa.Column('owner_id', sa.UUID(), nullable=False),
    sa.Column('avatar', sa.String(length=1000), nullable=True),
    sa.Column('subscribers_count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('secret_info',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('hashed_password', sa.String(length=256), nullable=False),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.Column('INN', sa.String(length=12), nullable=True),
    sa.Column('organization_name', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('INN'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('courses',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('channel_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('student_count', sa.Integer(), nullable=False),
    sa.Column('preview', sa.String(length=1000), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('courses_comments',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('text', sa.String(length=2000), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'course_id')
    )
    op.create_table('courses_structure',
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('structure', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('course_id')
    )
    op.create_table('users_permissions',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('course_id', sa.UUID(), nullable=False),
    sa.Column('access_level', postgresql.ENUM('HIGH_MODERATOR', 'MODERATOR', 'STUDENT', name='access_level_enum'), nullable=False),
    sa.Column('expiration_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'course_id')
    )
    op.create_table('video',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('course_id', sa.UUID(), nullable=True),
    sa.Column('channel_id', sa.String(length=255), nullable=False),
    sa.Column('preview', sa.String(length=1000), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('is_free', sa.Boolean(), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('timeline', sa.Integer(), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('video_comments',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('video_id', sa.UUID(), nullable=False),
    sa.Column('text', sa.String(length=2000), nullable=False),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'video_id')
    )
    op.create_table('video_metadatas',
    sa.Column('video_id', sa.UUID(), nullable=False),
    sa.Column('views', sa.Integer(), nullable=False),
    sa.Column('likes', sa.Integer(), nullable=False),
    sa.Column('dislikes', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('video_id')
    )
    op.create_table('video_tag',
    sa.Column('video_id', sa.UUID(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['video_id'], ['video.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('video_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('video_tag')
    op.drop_table('video_metadatas')
    op.drop_table('video_comments')
    op.drop_table('video')
    op.drop_table('users_permissions')
    op.drop_table('courses_structure')
    op.drop_table('courses_comments')
    op.drop_table('courses')
    op.drop_table('secret_info')
    op.drop_table('channels')
    op.drop_table('users')
    op.drop_table('tag')
    op.drop_table('category')
    # ### end Alembic commands ###
