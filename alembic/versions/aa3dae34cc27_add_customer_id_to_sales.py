"""add_customer_id_to_sales

Revision ID: aa3dae34cc27
Revises: e0f3ab12f067
Create Date: 2026-01-02 22:40:02.543917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa3dae34cc27'
down_revision: Union[str, Sequence[str], None] = 'e0f3ab12f067'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Usar batch mode para SQLite
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_sales_customer', 'customers', ['customer_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Usar batch mode para SQLite
    with op.batch_alter_table('sales', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sales_customer', type_='foreignkey')
        batch_op.drop_column('customer_id')
