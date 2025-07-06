"""Main Streamlit application for Family Football Pool."""

from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from supabase import Client

from family_huddle.pages import auth, home, leaderboard, pools, team_selection
from family_huddle.services.database import create_client

# Load environment variables for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available in production (Streamlit Cloud)
    pass


st.set_page_config(
    page_title="🏈 Family Huddle 🏈",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def init_database() -> "Client":
    """Initialize and cache the Supabase database client.

    Returns:
        Client: Cached Supabase client instance for database operations.
    """
    return create_client()


def init_session_state() -> None:
    """Initialize Streamlit session state variables with default values.

    Sets up session state for authentication, user ID, current profile,
    and user email if not already present.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "current_profile" not in st.session_state:
        st.session_state.current_profile = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None


def main() -> None:
    """Main application entry point and routing logic.

    Handles authentication flow, profile selection, navigation menu,
    and page routing based on user selections.
    """
    init_session_state()
    db = init_database()

    if not st.session_state.authenticated:
        auth.show_login(db)
        return

    st.sidebar.title("🏈 Family Huddle")
    st.sidebar.markdown(f"**User:** {st.session_state.user_email}")

    if st.session_state.authenticated:
        profiles = (
            db.table("profiles").select("*").eq("user_id", st.session_state.user_id).execute()
        )

        if profiles.data:
            profile_names = [p["profile_name"] for p in profiles.data]
            selected_profile = st.sidebar.selectbox(
                "Active Profile:",
                options=profile_names,
                index=0
                if not st.session_state.current_profile
                else profile_names.index(st.session_state.current_profile["profile_name"]),
            )

            for profile in profiles.data:
                if profile["profile_name"] == selected_profile:
                    st.session_state.current_profile = profile
                    break

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "🏆 My Pools", "🎯 Team Selection", "📊 Leaderboards", "👤 Profile"],
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    if page == "🏠 Home":
        home.show(db)
    elif page == "🏆 My Pools":
        pools.show(db)
    elif page == "🎯 Team Selection":
        team_selection.show(db)
    elif page == "📊 Leaderboards":
        leaderboard.show(db)
    elif page == "👤 Profile":
        auth.show_profile(db)


if __name__ == "__main__":
    main()
