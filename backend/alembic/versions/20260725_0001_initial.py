"""Initial schema.

Revision ID: 20260725_0001
Revises: None
"""
from alembic import op
import sqlalchemy as sa

revision = "20260725_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The metadata is the source of truth; create_all keeps the demo frictionless.
    # This migration provides a production-safe first baseline.
    from app.database import Base
    from app import models  # noqa: F401
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    from app.database import Base
    from app import models  # noqa: F401
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
