"""Prevent anonymous writes through a managed database's automatic data API."""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    for table in [
        "districts",
        "villages",
        "grid_cells",
        "grid_village_parts",
        "historical_flood_events",
        "grid_flood_evidence",
        "rainfall_scenarios",
        "waterways",
        "risk_results",
        "model_metadata",
        "priority_weights_config",
    ]:
        op.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')


def downgrade():
    raise RuntimeError(
        "Removing database access protection needs an explicit reviewed migration"
    )
