"""Mock NFL data provider for local testing."""

import random
from datetime import datetime, timedelta
from typing import Any

import pandas as pd


class MockNFLData:
    """Mock NFL data provider that simulates nfl_data_py functionality."""

    def __init__(self) -> None:
        self.teams = self._create_teams()
        self.current_season = datetime.now().year

    def _create_teams(self) -> list[dict[str, Any]]:
        """Create mock NFL teams data."""
        teams = [
            # AFC East
            {
                "team_code": "BUF",
                "team_name": "Bills",
                "team_city": "Buffalo",
                "conference": "AFC",
                "division": "East",
                "points": 10,
            },
            {
                "team_code": "MIA",
                "team_name": "Dolphins",
                "team_city": "Miami",
                "conference": "AFC",
                "division": "East",
                "points": 8,
            },
            {
                "team_code": "NE",
                "team_name": "Patriots",
                "team_city": "New England",
                "conference": "AFC",
                "division": "East",
                "points": 6,
            },
            {
                "team_code": "NYJ",
                "team_name": "Jets",
                "team_city": "New York",
                "conference": "AFC",
                "division": "East",
                "points": 4,
            },
            # AFC North
            {
                "team_code": "BAL",
                "team_name": "Ravens",
                "team_city": "Baltimore",
                "conference": "AFC",
                "division": "North",
                "points": 9,
            },
            {
                "team_code": "CIN",
                "team_name": "Bengals",
                "team_city": "Cincinnati",
                "conference": "AFC",
                "division": "North",
                "points": 7,
            },
            {
                "team_code": "CLE",
                "team_name": "Browns",
                "team_city": "Cleveland",
                "conference": "AFC",
                "division": "North",
                "points": 5,
            },
            {
                "team_code": "PIT",
                "team_name": "Steelers",
                "team_city": "Pittsburgh",
                "conference": "AFC",
                "division": "North",
                "points": 10,
            },
            # AFC South
            {
                "team_code": "HOU",
                "team_name": "Texans",
                "team_city": "Houston",
                "conference": "AFC",
                "division": "South",
                "points": 7,
            },
            {
                "team_code": "IND",
                "team_name": "Colts",
                "team_city": "Indianapolis",
                "conference": "AFC",
                "division": "South",
                "points": 6,
            },
            {
                "team_code": "JAX",
                "team_name": "Jaguars",
                "team_city": "Jacksonville",
                "conference": "AFC",
                "division": "South",
                "points": 5,
            },
            {
                "team_code": "TEN",
                "team_name": "Titans",
                "team_city": "Tennessee",
                "conference": "AFC",
                "division": "South",
                "points": 4,
            },
            # AFC West
            {
                "team_code": "DEN",
                "team_name": "Broncos",
                "team_city": "Denver",
                "conference": "AFC",
                "division": "West",
                "points": 6,
            },
            {
                "team_code": "KC",
                "team_name": "Chiefs",
                "team_city": "Kansas City",
                "conference": "AFC",
                "division": "West",
                "points": 10,
            },
            {
                "team_code": "LV",
                "team_name": "Raiders",
                "team_city": "Las Vegas",
                "conference": "AFC",
                "division": "West",
                "points": 5,
            },
            {
                "team_code": "LAC",
                "team_name": "Chargers",
                "team_city": "Los Angeles",
                "conference": "AFC",
                "division": "West",
                "points": 8,
            },
            # NFC East
            {
                "team_code": "DAL",
                "team_name": "Cowboys",
                "team_city": "Dallas",
                "conference": "NFC",
                "division": "East",
                "points": 9,
            },
            {
                "team_code": "NYG",
                "team_name": "Giants",
                "team_city": "New York",
                "conference": "NFC",
                "division": "East",
                "points": 5,
            },
            {
                "team_code": "PHI",
                "team_name": "Eagles",
                "team_city": "Philadelphia",
                "conference": "NFC",
                "division": "East",
                "points": 10,
            },
            {
                "team_code": "WAS",
                "team_name": "Commanders",
                "team_city": "Washington",
                "conference": "NFC",
                "division": "East",
                "points": 6,
            },
            # NFC North
            {
                "team_code": "CHI",
                "team_name": "Bears",
                "team_city": "Chicago",
                "conference": "NFC",
                "division": "North",
                "points": 4,
            },
            {
                "team_code": "DET",
                "team_name": "Lions",
                "team_city": "Detroit",
                "conference": "NFC",
                "division": "North",
                "points": 9,
            },
            {
                "team_code": "GB",
                "team_name": "Packers",
                "team_city": "Green Bay",
                "conference": "NFC",
                "division": "North",
                "points": 8,
            },
            {
                "team_code": "MIN",
                "team_name": "Vikings",
                "team_city": "Minnesota",
                "conference": "NFC",
                "division": "North",
                "points": 7,
            },
            # NFC South
            {
                "team_code": "ATL",
                "team_name": "Falcons",
                "team_city": "Atlanta",
                "conference": "NFC",
                "division": "South",
                "points": 6,
            },
            {
                "team_code": "CAR",
                "team_name": "Panthers",
                "team_city": "Carolina",
                "conference": "NFC",
                "division": "South",
                "points": 3,
            },
            {
                "team_code": "NO",
                "team_name": "Saints",
                "team_city": "New Orleans",
                "conference": "NFC",
                "division": "South",
                "points": 7,
            },
            {
                "team_code": "TB",
                "team_name": "Buccaneers",
                "team_city": "Tampa Bay",
                "conference": "NFC",
                "division": "South",
                "points": 8,
            },
            # NFC West
            {
                "team_code": "ARI",
                "team_name": "Cardinals",
                "team_city": "Arizona",
                "conference": "NFC",
                "division": "West",
                "points": 5,
            },
            {
                "team_code": "LAR",
                "team_name": "Rams",
                "team_city": "Los Angeles",
                "conference": "NFC",
                "division": "West",
                "points": 7,
            },
            {
                "team_code": "SF",
                "team_name": "49ers",
                "team_city": "San Francisco",
                "conference": "NFC",
                "division": "West",
                "points": 10,
            },
            {
                "team_code": "SEA",
                "team_name": "Seahawks",
                "team_city": "Seattle",
                "conference": "NFC",
                "division": "West",
                "points": 6,
            },
        ]
        return teams

    def import_teams(self) -> pd.DataFrame:
        """Import NFL teams data."""
        return pd.DataFrame(self.teams)

    def import_schedules(self, years: list[int]) -> pd.DataFrame:
        """Import NFL schedules for given years."""
        schedules = []

        for year in years:
            season_start = datetime(year, 9, 7)

            for week in range(1, 19):  # 18 weeks
                week_start = season_start + timedelta(weeks=week - 1)

                teams_copy = self.teams.copy()
                random.shuffle(teams_copy)

                for i in range(0, len(teams_copy), 2):
                    if i + 1 < len(teams_copy):
                        home_team = teams_copy[i]["team_code"]
                        away_team = teams_copy[i + 1]["team_code"]

                        game_date = week_start + timedelta(
                            days=random.choice([0, 3, 4])
                        )  # Thu, Sun, Mon

                        # Simulate some completed games
                        if week < self._get_current_week(year):
                            home_score = random.randint(0, 45)
                            away_score = random.randint(0, 45)
                            status = "COMPLETED"
                        else:
                            home_score = None
                            away_score = None
                            status = "SCHEDULED"

                        schedules.append(
                            {
                                "season": year,
                                "week": week,
                                "game_date": game_date,
                                "home_team": home_team,
                                "away_team": away_team,
                                "home_score": home_score,
                                "away_score": away_score,
                                "game_status": status,
                            }
                        )

        return pd.DataFrame(schedules)

    def import_team_stats(self, years: list[int]) -> pd.DataFrame:
        """Import team statistics for given years."""
        stats = []

        for year in years:
            for team in self.teams:
                wins = random.randint(3, 14)
                losses = 17 - wins

                stats.append(
                    {
                        "season": year,
                        "team": team["team_code"],
                        "games_played": 17,
                        "wins": wins,
                        "losses": losses,
                        "ties": 0,
                        "win_percentage": wins / 17,
                        "playoff_made": wins >= 10,  # Simplified playoff logic
                    }
                )

        return pd.DataFrame(stats)

    def _get_current_week(self, year: int) -> int:
        """Get the current week of the NFL season."""
        if year < datetime.now().year:
            return 19  # Past season, all games complete
        elif year > datetime.now().year:
            return 0  # Future season
        else:
            # Current season - calculate week
            season_start = datetime(year, 9, 7)
            weeks_elapsed = (datetime.now() - season_start).days // 7
            return min(max(1, weeks_elapsed + 1), 18)


# Global instance for easy import
nfl_data = MockNFLData()
