"""add OWNER permission in enum

Revision ID: 742c31a4b5e4
Revises: a34d5327c46b
Create Date: 2025-04-21 18:31:17.412911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '742c31a4b5e4'
down_revision = 'a34d5327c46b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE access_level_enum ADD VALUE 'OWNER';")

def downgrade() -> None:
    # 1) Создаём временный ENUM без 'OWNER'
    op.execute("""
        CREATE TYPE access_level_enum_old AS ENUM (
            'HIGH_MODERATOR',
            'MODERATOR',
            'STUDENT'
        );
    """)
    # 2) Переводим колонку permissions.access_level на новый тип
    op.execute("""
        ALTER TABLE permissions
        ALTER COLUMN access_level
        TYPE access_level_enum_old
        USING access_level::text::access_level_enum_old;
    """)
    # 3) Удаляем старый тип
    op.execute("DROP TYPE access_level_enum;")
    # 4) Переименовываем временный тип в оригинальный
    op.execute("ALTER TYPE access_level_enum_old RENAME TO access_level_enum;")