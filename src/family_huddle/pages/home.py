"""Home page for the Family Football Pool application."""

from datetime import datetime
from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from supabase import Client


def show(db: "Client") -> None:
    """Display the home dashboard page.

    Shows user welcome message, pool statistics, quick action buttons,
    and recent activity for the current user profile.

    Args:
        db: Supabase client for database operations.
    """
    st.title("🏈 Family Football Pool - Home")

    user = db.table("users").select("*").eq("user_id", st.session_state.user_id).execute().data[0]
    st.markdown(f"### Welcome back, {user['first_name']}!")

    current_profile = st.session_state.current_profile

    if not current_profile:
        st.warning("Please select or create a profile to get started!")
        st.stop()

    col1, col2, col3 = st.columns(3)

    with col1:
        participant_count = (
            db.table("pool_participants")
            .select("*")
            .eq("profile_id", current_profile["profile_id"])
            .execute()
        )

        st.metric("Active Pools", len(participant_count.data) if participant_count.data else 0)

    with col2:
        selections = (
            db.table("team_selections")
            .select("*")
            .eq("profile_id", current_profile["profile_id"])
            .execute()
        )

        st.metric("Teams Selected", len(selections.data) if selections.data else 0)

    with col3:
        current_week = _get_current_week()
        st.metric("Current Week", f"Week {current_week}")

    st.divider()
    st.subheader("Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏆 Join a Pool")
        st.write("Browse available pools and join the competition!")
        if st.button("Browse Pools", use_container_width=True):
            st.info("Navigate to 'My Pools' to join or create pools")

    with col2:
        st.markdown("#### 🎯 Select Teams")
        st.write("Choose your teams for the pools you've joined")
        if st.button("Select Teams", use_container_width=True):
            st.info("Navigate to 'Team Selection' to pick your teams")

    st.divider()

    st.subheader("Recent Activity")

    pools_data = []
    participants = (
        db.table("pool_participants")
        .select("*")
        .eq("profile_id", current_profile["profile_id"])
        .execute()
    )

    if participants.data:
        for participant in participants.data:
            pool = db.table("pools").select("*").eq("pool_id", participant["pool_id"]).execute()

            if pool.data:
                pool_info = pool.data[0]
                scores = (
                    db.table("pool_scores")
                    .select("*")
                    .eq("pool_id", participant["pool_id"])
                    .eq("profile_id", current_profile["profile_id"])
                    .execute()
                )

                latest_score = scores.data[-1] if scores.data else None

                pools_data.append(
                    {
                        "Pool Name": pool_info["pool_name"],
                        "Season": pool_info["season_year"],
                        "Status": "Active" if pool_info["is_active"] else "Inactive",
                        "Total Points": latest_score["total_points"] if latest_score else 0,
                        "Rank": latest_score["rank_position"] if latest_score else "-",
                    }
                )

    if pools_data:
        st.dataframe(pools_data, use_container_width=True)
    else:
        st.info("You haven't joined any pools yet. Get started by joining or creating a pool!")

    st.divider()
    st.subheader("🏈 NFL Updates")
    st.info("NFL news and updates will appear here once the season starts!")


def _get_current_week() -> int:
    """Calculate the current NFL week based on season start date.

    Returns:
        int: Current NFL week number (0 if before season, 1-18 during season).
    """
    season_start = datetime(datetime.now().year, 9, 7)
    if datetime.now() < season_start:
        return 0

    weeks_elapsed = (datetime.now() - season_start).days // 7
    return min(max(1, weeks_elapsed + 1), 18)
