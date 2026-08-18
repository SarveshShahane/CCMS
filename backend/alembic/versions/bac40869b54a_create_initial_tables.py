"""create_initial_tables

Revision ID: bac40869b54a
Revises: 
Create Date: 2026-08-18 11:43:14.927533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bac40869b54a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create complaints table
    op.create_table(
        'complaints',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('complaint_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='NEW', nullable=False),
        sa.Column('complaint_source', sa.String(length=100), server_default='Pharmacy', nullable=True),
        sa.Column('customer_name', sa.String(length=255), nullable=True),
        sa.Column('customer_contact_email', sa.String(length=255), nullable=True),
        sa.Column('customer_contact_phone', sa.String(length=50), nullable=True),
        sa.Column('product_name', sa.String(length=255), nullable=True),
        sa.Column('product_code', sa.String(length=100), nullable=True),
        sa.Column('dosage_form', sa.String(length=100), nullable=True),
        sa.Column('product_strength', sa.String(length=100), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('affected_quantity', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('affected_quantity_unit', sa.String(length=50), server_default='units', nullable=False),
        sa.Column('normalized_quantity', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('originating_site_block', sa.String(length=100), nullable=True),
        sa.Column('impacted_npm', sa.String(length=255), nullable=True),
        sa.Column('complaint_category', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sample_received', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('initial_severity', sa.String(length=50), nullable=True),
        sa.Column('suggested_severity', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('ai_risk_assessment', sa.Text(), nullable=True),
        sa.Column('ai_suggested_next_action', sa.Text(), nullable=True),
        sa.Column('ai_extra_data', sa.JSON(), nullable=True),
        sa.Column('root_cause_category', sa.String(length=100), nullable=True),
        sa.Column('investigation_findings', sa.Text(), nullable=True),
        sa.Column('capa_required', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('capa_details', sa.Text(), nullable=True),
        sa.Column('incident_date', sa.Date(), nullable=True),
        sa.Column('complaint_date', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
        sa.Column('manufacturing_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('sample_received_date', sa.Date(), nullable=True),
        sa.Column('investigation_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('investigation_completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('capa_target_date', sa.Date(), nullable=True),
        sa.Column('capa_completion_date', sa.Date(), nullable=True),
        sa.Column('resolved_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaints_batch_number'), 'complaints', ['batch_number'], unique=False)
    op.create_index(op.f('ix_complaints_complaint_category'), 'complaints', ['complaint_category'], unique=False)
    op.create_index(op.f('ix_complaints_complaint_number'), 'complaints', ['complaint_number'], unique=True)
    op.create_index(op.f('ix_complaints_product_code'), 'complaints', ['product_code'], unique=False)
    op.create_index(op.f('ix_complaints_product_name'), 'complaints', ['product_name'], unique=False)
    op.create_index(op.f('ix_complaints_status'), 'complaints', ['status'], unique=False)

    # 2. Create chats table
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('complaint_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chats_complaint_id'), 'chats', ['complaint_id'], unique=False)

    # 3. Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('sender', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_chat_id'), 'chat_messages', ['chat_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_chat_messages_chat_id'), table_name='chat_messages')
    op.drop_table('chat_messages')

    op.drop_index(op.f('ix_chats_complaint_id'), table_name='chats')
    op.drop_table('chats')

    op.drop_index(op.f('ix_complaints_status'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_product_name'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_product_code'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_complaint_number'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_complaint_category'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_batch_number'), table_name='complaints')
    op.drop_table('complaints')

