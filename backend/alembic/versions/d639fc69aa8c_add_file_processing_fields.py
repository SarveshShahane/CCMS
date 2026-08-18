"""add_file_processing_fields

Revision ID: d639fc69aa8c
Revises: bac40869b54a
Create Date: 2026-08-18 18:37:55.063775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd639fc69aa8c'
down_revision: Union[str, None] = 'bac40869b54a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('stored_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('extension', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('complaint_id', sa.Integer(), nullable=True),
        sa.Column('chat_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_files_stored_filename'), 'files', ['stored_filename'], unique=True)
    op.create_index(op.f('ix_files_extension'), 'files', ['extension'], unique=False)
    op.create_index(op.f('ix_files_status'), 'files', ['status'], unique=False)
    op.create_index(op.f('ix_files_complaint_id'), 'files', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_files_chat_id'), 'files', ['chat_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_files_chat_id'), table_name='files')
    op.drop_index(op.f('ix_files_complaint_id'), table_name='files')
    op.drop_index(op.f('ix_files_status'), table_name='files')
    op.drop_index(op.f('ix_files_extension'), table_name='files')
    op.drop_index(op.f('ix_files_stored_filename'), table_name='files')
    op.drop_table('files')
