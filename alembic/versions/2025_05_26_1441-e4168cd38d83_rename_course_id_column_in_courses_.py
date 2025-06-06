"""rename course_id column in courses_structure

Revision ID: e4168cd38d83
Revises: 6857f4da7681
Create Date: 2025-05-26 14:41:09.795225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4168cd38d83'
down_revision = '6857f4da7681'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('video_categories',
    sa.Column('video_id', sa.UUID(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('video_id', 'category_id')
    )
    op.add_column('courses_structure', sa.Column('id', sa.UUID(), nullable=False))
    op.drop_constraint('courses_structure_course_id_fkey', 'courses_structure', type_='foreignkey')
    op.create_foreign_key(None, 'courses_structure', 'courses', ['id'], ['id'], ondelete='CASCADE')
    op.drop_column('courses_structure', 'course_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('courses_structure', sa.Column('course_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'courses_structure', type_='foreignkey')
    op.create_foreign_key('courses_structure_course_id_fkey', 'courses_structure', 'courses', ['course_id'], ['id'], ondelete='CASCADE')
    op.drop_column('courses_structure', 'id')
    op.drop_table('video_categories')
    # ### end Alembic commands ###
