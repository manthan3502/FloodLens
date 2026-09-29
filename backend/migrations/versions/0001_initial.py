"""Version the real feature, scoring and priority configuration schema."""

from pathlib import Path

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    for statement in Path(__file__).with_name("0001_schema.sql").read_text().split(";"):
        if statement.strip():
            op.execute(statement)
    op.execute(
        "CREATE TABLE IF NOT EXISTS model_metadata (id text PRIMARY KEY, model_type text NOT NULL, trained_at timestamptz, pr_auc_spatial_cv double precision, pr_auc_temporal_holdout double precision, feature_list jsonb NOT NULL, notes jsonb NOT NULL)"
    )
    op.execute(
        "CREATE TABLE IF NOT EXISTS risk_results (grid_cell_id text REFERENCES grid_cells(id), scenario_id text REFERENCES rainfall_scenarios(id), risk_score double precision NOT NULL CHECK(risk_score BETWEEN 0 AND 1), risk_category text NOT NULL, computed_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY(grid_cell_id,scenario_id))"
    )
    op.execute(
        "CREATE TABLE IF NOT EXISTS priority_weights_config (id integer PRIMARY KEY CHECK(id=1), w_risk double precision NOT NULL CHECK(w_risk>=0), w_pop double precision NOT NULL CHECK(w_pop>=0), updated_at timestamptz NOT NULL DEFAULT now(), CHECK(abs(w_risk+w_pop-1)<0.000001))"
    )
    op.execute(
        "INSERT INTO priority_weights_config(id,w_risk,w_pop) VALUES(1,0.65,0.35) ON CONFLICT DO NOTHING"
    )


def downgrade():
    raise RuntimeError(
        "Destructive schema removal requires an explicit reviewed migration"
    )
