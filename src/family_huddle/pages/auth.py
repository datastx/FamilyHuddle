"""Authentication and profile management pages."""

import streamlit as st
import bcrypt
from datetime import datetime


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def show_login(db):
    """Show login/signup page."""
    st.title("🏈 Family Football Pool")
    st.markdown("### Welcome! Please login or create an account to continue.")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if email and password:
                    # Query user from database
                    result = db.table('users').select("*").eq('email', email).execute()
                    
                    if result.data and verify_password(password, result.data[0]['password_hash']):
                        user = result.data[0]
                        st.session_state.authenticated = True
                        st.session_state.user_id = user['user_id']
                        st.session_state.user_email = user['email']
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
                else:
                    st.error("Please enter both email and password")
    
    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submitted:
                # Validation
                if not all([new_email, new_password, confirm_password, first_name, last_name]):
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    # Check if user exists
                    existing = db.table('users').select("*").eq('email', new_email).execute()
                    
                    if existing.data:
                        st.error("An account with this email already exists")
                    else:
                        # Create new user
                        hashed_pw = hash_password(new_password)
                        
                        user_data = {
                            'email': new_email,
                            'password_hash': hashed_pw,
                            'first_name': first_name,
                            'last_name': last_name,
                            'is_active': True,
                            'email_verified': False
                        }
                        
                        result = db.table('users').insert(user_data)
                        
                        if result.data:
                            # Create default profile with first and last name
                            profile_data = {
                                'user_id': result.data[0]['user_id'],
                                'profile_name': f"{first_name} {last_name}",
                                'display_name': f"{first_name} {last_name}"
                            }
                            db.table('profiles').insert(profile_data)
                            
                            st.success("Account created successfully! Please log in.")
                            st.info("A default profile has been created for you.")
                        else:
                            st.error("Error creating account. Please try again.")


def show_profile(db):
    """Show user profile management page."""
    st.title("👤 Profile Management")
    
    user_id = st.session_state.user_id
    
    # Get user info
    user = db.table('users').select("*").eq('user_id', user_id).execute().data[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Information")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Name:** {user['first_name']} {user['last_name']}")
        st.write(f"**Member Since:** {user['created_at'][:10]}")
    
    with col2:
        st.subheader("Account Settings")
        if st.button("Change Password"):
            st.info("Password change functionality coming soon!")
    
    st.divider()
    
    # Profile Management
    st.subheader("My Profiles")
    st.info("You can create multiple profiles to participate in different pools.")
    
    # Get user profiles
    profiles = db.table('profiles').select("*").eq('user_id', user_id).execute()
    
    if profiles.data:
        # Display profiles in a table
        profile_data = []
        for profile in profiles.data:
            profile_data.append({
                "Profile Name": profile['profile_name'],
                "Display Name": profile['display_name'],
                "Created": profile['created_at'][:10]
            })
        
        st.dataframe(profile_data, use_container_width=True)
    
    # Add new profile
    st.subheader("Create New Profile")
    
    with st.form("new_profile_form"):
        profile_name = st.text_input("Profile Name (unique identifier)")
        display_name = st.text_input("Display Name (shown in pools)")
        submitted = st.form_submit_button("Create Profile")
        
        if submitted:
            if profile_name and display_name:
                # Check if profile name exists
                existing = db.table('profiles').select("*").eq(
                    'user_id', user_id
                ).eq('profile_name', profile_name).execute()
                
                if existing.data:
                    st.error("You already have a profile with this name")
                else:
                    profile_data = {
                        'user_id': user_id,
                        'profile_name': profile_name,
                        'display_name': display_name
                    }
                    
                    result = db.table('profiles').insert(profile_data)
                    
                    if result.data:
                        st.success("Profile created successfully!")
                        st.rerun()
                    else:
                        st.error("Error creating profile")
            else:
                st.error("Please fill in all fields")