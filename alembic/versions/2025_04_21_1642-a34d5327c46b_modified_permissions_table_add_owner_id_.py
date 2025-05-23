"""modified permissions table, add owner_id to courses

Revision ID: a34d5327c46b
Revises: d3be26b6c840
Create Date: 2025-04-21 16:42:47.749112

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a34d5327c46b'
down_revision = 'd3be26b6c840'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'access_level_enum'
      ) THEN
        CREATE TYPE access_level_enum AS ENUM (
          'HIGH_MODERATOR', 'MODERATOR', 'STUDENT'
        );
      END IF;
    END
    $$;
    """)

    op.create_table(
        'permissions',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('course_id', sa.UUID(), nullable=False),
        sa.Column(
            'access_level',
            postgresql.ENUM(
                'HIGH_MODERATOR', 'MODERATOR', 'STUDENT',
                name='access_level_enum',
                create_type=False        # не трогать тип, он уже есть / был создан выше
            ),
            nullable=False
        ),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expiration_date', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'course_id'),
    )

    op.drop_table('users_permissions')

    op.add_column(
        'courses',
        sa.Column('owner_id', sa.UUID(), nullable=False)
    )
    op.create_foreign_key(
        None,
        'courses',
        'users',
        ['owner_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'courses', type_='foreignkey')
    op.drop_column('courses', 'owner_id')
    op.create_table('users_permissions',
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('course_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('access_level', postgresql.ENUM('HIGH_MODERATOR', 'MODERATOR', 'STUDENT', name='access_level_enum'), autoincrement=False, nullable=False),
    sa.Column('expiration_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('granted_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], name='users_permissions_course_id_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='users_permissions_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'course_id', name='users_permissions_pkey')
    )
    op.drop_table('permissions')
    # ### end Alembic commands ###
