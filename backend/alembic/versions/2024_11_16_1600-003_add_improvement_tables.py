"""Add improvement workflow tables

Revision ID: 003
Revises: 002
Create Date: 2024-11-16 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create quality_thresholds table
    op.create_table(
        'quality_thresholds',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('seo_min_score', sa.Integer(), nullable=False, server_default='70'),
        sa.Column('accessibility_min_score', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('performance_min_score', sa.Integer(), nullable=False, server_default='75'),
        sa.Column('overall_min_score', sa.Integer(), nullable=False, server_default='75'),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create improvement_cycles table
    op.create_table(
        'improvement_cycles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('site_id', sa.String(), nullable=True),
        sa.Column('cycle_number', sa.Integer(), nullable=False),
        sa.Column('initial_seo_score', sa.Integer(), nullable=False),
        sa.Column('initial_accessibility_score', sa.Integer(), nullable=False),
        sa.Column('initial_performance_score', sa.Integer(), nullable=False),
        sa.Column('initial_overall_score', sa.Integer(), nullable=False),
        sa.Column('final_seo_score', sa.Integer(), nullable=True),
        sa.Column('final_accessibility_score', sa.Integer(), nullable=True),
        sa.Column('final_performance_score', sa.Integer(), nullable=True),
        sa.Column('final_overall_score', sa.Integer(), nullable=True),
        sa.Column('issues_addressed', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('improvement_instructions', sa.String(), nullable=True),
        sa.Column('success', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_improvement_cycles_workflow_id', 'improvement_cycles', ['workflow_id'])
    op.create_index('ix_improvement_cycles_session_id', 'improvement_cycles', ['session_id'])
    op.create_index('ix_improvement_cycles_site_id', 'improvement_cycles', ['site_id'])
    
    # Insert default quality threshold
    op.execute("""
        INSERT INTO quality_thresholds (id, name, seo_min_score, accessibility_min_score, performance_min_score, overall_min_score, enabled)
        VALUES ('default-threshold-001', 'default', 70, 80, 75, 75, true)
    """)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index('ix_improvement_cycles_site_id', table_name='improvement_cycles')
    op.drop_index('ix_improvement_cycles_session_id', table_name='improvement_cycles')
    op.drop_index('ix_improvement_cycles_workflow_id', table_name='improvement_cycles')
    op.drop_table('improvement_cycles')
    op.drop_table('quality_thresholds')
