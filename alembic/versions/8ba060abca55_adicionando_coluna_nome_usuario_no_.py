"""Adicionando coluna nome usuario no banco de pedidos

Revision ID: 8ba060abca55
Revises: 5ba1ac31ab46
Create Date: 2026-01-12 22:23:27.427172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ba060abca55'
down_revision: Union[str, Sequence[str], None] = '5ba1ac31ab46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Preenche registros antigos
    op.execute("""
        UPDATE orders
        SET nome_usuario = 'Sistema'
        WHERE nome_usuario IS NULL
    """)

    # 2. Garante NOT NULL usando batch (SQLite)
    with op.batch_alter_table("orders") as batch_op:
        batch_op.alter_column(
            "nome_usuario",
            existing_type=sa.String(),
            nullable=False
        )


def downgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.alter_column(
            "nome_usuario",
            existing_type=sa.String(),
            nullable=True
        )
