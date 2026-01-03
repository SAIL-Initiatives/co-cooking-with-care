import streamlit as st
from supabase import create_client
import os
import numpy as np; 
from datetime import datetime

import uuid, json

now = datetime.now()    


# Supabase credentials
# SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_URL = os.environ['SUPABASE_URL']   
SUPABASE_KEY = os.environ['SUPABASE_KEY']  # YOUR_ANON_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Cherish Chef")

# Session tracking
if "user" not in st.session_state:
    st.session_state.user = None

tabs= st.tabs(['Share', 'Signup', 'System history' ] )

if 0:
    '''
    id='44da6b55-f712-4cd1-8d18-b49beeb0457b' 
    app_metadata={'provider': 'email', 'providers': ['email']} 
    user_metadata={'email': '1470pancake@gmail.com', 'email_verified': False, 
    'phone_verified': False, 'sub': '44da6b55-f712-4cd1-8d18-b49beeb0457b'}
    
    aud='authenticated' 
    confirmation_sent_at=datetime.datetime(2026, 1, 2, 7, 26, 23, 473154, tzinfo=TzInfo(0)) 
    recovery_sent_at=None email_change_sent_at=None new_email=None new_phone=None 
    invited_at=None action_link=None email='1470pancake@gmail.com' phone='' 
    
    created_at=datetime.datetime(2026, 1, 2, 7, 26, 23, 458624, tzinfo=TzInfo(0)) 
    confirmed_at=None email_confirmed_at=None phone_confirmed_at=None last_sign_in_at=None 
    role='authenticated' updated_at=datetime.datetime(2026, 1, 2, 7, 26, 24, 634023, tzinfo=TzInfo(0)) 
    identities=[UserIdentity(id='44da6b55-f712-4cd1-8d18-b49beeb0457b', 
    identity_id='e6cf7f9d-e6db-4db5-9c19-ba558a28f93d', 
    user_id='44da6b55-f712-4cd1-8d18-b49beeb0457b',
    
    identity_data={'email': '1470pancake@gmail.com', 'email_verified': False, 
    'phone_verified': False, 'sub': '44da6b55-f712-4cd1-8d18-b49beeb0457b'}, 
    provider='email', created_at=datetime.datetime(2026, 1, 2, 7, 26, 23, 469418, tzinfo=TzInfo(0)), 
    last_sign_in_at=datetime.datetime(2026, 1, 2, 7, 26, 23, 469366, tzinfo=TzInfo(0)), 
    updated_at=datetime.datetime(2026, 1, 2, 7, 26, 23, 469418, tzinfo=TzInfo(0)))] 
    is_anonymous=False 
    factors=None
    
    
    44da6b55-f712-4cd1-8d18-b49beeb0457b
    '''

with tabs[0]:
    # --- Display posts ---
    response = supabase.table("posts").select("*").order("created_at", desc=True).execute()
    posts = response.data
    
    if posts:
        st.subheader("Recent Posts")
        for p in posts:
            timestamp = p['created_at']
            dt = datetime.fromisoformat( timestamp.replace("Z", "+00:00") )
    
            timestamp = dt.strftime("%b %d, %Y • %I:%M %p")
            #**ID:** {p['post_id']} 
            
            st.markdown(f"**Created:** {timestamp} | **Author's name:** {p['display_name']}")
            st.html( '<hr>'+ p["content"] + '<hr>' )
            if p['sharable']: 
                st.html("Shared with care. Please mention the author whenever you repost it." )
            n=p['likes']
            st.markdown( f"**{n} Likes**")
            
            # Like button
            if st.button( "Like Post", key=p['post_id']+'_like_button' ):
                # Increment likes by 1
                supabase.table("posts").update({"likes": p["likes"] + 1}).eq("post_id", p["post_id"]).execute()
                st.rerun()  # Refresh to show updated likes
            st.markdown("---")
    else:
        st.info("No posts yet.")
    
    st.divider()
    st.subheader("Add a Post")
    with st.form("add_post"):
        content = st.text_area("Please tell us your story")
    
        display_name = st.text_input(
            "Your display name"
        )
        
        sharable = st.checkbox("If someone shares your story again, they must mention your name.")
        sharable = int( sharable )
        st.html("<p>We believe your story belongs to you. If others share it, they should be encouraged to mention you.</p>")
        
        submitted = st.form_submit_button("Submit")
    
        if submitted:            
            post_id = str(uuid.uuid4())  # generate random UUID
              
            # Insert record
            supabase.table("posts").insert(
                {
                    "post_id": post_id,
                    "content": content, 
                    "sharable": sharable,
                    "display_name": display_name,
                    "likes": 0,
                }
            ).execute()
            st.success("Post added successfully!")
            st.rerun()
    
    
with tabs[1]: #st.sidebar.header("Signup / Login")

    choice = st.radio("Choose", ["Login", "Signup", "Logout"])
    
    if choice == "Signup":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        display_name = st.text_input("Display Name")
        if st.button("Signup"):
            response = supabase.auth.sign_up({"email": email, "password": password})
            user = response.user
            st.text( f'User ID: {user.id}' ) 
            
            if user:
                # Insert into Users table (UUID-based RLS)
                supabase.table("userprofiles").insert({
                    "id": user.id,
                    "email": email,
                    "display_name": display_name
                }).execute()
                st.success("Signup successful! Please log in.")
                
    elif choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = response.user
            if user:
                st.session_state.user = user
                st.write(f"Logged in as {user.email}")
                st.success(f"Logged in as {user.email}")
            else:
                st.error("Login failed")
    
    elif choice == "Logout":
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.success("Logged out!")



with tabs[2]:
    # --- Display users ---
    response = supabase.table("userprofiles").select("*").order("created_at", desc=True).execute()
    users = response.data
    
    if users:
        for p in users:
            timestamp = p['created_at']
            dt = datetime.fromisoformat( timestamp.replace("Z", "+00:00") )
            timestamp = dt.strftime("%b %d, %Y • %I:%M %p")
            st.html( f'<hr/>Last account signup by {p['display_name']} at {timestamp}<hr/>' )
            
st.html('<hr/>')
st.write( f"System's time: {now}" )
st.write( 'URL: https://sail-initiatives-mvp.share.connect.posit.cloud' )
