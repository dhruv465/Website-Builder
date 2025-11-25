"""Add integrations table

Revision ID: 002
Revises: 001
Create Date: 2024-11-16 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create integrations table."""
    op.create_table(
        'integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('site_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('integration_type', sa.String(length=50), nullable=False),
        sa.Column('provider', sa.String(length=100), nullable=False),
        sa.Column('html_snippet', sa.Text(), nullable=False),
        sa.Column('javascript_snippet', sa.Text(), nullable=True),
        sa.Column('css_snippet', sa.Text(), nullable=True),
        sa.Column('dependencies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('setup_instructions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_secure', sa.Boolean(), nullable=True),
        sa.Column('security_issues', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('security_warnings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('security_recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_integrations_site_id'), 'integrations', ['site_id'], unique=False)


def downgrade() -> None:
    """Drop integrations table."""
    op.drop_index(op.f('ix_integrations_site_id'), table_name='integrations')
    op.drop_table('integrations')
