"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-11-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=False),
        sa.Column('preferences', JSON, nullable=False, server_default='{}'),
    )
    op.create_index('ix_sessions_id', 'sessions', ['id'])
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', UUID(as_uuid=True), nullable=False),
        sa.Column('default_color_scheme', sa.String(100), nullable=True),
        sa.Column('default_site_type', sa.String(100), nullable=True),
        sa.Column('favorite_features', JSON, nullable=False, server_default='[]'),
        sa.Column('design_style', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_user_preferences_session_id', 'user_preferences', ['session_id'])
    
    # Create sites table
    op.create_table(
        'sites',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_sites_session_id', 'sites', ['session_id'])
    
    # Create site_versions table
    op.create_table(
        'site_versions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('site_id', UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('requirements', JSON, nullable=True),
        sa.Column('changes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('audit_score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_site_versions_site_id', 'site_versions', ['site_id'])
    
    # Create audits table
    op.create_table(
        'audits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('site_id', UUID(as_uuid=True), nullable=False),
        sa.Column('site_version_id', UUID(as_uuid=True), nullable=True),
        sa.Column('seo_score', sa.Integer(), nullable=False),
        sa.Column('accessibility_score', sa.Integer(), nullable=False),
        sa.Column('performance_score', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('details', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['site_version_id'], ['site_versions.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_audits_site_id', 'audits', ['site_id'])
    op.create_index('ix_audits_site_version_id', 'audits', ['site_version_id'])
    
    # Create audit_issues table
    op.create_table(
        'audit_issues',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('audit_id', UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('severity', sa.Enum('critical', 'warning', 'info', name='severitylevel'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('location', sa.String(500), nullable=True),
        sa.Column('fix_suggestion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_audit_issues_audit_id', 'audit_issues', ['audit_id'])
    
    # Create deployments table
    op.create_table(
        'deployments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('site_id', UUID(as_uuid=True), nullable=False),
        sa.Column('site_version_id', UUID(as_uuid=True), nullable=True),
        sa.Column('url', sa.String(512), nullable=False),
        sa.Column('deployment_id', sa.String(255), nullable=False),
        sa.Column('project_id', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('build_time', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['site_version_id'], ['site_versions.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_deployments_site_id', 'deployments', ['site_id'])
    op.create_index('ix_deployments_site_version_id', 'deployments', ['site_version_id'])
    
    # Create workflow_logs table
    op.create_table(
        'workflow_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('workflow_id', UUID(as_uuid=True), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=True),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_workflow_logs_workflow_id', 'workflow_logs', ['workflow_id'])
    op.create_index('ix_workflow_logs_created_at', 'workflow_logs', ['created_at'])
    
    # Create agent_metrics table
    op.create_table(
        'agent_metrics',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_duration', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_execution_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_agent_metrics_agent_name', 'agent_metrics', ['agent_name'])


def downgrade() -> None:
    op.drop_table('agent_metrics')
    op.drop_table('workflow_logs')
    op.drop_table('deployments')
    op.drop_table('audit_issues')
    op.drop_table('audits')
    op.drop_table('site_versions')
    op.drop_table('sites')
    op.drop_table('user_preferences')
    op.drop_table('sessions')
