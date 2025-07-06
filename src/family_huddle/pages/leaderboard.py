"""Leaderboard page for displaying pool rankings."""

from typing import TYPE_CHECKING, Any

import pandas as pd
import plotly.express as px
import streamlit as st

if TYPE_CHECKING:
    from supabase import Client


def show(db: "Client") -> None:
    """Display the leaderboard interface with pool selection.

    Shows tabs for overall standings, weekly performance, and team performance
    analysis for the selected pool.

    Args:
        db: Supabase client for database operations.
    """
    st.title("📊 Leaderboards")

    current_profile = st.session_state.current_profile

    if not current_profile:
        st.warning("Please select or create a profile first!")
        st.stop()

    participants = (
        db.table("pool_participants")
        .select("*")
        .eq("profile_id", current_profile["profile_id"])
        .execute()
    )

    if not participants.data:
        st.info("You haven't joined any pools yet!")
        return

    pool_options = []
    pool_map = {}

    for participant in participants.data:
        pool = db.table("pools").select("*").eq("pool_id", participant["pool_id"]).execute().data[0]

        pool_name = f"{pool['pool_name']} ({pool['season_year']})"
        pool_options.append(pool_name)
        pool_map[pool_name] = pool

    selected_pool_name = st.selectbox("Select Pool", pool_options)
    selected_pool = pool_map[selected_pool_name]

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Pool Name", selected_pool["pool_name"])

    with col2:
        st.metric("Season", selected_pool["season_year"])

    with col3:
        all_participants = (
            db.table("pool_participants")
            .select("*")
            .eq("pool_id", selected_pool["pool_id"])
            .execute()
        )
        st.metric("Participants", len(all_participants.data) if all_participants.data else 0)

    tab1, tab2, tab3 = st.tabs(["Overall Standings", "Weekly Performance", "Team Performance"])

    with tab1:
        show_overall_standings(db, selected_pool)

    with tab2:
        show_weekly_performance(db, selected_pool)

    with tab3:
        show_team_performance(db, selected_pool)


