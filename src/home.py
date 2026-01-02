import streamlit as st
from supabase import create_client
import os
import numpy as np; 
from datetime import datetime

import uuid, json

now = datetime.now()    

st.write( now )

# Supabase credentials
# SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_URL = os.environ['SUPABASE_URL']   
SUPABASE_KEY = os.environ['SUPABASE_KEY']  # YOUR_ANON_KEY
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Cherish Chef")

# Session tracking
if "user" not in st.session_state:
    st.session_state.user = None

tabs= st.tabs(['Share', 'Users'] )



with tabs[1]:
    # --- Display users ---
    response = supabase.table("userprofiles").select("*").order("created_at", desc=True).execute()
    users = response.data
    
    if users:
        for p in users:
            timestamp = p['created_at']
            dt = datetime.fromisoformat( timestamp.replace("Z", "+00:00") )
            timestamp = dt.strftime("%b %d, %Y • %I:%M %p")
            st.html( '<hr>'+ timestamp + '<hr>' )
            
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
            #if user_id_input.strip() == "":
            
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
    
    
    

st.sidebar.header("Signup / Login")

choice = st.sidebar.radio("Choose", ["Login", "Signup", "Logout"])

if choice == "Signup":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    display_name = st.sidebar.text_input("Display Name")
    if st.sidebar.button("Signup"):
        response = supabase.auth.sign_up({"email": email, "password": password})
        user = response.user
        if user.id:
            st.write( uid:= user.id)
        else:
            uid = str(uuid.uuid4()) 
        if user:
            # Insert into Users table (UUID-based RLS)
            supabase.table("userprofiles").insert({
                "id": uid,
                "display_name": display_name
            }).execute()
            st.success("Signup successful! Please log in.")
            
elif choice == "Login":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = response.user
        if user:
            st.session_state.user = user
            st.success(f"Logged in as {user['email']}")
        else:
            st.error("Login failed")

elif choice == "Logout":
    if st.sidebar.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.success("Logged out!")
