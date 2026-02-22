"""rename initial_stock to remaining and drop supply_consumptions

Revision ID: be7520d40658
Revises: 7a96d752b753
Create Date: 2026-02-21 21:24:34.405213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be7520d40658'
down_revision: Union[str, Sequence[str], None] = '7a96d752b753'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Renombrar initial_stock -> remaining (batch mode para SQLite)
    with op.batch_alter_table('supply_purchases') as batch_op:
        batch_op.alter_column('initial_stock', new_column_name='remaining')

    # Eliminar tabla de consumos (ya no se necesita)
    op.drop_table('supply_consumptions')


def downgrade() -> None:
    # Recrear tabla supply_consumptions
    op.create_table('supply_consumptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('supply_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('quantity_consumed', sa.Float(), nullable=False),
        sa.Column('quantity_remaining', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['supply_id'], ['supplies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Renombrar remaining -> initial_stock
    with op.batch_alter_table('supply_purchases') as batch_op:
        batch_op.alter_column('remaining', new_column_name='initial_stock')
