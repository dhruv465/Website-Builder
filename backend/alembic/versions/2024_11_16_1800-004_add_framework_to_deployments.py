"""add framework to deployments

Revision ID: 004
Revises: 003
Create Date: 2024-11-16 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add framework and build_config columns to deployments table."""
    # Add framework column
    op.add_column(
        'deployments',
        sa.Column('framework', sa.String(50), nullable=False, server_default='vanilla')
    )
    
    # Add build_config column (JSON)
    # Add build_config column (JSON)
    op.add_column(
        'deployments',
        sa.Column('build_config', sa.JSON, nullable=True)
    )
    
    # Remove server default after adding column
    with op.batch_alter_table('deployments') as batch_op:
        batch_op.alter_column('framework', server_default=None)


def downgrade() -> None:
    """Remove framework and build_config columns from deployments table."""
    op.drop_column('deployments', 'build_config')
    op.drop_column('deployments', 'framework')
