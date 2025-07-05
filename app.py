"""Main Streamlit application for Family Football Pool."""

import streamlit as st

from family_huddle.services.local_db import create_client
from family_huddle.pages import auth, home, pools, team_selection, leaderboard


st.set_page_config(
    page_title="🏈 Family Huddle 🏈",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_database():
    """Initialize the local database."""
    return create_client("local", "local")

def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'current_profile' not in st.session_state:
        st.session_state.current_profile = None
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

def main():
    """Main application entry point."""
    init_session_state()
    db = init_database()
    
    if not st.session_state.authenticated:
        auth.show_login(db)
        return
    
    st.sidebar.title("🏈 Family Huddle")
    st.sidebar.markdown(f"**User:** {st.session_state.user_email}")
    
    if st.session_state.authenticated:
        profiles = db.table('profiles').select("*").eq(
            'user_id', st.session_state.user_id
        ).execute()
        
        if profiles.data:
            profile_names = [p['profile_name'] for p in profiles.data]
            selected_profile = st.sidebar.selectbox(
                "Active Profile:",
                options=profile_names,
                index=0 if not st.session_state.current_profile else 
                      profile_names.index(st.session_state.current_profile['profile_name'])
            )
            
            for profile in profiles.data:
                if profile['profile_name'] == selected_profile:
                    st.session_state.current_profile = profile
                    break
    
    st.sidebar.divider()
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "🏆 My Pools", "🎯 Team Selection", "📊 Leaderboards", "👤 Profile"]
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