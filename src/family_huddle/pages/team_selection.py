"""Team selection page."""

import streamlit as st
from family_huddle.services.nfl_data import nfl_data


def show(db):
    """Display the team selection page."""
    st.title("🎯 Team Selection")
    
    current_profile = st.session_state.current_profile
    
    if not current_profile:
        st.warning("Please select or create a profile first!")
        st.stop()
    
    participants = db.table('pool_participants').select("*").eq(
        'profile_id', current_profile['profile_id']
    ).execute()
    
    if not participants.data:
        st.info("You haven't joined any pools yet. Check the 'My Pools' tab to join a pool!")
        return
    
    pool_options = []
    pool_map = {}
    
    for participant in participants.data:
        pool = db.table('pools').select("*").eq(
            'pool_id', participant['pool_id']
        ).execute().data[0]
        
        pool_name = f"{pool['pool_name']} ({pool['season_year']})"
        pool_options.append(pool_name)
        pool_map[pool_name] = pool
    
    selected_pool_name = st.selectbox("Select Pool", pool_options)
    selected_pool = pool_map[selected_pool_name]
    
    st.divider()
    
    st.subheader(f"Team Selection for: {selected_pool['pool_name']}")
    
    current_participant = next((p for p in participants.data if p['pool_id'] == selected_pool['pool_id']), None)
    selections_complete = current_participant and current_participant.get('selections_complete', False)
    
    if selections_complete:
        st.info("✅ You have completed your team selections for this pool. You can modify them below if needed.")
    else:
        st.info("Select exactly 4 teams for this pool. Choose wisely!")
    
    current_selections = db.table('team_selections').select("*").eq(
        'pool_id', selected_pool['pool_id']
    ).eq('profile_id', current_profile['profile_id']).execute()
    
    selected_team_ids = [s['team_id'] for s in current_selections.data] if current_selections.data else []
    
    teams_df = nfl_data.import_teams()
    
    existing_teams = db.table('nfl_teams').select("*").execute()
    
    if not existing_teams.data:
        for _, team in teams_df.iterrows():
            team_data = {
                'team_code': team['team_code'],
                'team_name': team['team_name'],
                'team_city': team['team_city'],
                'conference': team['conference'],
                'division': team['division'],
                'points': team.get('points', 5),
                'is_active': True
            }
            db.table('nfl_teams').insert(team_data)
    
    all_teams = db.table('nfl_teams').select("*").execute().data
    
    conferences = {'AFC': {}, 'NFC': {}}
    
    for team in all_teams:
        conf = team['conference']
        div = team['division']
        
        if div not in conferences[conf]:
            conferences[conf][div] = []
        
        conferences[conf][div].append(team)
    
    st.markdown(f"### Current Selections ({len(selected_team_ids)}/4)")
    
    if selected_team_ids:
        selected_teams = []
        for team_id in selected_team_ids:
            team = next((t for t in all_teams if t.get('team_id') == team_id), None)
            if team:
                selected_teams.append(team)
        
        if selected_teams:
            total_points = sum(team.get('points', 0) for team in selected_teams)
            for i, team in enumerate(selected_teams):
                team_points = team.get('points', 0)
                st.write(f"{i+1}. {team['team_city']} {team['team_name']} ({team_points} pts)")
            st.info(f"**Total Points: {total_points}**")
        else:
            st.warning(f"Could not find team details for selected team IDs: {selected_team_ids}")
            st.write("Please re-initialize your data with `make init-data`")
    else:
        st.write("No teams selected yet")
    
    st.divider()
    
    tab1, tab2 = st.tabs(["AFC", "NFC"])
    
    selected_teams = []
    
    with tab1:
        show_conference_teams(db, "AFC", conferences["AFC"], selected_team_ids, selected_teams)
    
    with tab2:
        show_conference_teams(db, "NFC", conferences["NFC"], selected_team_ids, selected_teams)
    
    st.divider()
    
    if st.button("🔄 Clear Cache & Refresh", help="Clear Streamlit cache and refresh data"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Selections", type="secondary", use_container_width=True):
            db.table('team_selections').eq(
                'pool_id', selected_pool['pool_id']
            ).eq('profile_id', current_profile['profile_id']).delete()
            
            db.table('pool_participants').eq(
                'pool_id', selected_pool['pool_id']
            ).eq('profile_id', current_profile['profile_id']).update({
                'selections_complete': False
            })
            
            st.success("Selections cleared!")
            st.rerun()
    
    with col2:
        save_button_text = "Update Selections" if selections_complete else "Save Selections"
        if st.button(save_button_text, type="primary", use_container_width=True):
            all_selected = []
            
            name_to_id = {}
            for team in all_teams:
                team_points = team.get('points', 0)
                team_name = f"{team['team_city']} {team['team_name']} ({team_points} pts)"
                name_to_id[team_name] = team['team_id']
            
            for conf in ["AFC", "NFC"]:
                for div in ["East", "North", "South", "West"]:
                    key = f"team_{conf}_{div}"
                    if key in st.session_state and st.session_state[key]:
                        for team_name in st.session_state[key]:
                            if team_name in name_to_id:
                                all_selected.append(name_to_id[team_name])
            
            if len(all_selected) != 4:
                st.error(f"Please select exactly 4 teams. You've selected {len(all_selected)}.")
            else:
                db.table('team_selections').eq(
                    'pool_id', selected_pool['pool_id']
                ).eq('profile_id', current_profile['profile_id']).delete()
                
                for i, team_id in enumerate(all_selected):
                    selection_data = {
                        'pool_id': selected_pool['pool_id'],
                        'profile_id': current_profile['profile_id'],
                        'team_id': team_id,
                        'selection_order': i + 1
                    }
                    db.table('team_selections').insert(selection_data)
                
                db.table('pool_participants').eq(
                    'pool_id', selected_pool['pool_id']
                ).eq('profile_id', current_profile['profile_id']).update({
                    'selections_complete': True
                })
                
                success_message = "Teams updated successfully!" if selections_complete else "Teams saved successfully!"
                st.success(success_message)
                st.balloons()
                st.rerun()


def show_conference_teams(db, conference, divisions, already_selected, selected_teams):
    """Show teams for a conference organized by division."""
    
    for division, teams in divisions.items():
        st.markdown(f"#### {conference} {division}")
        
        team_options = []
        team_map = {}
        
        for team in sorted(teams, key=lambda x: x['team_city']):
            team_points = team.get('points', 0)
            team_name = f"{team['team_city']} {team['team_name']} ({team_points} pts)"
            team_options.append(team_name)
            team_map[team_name] = team['team_id']
        
        default = []
        for team_name, team_id in team_map.items():
            if team_id in already_selected or team_name in already_selected:
                default.append(team_name)
        
        selected = st.multiselect(
            f"Select from {conference} {division}",
            options=team_options,
            default=default,
            key=f"team_{conference}_{division}",
            label_visibility="collapsed"
        )
        
        for team_name in selected:
            if team_map[team_name] not in selected_teams:
                selected_teams.append(team_map[team_name])