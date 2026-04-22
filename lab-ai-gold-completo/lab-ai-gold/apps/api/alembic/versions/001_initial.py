"""initial tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")

    op.execute("CREATE TYPE userrole AS ENUM ('user','geologist','admin')")
    op.execute("CREATE TYPE userstatus AS ENUM ('active','inactive','pending')")
    op.execute("CREATE TYPE projectstatus AS ENUM ('active','archived')")
    op.execute("CREATE TYPE projectphase AS ENUM ('phase1','phase2')")
    op.execute("CREATE TYPE parsestatus AS ENUM ('pending','ok','error')")
    op.execute("CREATE TYPE analysisstatus AS ENUM ('pending','running','done','error')")
    op.execute("CREATE TYPE priority AS ENUM ('high','medium','low')")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name",          sa.String(120),  nullable=False),
        sa.Column("email",         sa.String(255),  nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255),  nullable=False),
        sa.Column("role",   sa.Enum("user","geologist","admin", name="userrole"),     nullable=False, server_default="user"),
        sa.Column("status", sa.Enum("active","inactive","pending", name="userstatus"), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id",      UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name",        sa.String(200), nullable=False),
        sa.Column("description", sa.Text,        nullable=True),
        sa.Column("status", sa.Enum("active","archived",           name="projectstatus"), nullable=False, server_default="active"),
        sa.Column("phase",  sa.Enum("phase1","phase2",             name="projectphase"),  nullable=False, server_default="phase1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_projects_user_id", "projects", ["user_id"])

    op.create_table(
        "project_areas",
        sa.Column("id",         UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_filename", sa.String(255)),
        sa.Column("storage_path",      sa.String(512)),
        sa.Column("geojson",      JSONB, nullable=True),
        sa.Column("area_ha",      sa.Float, nullable=True),
        sa.Column("centroid_lat", sa.Float, nullable=True),
        sa.Column("centroid_lng", sa.Float, nullable=True),
        sa.Column("bounds_json",  JSONB, nullable=True),
        sa.Column("parse_status", sa.Enum("pending","ok","error", name="parsestatus"), nullable=False, server_default="pending"),
        sa.Column("parse_error",  sa.Text, nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_project_areas_project_id", "project_areas", ["project_id"])

    op.create_table(
        "analyses",
        sa.Column("id",           UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("project_id",   UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("phase",             sa.String(20),  nullable=False, server_default="phase1"),
        sa.Column("status",            sa.Enum("pending","running","done","error", name="analysisstatus"), nullable=False, server_default="pending"),
        sa.Column("algorithm_version", sa.String(20),  nullable=False, server_default="v0"),
        sa.Column("summary_json",  JSONB, nullable=True),
        sa.Column("started_at",    sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at",   sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at",    sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_analyses_project_id", "analyses", ["project_id"])

    op.create_table(
        "analysis_points",
        sa.Column("id",          UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("analysis_id", UUID(as_uuid=True), sa.ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label",    sa.String(50)),
        sa.Column("lat",      sa.Float),
        sa.Column("lng",      sa.Float),
        sa.Column("score",    sa.Float),
        sa.Column("priority", sa.Enum("high","medium","low", name="priority"), nullable=False),
        sa.Column("color",    sa.String(10)),
        sa.Column("rank",     sa.Integer),
        sa.Column("reasons_json", JSONB, nullable=False, server_default="'[]'"),
    )
    op.create_index("ix_analysis_points_analysis_id", "analysis_points", ["analysis_id"])


def downgrade() -> None:
    op.drop_table("analysis_points")
    op.drop_table("analyses")
    op.drop_table("project_areas")
    op.drop_table("projects")
    op.drop_table("users")
    for t in ["userrole","userstatus","projectstatus","projectphase","parsestatus","analysisstatus","priority"]:
        op.execute(f"DROP TYPE IF EXISTS {t}")
