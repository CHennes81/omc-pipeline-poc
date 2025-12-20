"""Seed data loading functionality."""
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.database import engine


def load_seed_sql(db: Session, reset: bool = False) -> dict:
    """Load seed data from db/seed.sql file."""
    # Get the project root (two levels up from apps/api/app)
    project_root = Path(__file__).parent.parent.parent.parent
    seed_file = project_root / "db" / "seed.sql"

    if not seed_file.exists():
        raise FileNotFoundError(f"Seed file not found: {seed_file}")

    with open(seed_file, "r") as f:
        seed_sql = f.read()

    # Execute the seed SQL
    with engine.connect() as conn:
        # If reset mode, truncate tables first
        if reset:
            conn.execute("""
                TRUNCATE TABLE events, package_members, packages,
                          version_lineage, versions, assets, shots, productions CASCADE
            """)
            conn.commit()

        # Execute seed SQL
        conn.execute(seed_sql)
        conn.commit()

    # Count shots loaded
    result = db.execute("SELECT COUNT(*) FROM shots WHERE production_id = (SELECT id FROM productions WHERE code = 'EXFTR')")
    shots_count = result.scalar() or 0

    return {
        "ok": True,
        "production_code": "EXFTR",
        "shots_loaded": shots_count
    }
