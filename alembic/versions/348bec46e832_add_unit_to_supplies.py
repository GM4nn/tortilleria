"""add unit to supplies

Revision ID: 348bec46e832
Revises: be7520d40658
Create Date: 2026-02-21 23:18:39.784864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '348bec46e832'
down_revision: Union[str, Sequence[str], None] = 'be7520d40658'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agregar columna unit a supplies con server_default para filas existentes
    with op.batch_alter_table('supplies') as batch_op:
        batch_op.add_column(sa.Column('unit', sa.String(50), nullable=False, server_default='kilos'))

    # Backfill: copiar unit de la compra mas reciente de cada supply
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT s.id, sp.unit
        FROM supplies s
        JOIN supply_purchases sp ON s.id = sp.supply_id
        WHERE sp.id = (
            SELECT sp2.id FROM supply_purchases sp2
            WHERE sp2.supply_id = s.id
            ORDER BY sp2.purchase_date DESC
            LIMIT 1
        )
    """))
    for row in result:
        conn.execute(
            sa.text("UPDATE supplies SET unit = :unit WHERE id = :id"),
            {"unit": row[1], "id": row[0]}
        )

    # Quitar server_default (solo era necesario para la migracion)
    with op.batch_alter_table('supplies') as batch_op:
        batch_op.alter_column('unit', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('supplies') as batch_op:
        batch_op.drop_column('unit')
