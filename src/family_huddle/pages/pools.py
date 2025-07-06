"""Pool management page."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

import streamlit as st

if TYPE_CHECKING:
    from supabase import Client


def show(db: "Client") -> None:
    """Display the pool management interface with tabbed navigation.

    Renders tabs for viewing user's pools, joining new pools, and creating pools.

    Args:
        db: Supabase client for database operations.
    """
    st.title("🏆 My Pools")

    current_profile = st.session_state.current_profile

    if not current_profile:
        st.warning("Please select or create a profile first!")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["My Pools", "Join Pool", "Create Pool"])

    with tab1:
        show_my_pools(db, current_profile)

    with tab2:
        show_join_pool(db, current_profile)

    with tab3:
        show_create_pool(db)


def show_my_pools(db: "Client", current_profile: dict[str, Any]) -> None:
    """Display pools that the current user profile is participating in.

    Shows pool details, user's team selections, and status for each pool.

    Args:
        db: Supabase client for database operations.
        current_profile: Current user profile containing profile_id.
    """
    st.subheader("Pools I'm Participating In")

    participants = (
        db.table("pool_participants")
        .select("*")
        .eq("profile_id", current_profile["profile_id"])
        .execute()
    )

    if not participants.data:
        st.info("You haven't joined any pools yet. Check the 'Join Pool' tab to get started!")
        return

    for participant in participants.data:
        pool_result = db.table("pools").select("*").eq("pool_id", participant["pool_id"]).execute()

        if not pool_result.data:
            continue

        pool = pool_result.data[0]

        with st.expander(f"🏈 {pool['pool_name']} ({pool['season_year']})"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Description:** {pool['pool_description'] or 'No description'}")
                st.write(f"**Entry Fee:** ${pool['entry_fee']}")
                st.write(f"**Max Participants:** {pool['max_participants']}")

            with col2:
                st.write(f"**Status:** {'✅ Active' if pool['is_active'] else '❌ Inactive'}")
                joined_date = participant.get("joined_at", participant.get("created_at", ""))
                st.write(f"**Joined:** {joined_date[:10] if joined_date else 'Unknown'}")
                st.write(
                    f"**Teams Selected:** {'✅ Yes' if participant['selections_complete'] else '❌ No'}"
                )

            selections = (
                db.table("team_selections")
                .select("*")
                .eq("pool_id", pool["pool_id"])
                .eq("profile_id", current_profile["profile_id"])
                .execute()
            )

            if selections.data:
                st.write("**Your Teams:**")
                teams = []
                for selection in sorted(selections.data, key=lambda x: x["selection_order"]):
                    team_result = (
                        db.table("nfl_teams")
                        .select("*")
                        .eq("team_id", selection["team_id"])
                        .execute()
                    )

                    if team_result.data:
                        team = team_result.data[0]
                        team_points = team.get("points", 0)
                        teams.append(
                            f"{selection['selection_order']}. {team['team_city']} {team['team_name']} ({team_points} pts)"
                        )
                    else:
                        teams.append(f"{selection['selection_order']}. Unknown Team")

                for team in teams:
                    st.write(f"  {team}")

            col1, col2 = st.columns(2)
            with col1:
                if not participant["selections_complete"] and st.button(
                    "Select Teams", key=f"select_{pool['pool_id']}"
                ):
                    st.info("Go to 'Team Selection' page to pick your teams")

            with col2:
                if st.button("View Leaderboard", key=f"leader_{pool['pool_id']}"):
                    st.info("Go to 'Leaderboards' page to see rankings")


def show_join_pool(db: "Client", current_profile: dict[str, Any]) -> None:
    """Display available pools that the user can join.

    Lists active pools excluding those the user has already joined,
    with join functionality and participant counts.

    Args:
        db: Supabase client for database operations.
        current_profile: Current user profile containing profile_id.
    """
    st.subheader("Available Pools")

    pools = db.table("pools").select("*").eq("is_active", True).execute()

    if not pools.data:
        st.info("No active pools available at the moment.")
        return

    my_pools = (
        db.table("pool_participants")
        .select("pool_id")
        .eq("profile_id", current_profile["profile_id"])
        .execute()
    )

    my_pool_ids = [p["pool_id"] for p in my_pools.data] if my_pools.data else []

    available_pools = [p for p in pools.data if p["pool_id"] not in my_pool_ids]

    if not available_pools:
        st.info("You've already joined all available pools!")
        return

    for pool in available_pools:
        participants = (
            db.table("pool_participants").select("*").eq("pool_id", pool["pool_id"]).execute()
        )

        participant_count = len(participants.data) if participants.data else 0

        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"### {pool['pool_name']}")
                st.write(pool["pool_description"] or "No description provided")
                st.write(f"Season: {pool['season_year']} | Entry Fee: ${pool['entry_fee']}")

            with col2:
                st.metric("Participants", f"{participant_count}/{pool['max_participants']}")

            with col3:
                if participant_count < pool["max_participants"]:
                    if st.button("Join Pool", key=f"join_{pool['pool_id']}"):
                        participant_data = {
                            "pool_id": pool["pool_id"],
                            "profile_id": current_profile["profile_id"],
                            "selections_complete": False,
                            "joined_at": datetime.now().isoformat(),
                        }

                        result = db.table("pool_participants").insert(participant_data).execute()

                        if result.data:
                            st.success(f"Successfully joined {pool['pool_name']}!")
                            st.rerun()
                        else:
                            st.error("Failed to join pool. Please try again.")
                else:
                    st.write("**FULL**")

            st.divider()


def show_create_pool(db: "Client") -> None:
    """Display the pool creation form.

    Allows users to create new pools with custom settings including
    entry fee, participant limits, and registration deadlines.

    Args:
        db: Supabase client for database operations.
    """
    st.subheader("Create New Pool")

    with st.form("create_pool_form"):
        pool_name = st.text_input("Pool Name", placeholder="Family Football 2024")
        pool_description = st.text_area("Description", placeholder="Annual family football pool")

        col1, col2 = st.columns(2)

        with col1:
            season_year = st.number_input(
                "Season Year",
                min_value=datetime.now().year,
                max_value=datetime.now().year + 1,
                value=datetime.now().year,
            )
            entry_fee = st.number_input("Entry Fee ($)", min_value=0.0, value=0.0, step=5.0)

        with col2:
            max_participants = st.number_input(
                "Max Participants", min_value=2, max_value=100, value=20
            )
            deadline_days = st.number_input(
                "Registration deadline (days from now)", min_value=1, max_value=30, value=7
            )

        submitted = st.form_submit_button("Create Pool", use_container_width=True)

        if submitted:
            if not pool_name:
                st.error("Please enter a pool name")
            else:
                deadline = datetime.now() + timedelta(days=deadline_days)

                pool_data = {
                    "pool_name": pool_name,
                    "pool_description": pool_description,
                    "created_by": st.session_state.user_id,
                    "season_year": season_year,
                    "entry_fee": entry_fee,
                    "max_participants": max_participants,
                    "registration_deadline": deadline.isoformat(),
                    "is_active": True,
                }

                result = db.table("pools").insert(pool_data).execute()

                if result.data:
                    participant_data = {
                        "pool_id": result.data[0]["pool_id"],
                        "profile_id": st.session_state.current_profile["profile_id"],
                        "selections_complete": False,
                        "joined_at": datetime.now().isoformat(),
                    }

                    db.table("pool_participants").insert(participant_data).execute()

                    st.success(
                        f"Pool '{pool_name}' created successfully! You've been automatically added as a participant."
                    )
                    st.rerun()
                else:
                    st.error("Failed to create pool. Please try again.")
