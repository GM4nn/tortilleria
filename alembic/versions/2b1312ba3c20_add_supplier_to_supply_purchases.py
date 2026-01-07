"""add_supplier_to_supply_purchases

Revision ID: 2b1312ba3c20
Revises: 2999a5228b35
Create Date: 2026-01-06 13:25:54.634245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b1312ba3c20'
down_revision: Union[str, Sequence[str], None] = '2999a5228b35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER COLUMN, so we need to use batch_alter_table
    with op.batch_alter_table('supply_purchases') as batch_op:
        # Add supplier_id column
        batch_op.add_column(sa.Column('supplier_id', sa.Integer(), nullable=True))

    # Set supplier_id for existing purchases based on their supply's supplier
    op.execute("""
        UPDATE supply_purchases
        SET supplier_id = (
            SELECT supplier_id
            FROM supplies
            WHERE supplies.id = supply_purchases.supply_id
        )
    """)

    # Create a new table with the updated schema and copy data
    # This is the recommended approach for SQLite schema changes
    with op.batch_alter_table('supply_purchases') as batch_op:
        # Make supplier_id NOT NULL
        batch_op.alter_column('supplier_id', nullable=False)

        # Add foreign key constraint
        batch_op.create_foreign_key(
            'fk_supply_purchases_supplier_id',
            'suppliers',
            ['supplier_id'],
            ['id']
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraint
    op.drop_constraint('fk_supply_purchases_supplier_id', 'supply_purchases', type_='foreignkey')

    # Drop supplier_id column
    op.drop_column('supply_purchases', 'supplier_id')
