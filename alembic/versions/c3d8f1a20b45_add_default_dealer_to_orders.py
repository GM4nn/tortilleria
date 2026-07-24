"""add default_dealer to orders

Revision ID: c3d8f1a20b45
Revises: 7e344dd48594
Create Date: 2026-07-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d8f1a20b45'
down_revision: Union[str, Sequence[str], None] = '7e344dd48594'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('default_dealer', sa.String(length=100), nullable=True))
        batch_op.create_foreign_key(
            'fk_orders_default_dealer_dealers',
            'dealers',
            ['default_dealer'],
            ['username'],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_constraint('fk_orders_default_dealer_dealers', type_='foreignkey')
        batch_op.drop_column('default_dealer')
