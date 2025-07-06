#!/usr/bin/env python3
"""Initialize local database with NFL teams and sample data."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

if TYPE_CHECKING:
    from supabase import Client

import random
from datetime import datetime, timedelta

from family_huddle.services.database import create_admin_client
from family_huddle.services.nfl_data import nfl_data


def init_nfl_teams(db: "Client") -> None:
    """Initialize NFL teams data in the database.

    Loads team data from the mock NFL data service and inserts all teams
    into the nfl_teams table with conference, division, and point values.

    Args:
        db: Supabase client for database operations.
    """
    print("Initializing NFL teams...")

    teams_df = nfl_data.import_teams()

    for _, team in teams_df.iterrows():
        team_data = {
            "team_code": team["team_code"],
            "team_name": team["team_name"],
            "team_city": team["team_city"],
            "conference": team["conference"],
            "division": team["division"],
            "points": team.get("points", 5),  # Default to 5 points if not specified
            "is_active": True,
        }
        db.table("nfl_teams").insert(team_data).execute()

    print(f"✅ Loaded {len(teams_df)} NFL teams")


def init_seasons_and_weeks(db: "Client") -> str:
    """Initialize current NFL season and weekly schedule data.

    Creates season entry for the current year and generates 18 weeks
    of regular season schedule data.

    Args:
        db: Supabase client for database operations.

    Returns:
        str: The season_id of the created season.
    """
    print("Initializing seasons and weeks...")

    current_year = datetime.now().year

    # Create current season
    season_data = {"season_year": current_year, "regular_season_weeks": 18, "is_current": True}
    season_result = db.table("nfl_seasons").insert(season_data).execute()
    season_id = season_result.data[0]["season_id"]

    # Create weeks
    season_start = datetime(current_year, 9, 7)  # First Thursday of September

    for week_num in range(1, 19):
        week_start = season_start + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6)

        week_data = {
            "season_id": season_id,
            "week_number": week_num,
            "week_type": "Regular",
            "start_date": week_start.date().isoformat(),
            "end_date": week_end.date().isoformat(),
        }
        db.table("nfl_weeks").insert(week_data).execute()

    print(f"✅ Created season {current_year} with 18 weeks")
    return season_id


def init_team_performance(db: "Client", season_id: str) -> None:
    """Initialize mock team performance data for the season.

    Generates random wins/losses records and performance metrics
    for all teams in the given season.

    Args:
        db: Supabase client for database operations.
        season_id: The season ID to associate performance data with.
    """
    print("Initializing team performance...")

    teams = db.table("nfl_teams").select("*").execute().data

    for team in teams:
        # Generate random performance
        wins = random.randint(3, 14)
        losses = 17 - wins

        perf_data = {
            "team_id": team["team_id"],
            "season_id": season_id,
            "games_played": 17,
            "wins": wins,
            "losses": losses,
            "ties": 0,
            "win_percentage": round(wins / 17, 3),
            "playoff_made": wins >= 10,
            "performance_score": round(wins * 5.88 + (15 if wins >= 10 else 0), 3),
        }
        db.table("team_performance").insert(perf_data).execute()

    print("✅ Generated team performance data")


def init_sample_users(db: "Client") -> None:
    """Create sample user accounts for testing purposes.

    Creates test user accounts with default password 'password' and
    associated default profiles for testing the application.

    Args:
        db: Supabase client for database operations.
    """
    print("Creating sample users...")

    # Password is 'password' for all test users
    from family_huddle.pages.auth import hash_password

    test_password = hash_password("password")

    test_users = [
        {
            "email": "test@example.com",
            "password_hash": test_password,
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "email_verified": True,
        },
        {
            "email": "john@example.com",
            "password_hash": test_password,
            "first_name": "John",
            "last_name": "Doe",
            "is_active": True,
            "email_verified": True,
        },
    ]

    for user_data in test_users:
        result = db.table("users").insert(user_data).execute()

        # Create default profile with first and last name
        profile_data = {
            "user_id": result.data[0]["user_id"],
            "profile_name": f"{user_data['first_name']} {user_data['last_name']}",
            "display_name": f"{user_data['first_name']} {user_data['last_name']}",
        }
        db.table("profiles").insert(profile_data).execute()

    print("✅ Created sample users (password: 'password')")


def init_sample_pool(db: "Client") -> None:
    """Create a sample football pool for testing.

    Creates a default family pool for the current year with standard
    settings for testing pool functionality.

    Args:
        db: Supabase client for database operations.
    """
    print("Creating sample pool...")

    users = db.table("users").select("*").execute().data
    if users:
        pool_data = {
            "pool_name": "Family Pool 2024",
            "pool_description": "Annual family football pool - may the best teams win!",
            "created_by": users[0]["user_id"],
            "season_year": datetime.now().year,
            "entry_fee": 20.00,
            "max_participants": 20,
            "registration_deadline": (datetime.now() + timedelta(days=7)).isoformat(),
            "is_active": True,
        }
        db.table("pools").insert(pool_data).execute()

        print("✅ Created sample pool")


def main() -> None:
    """Main data initialization function.

    Orchestrates the complete database initialization process including
    teams, seasons, performance data, users, and sample pools.
    Prompts for confirmation if data already exists.
    """
    print("🏈 Family Football Pool - Data Initialization")
    print("=" * 50)

    db = create_admin_client()

    existing_teams = db.table("nfl_teams").select("*").execute().data

    if existing_teams:
        response = input("Data already exists. Reinitialize? (y/N): ")
        if response.lower() != "y":
            print("Initialization cancelled.")
            return

        print("Clearing existing data...")
        tables = [
            "pool_scores",
            "team_selections",
            "pool_participants",
            "pools",
            "profiles",
            "users",
            "team_performance",
            "nfl_games",
            "nfl_weeks",
            "nfl_seasons",
            "nfl_teams",
        ]

        for table in tables:
            try:
                # Delete all records from table
                db.table(table).delete().neq("id", "impossible_value").execute()
            except Exception as e:
                print(f"Warning: Could not clear table {table}: {e}")
                # Continue anyway

    init_nfl_teams(db)
    season_id = init_seasons_and_weeks(db)
    init_team_performance(db, season_id)
    init_sample_users(db)
    init_sample_pool(db)

    print("\n✅ Initialization complete!")
    print("\nYou can now run the app with: streamlit run app.py")
    print("\nTest credentials:")
    print("  Email: test@example.com")
    print("  Password: password")


if __name__ == "__main__":
    main()
