#!/usr/bin/env python3
"""Initialize production database with schema and sample data (non-interactive)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scripts.init_data import (
    init_nfl_teams,
    init_seasons_and_weeks,
    init_team_performance,
    init_sample_users,
    init_sample_pool,
)
from family_huddle.services.database import create_admin_client


def main() -> None:
    """Initialize production database without user prompts."""
    print("🏈 Family Football Pool - Production Initialization")
    print("=" * 50)

    try:
        db = create_admin_client()
        
        # Check if already initialized
        existing_teams = db.table("nfl_teams").select("*").execute().data
        
        if existing_teams:
            print("⚠️  Database already initialized. Skipping data initialization.")
            print(f"Found {len(existing_teams)} teams in database.")
            return
        
        print("🚀 Initializing production database...")
        
        init_nfl_teams(db)
        season_id = init_seasons_and_weeks(db)
        init_team_performance(db, season_id)
        init_sample_users(db)
        init_sample_pool(db)
        
        print("\n✅ Production initialization complete!")
        print("\nTest credentials:")
        print("  Email: test@example.com")
        print("  Password: password")
        
    except Exception as e:
        print(f"❌ Production initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()