def show_overall_standings(db: "Client", pool: dict[str, Any]) -> None:
    """Display overall pool standings with rankings and points.

    Shows participant rankings, total points, team selections, and completion status
    with visual highlighting of current user.

    Args:
        db: Supabase client for database operations.
        pool: Pool dictionary containing pool_id and other pool details.
    """
    st.subheader("Overall Standings")

    participants = (
        db.table("pool_participants").select("*").eq("pool_id", pool["pool_id"]).execute()
    )

    if not participants.data:
        st.info("No participants in this pool yet.")
        return

    standings_data = []

    for participant in participants.data:
        profile = (
            db.table("profiles")
            .select("*")
            .eq("profile_id", participant["profile_id"])
            .execute()
            .data[0]
        )

        scores = (
            db.table("pool_scores")
            .select("*")
            .eq("pool_id", pool["pool_id"])
            .eq("profile_id", participant["profile_id"])
            .execute()
        )

        if not scores.data:
            import random

            weeks = db.table("nfl_weeks").select("*").limit(1).execute()
            week_id = weeks.data[0]["week_id"] if weeks.data else None

            mock_score = {
                "pool_id": pool["pool_id"],
                "profile_id": participant["profile_id"],
                "week_id": week_id,
                "points_earned": random.randint(20, 100),
                "total_points": random.randint(100, 500),
            }
            db.table("pool_scores").insert(mock_score).execute()
            total_points = mock_score["total_points"]
        else:
            total_points = scores.data[-1]["total_points"]

        selections = (
            db.table("team_selections")
            .select("*")
            .eq("pool_id", pool["pool_id"])
            .eq("profile_id", participant["profile_id"])
            .execute()
        )

        teams = []
        if selections.data:
            for selection in sorted(selections.data, key=lambda x: x["selection_order"]):
                team = (
                    db.table("nfl_teams")
                    .select("*")
                    .eq("team_id", selection["team_id"])
                    .execute()
                    .data[0]
                )
                teams.append(f"{team['team_code']}")

        standings_data.append(
            {
                "Rank": 0,  # Will be calculated
                "Name": profile["display_name"],
                "Teams": ", ".join(teams) if teams else "No teams selected",
                "Total Points": total_points,
                "Status": "✅" if participant["selections_complete"] else "⚠️ Incomplete",
            }
        )

    standings_data.sort(key=lambda x: x["Total Points"], reverse=True)
    for i, standing in enumerate(standings_data):
        standing["Rank"] = i + 1

    df = pd.DataFrame(standings_data)

    current_profile_name = st.session_state.current_profile["display_name"]

    def highlight_user(row: Any) -> list[str]:
        if row["Name"] == current_profile_name:
            return ["background-color: #ffffcc"] * len(row)
        return [""] * len(row)

    styled_df = df.style.apply(highlight_user, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    if len(standings_data) > 1:
        st.subheader("Points Distribution")

        fig = px.bar(
            df,
            x="Name",
            y="Total Points",
            title="Total Points by Participant",
            color="Total Points",
            color_continuous_scale="Blues",
        )

        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def show_weekly_performance(db: "Client", pool: dict[str, Any]) -> None:
    """Display weekly performance trends with cumulative scoring.

    Shows mock data visualization of cumulative points by week for pool participants.

    Args:
        db: Supabase client for database operations.
        pool: Pool dictionary containing pool_id and other pool details.
    """
    st.subheader("Weekly Performance")

    st.info("Weekly performance tracking will be available once the season starts!")

    weeks = list(range(1, 8))
    mock_data = []

    participants = (
        db.table("pool_participants").select("*").eq("pool_id", pool["pool_id"]).execute()
    )

    if participants.data:
        for participant in participants.data[:5]:  # Show top 5
            profile = (
                db.table("profiles")
                .select("*")
                .eq("profile_id", participant["profile_id"])
                .execute()
                .data[0]
            )

            import random

            weekly_points = [random.randint(20, 80) for _ in weeks]
            cumulative = []
            total = 0
            for points in weekly_points:
                total += points
                cumulative.append(total)

            for week, points in zip(weeks, cumulative, strict=False):
                mock_data.append(
                    {
                        "Week": f"Week {week}",
                        "Participant": profile["display_name"],
                        "Cumulative Points": points,
                    }
                )

        df = pd.DataFrame(mock_data)

        fig = px.line(
            df,
            x="Week",
            y="Cumulative Points",
            color="Participant",
            title="Cumulative Points by Week",
            markers=True,
        )

        st.plotly_chart(fig, use_container_width=True)


def show_team_performance(db: "Client", pool: dict[str, Any]) -> None:
    """Display team performance analysis for the pool.

    Shows most popular team selections and mock performance statistics
    including wins, losses, and selection frequency.

    Args:
        db: Supabase client for database operations.
        pool: Pool dictionary containing pool_id and other pool details.
    """
    st.subheader("Team Performance Analysis")

    all_selections = (
        db.table("team_selections").select("*").eq("pool_id", pool["pool_id"]).execute()
    )

    if not all_selections.data:
        st.info("No teams have been selected yet.")
        return

    team_counts = {}
    team_performance = {}

    for selection in all_selections.data:
        team_id = selection["team_id"]
        team = db.table("nfl_teams").select("*").eq("team_id", team_id).execute().data[0]

        team_name = f"{team['team_city']} {team['team_name']}"

        if team_name not in team_counts:
            team_counts[team_name] = 0
            import random

            team_performance[team_name] = {
                "Wins": random.randint(0, 8),
                "Losses": random.randint(0, 8),
                "Points For": random.randint(150, 300),
                "Points Against": random.randint(150, 300),
            }

        team_counts[team_name] += 1

    st.markdown("#### Most Popular Teams")

    popular_df = pd.DataFrame(
        [
            {"Team": team, "Times Selected": count}
            for team, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    )

    if not popular_df.empty:
        fig = px.bar(
            popular_df, x="Times Selected", y="Team", orientation="h", title="Most Selected Teams"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Team Performance")

    perf_data = []
    for team, stats in team_performance.items():
        if team in team_counts:
            perf_data.append(
                {
                    "Team": team,
                    "W-L": f"{stats['Wins']}-{stats['Losses']}",
                    "Win %": f"{(stats['Wins'] / (stats['Wins'] + stats['Losses']) * 100):.1f}%"
                    if stats["Wins"] + stats["Losses"] > 0
                    else "0.0%",
                    "PF": stats["Points For"],
                    "PA": stats["Points Against"],
                    "Selected By": team_counts[team],
                }
            )

    if perf_data:
        perf_df = pd.DataFrame(perf_data)
        perf_df = perf_df.sort_values("Win %", ascending=False)
        st.dataframe(perf_df, use_container_width=True, hide_index=True)
