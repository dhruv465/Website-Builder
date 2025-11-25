"""Add framework and design style fields

Revision ID: 005
Revises: 004
Create Date: 2024-11-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add framework and design_style columns to sites and user_preferences tables."""
    
    # Create enum types for framework and design_style
    framework_enum = sa.Enum(
        'vanilla', 'react', 'vue', 'nextjs', 'svelte',
        name='framework_type'
    )
    design_style_enum = sa.Enum(
        'bold_minimalism', 'brutalism', 'flat_minimalist', 'anti_design',
        'vibrant_blocks', 'organic_fluid', 'retro_nostalgic', 'experimental',
        name='design_style_type'
    )
    
    # Create the enum types in the database
    framework_enum.create(op.get_bind(), checkfirst=True)
    design_style_enum.create(op.get_bind(), checkfirst=True)
    
    # Add framework column to sites table
    op.add_column(
        'sites',
        sa.Column('framework', framework_enum, nullable=True)
    )
    
    # Add design_style column to sites table
    op.add_column(
        'sites',
        sa.Column('design_style', design_style_enum, nullable=True)
    )
    
    # Add framework_preference column to user_preferences table
    op.add_column(
        'user_preferences',
        sa.Column('framework_preference', framework_enum, nullable=True)
    )
    
    # Add design_style_preference column to user_preferences table
    op.add_column(
        'user_preferences',
        sa.Column('design_style_preference', design_style_enum, nullable=True)
    )
    
    # Create framework_changes table for tracking framework migrations
    op.create_table(
        'framework_changes',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('site_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_framework', framework_enum, nullable=True),
        sa.Column('to_framework', framework_enum, nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_framework_changes_site_id', 'framework_changes', ['site_id'])


def downgrade() -> None:
    """Remove framework and design_style columns and framework_changes table."""
    
    # Drop framework_changes table
    op.drop_index('ix_framework_changes_site_id', table_name='framework_changes')
    op.drop_table('framework_changes')
    
    # Drop columns from user_preferences table
    op.drop_column('user_preferences', 'design_style_preference')
    op.drop_column('user_preferences', 'framework_preference')
    
    # Drop columns from sites table
    op.drop_column('sites', 'design_style')
    op.drop_column('sites', 'framework')
    
    # Drop enum types
    sa.Enum(name='design_style_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='framework_type').drop(op.get_bind(), checkfirst=True)
