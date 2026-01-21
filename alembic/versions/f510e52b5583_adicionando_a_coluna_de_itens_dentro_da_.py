"""Adicionando a coluna de itens dentro da tabela de pedidos

Revision ID: f510e52b5583
Revises: 8ba060abca55
Create Date: 2026-01-13 19:16:10.797496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f510e52b5583'
down_revision: Union[str, Sequence[str], None] = '8ba060abca55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column(
            'status',
            existing_type=sa.String(),
            nullable=True
        )


def downgrade() -> None:
    with op.batch_alter_table('orders') as batch_op:
        batch_op.alter_column(
            'status',
            existing_type=sa.String(),
            nullable=False
        )
