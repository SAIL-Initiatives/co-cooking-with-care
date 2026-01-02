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

tabs= st.tabs(['Share', 'Events'] )

with tabs[1]:    
    # -----------------------
    # SIGNUP
    # -----------------------
    st.subheader("Sign Up")
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        display_name = st.text_input("Display Name")
        submit_signup = st.form_submit_button("Sign Up")
    
        if submit_signup:
            # 1️⃣ Sign up with Supabase Auth
            response = supabase.auth.sign_up({"email": email, "password": password})
            user = response.user
    
            if user:
                st.success("Signup successful! Check your email to confirm.")
    
                # 2️⃣ Insert into User table
                supabase.table("Users").insert({  # same UUID as auth
                    "email": email,
                    "display_name": display_name
                }).execute()
            else:
                st.error(f"Error: {response.get('error', 'Unknown error')}")
    
    # -----------------------
    # LOGIN
    # -----------------------
    st.subheader("Login")
    with st.form("login_form"):
        email_login = st.text_input("Email", key="email_login")
        password_login = st.text_input("Password", type="password", key="password_login")
        submit_login = st.form_submit_button("Login")
    
        if submit_login:
            response = supabase.auth.sign_in_with_password({
                "email": email_login,
                "password": password_login
            })
            if response.user:
                st.session_state.user = response.user
                st.success(f"Logged in as {response.user['email']}")
            else:
                st.error("Login failed. Check email/password.")
    
    # -----------------------
    # LOGOUT
    # -----------------------
    if st.session_state.user:
        st.write(f"Hello, {st.session_state.user['email']}")
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.rerun()


with tabs[0]:
    st.subheader("Add a Post")
    with st.form("add_post"):
        content = st.text_area("Please tell us your story")
    
        display_name = st.text_input(
            "Your display name"
        )
        
        sharable  = st.checkbox("If someone shares your story again, they must mention your name.")
        st.html("<p>We believe your story belongs to you. If others share it, they should be encouraged to mention you.</p>")
        
        submitted = st.form_submit_button("Submit")
    
        if submitted:
            #if user_id_input.strip() == "":
            
            post_id = str(uuid.uuid4())  # generate random UUID
              
            # Insert record
            supabase.table("Posts").insert(
                {
                    "post_id": post_id,
                    "content": content, 
                    "sharable": sharable,
                    "display_name": display_name,
                    "likes": 0,
                }
            ).execute()
            st.success("Post added successfully!")
    
    
    st.divider()
    
    # --- Display posts ---
    st.subheader("Recent Posts")
    response = supabase.table("Posts").select("*").order("created_at", desc=True).execute()
    posts = response.data
    
    if posts:
        for p in posts:
            timestamp = p['created_at']
            dt = datetime.fromisoformat( timestamp.replace("Z", "+00:00") )
    
            timestamp = dt.strftime("%b %d, %Y • %I:%M %p")
            #**ID:** {p['post_id']} 
            
            st.markdown(f"**Created:** {timestamp} | **User name:** {p['user_name']}")
            st.html( '<hr>'+ p["content"] + '<hr>' )
            if p['sharable']: 
                st.html("Shared with care. Please mention the author whenever you repost it." )
            n=p['likes']
            st.markdown( f"**{n} Likes**")
            
            # Like button
            if st.button( "Like Post", key=p['post_id']+'_like_button' ):
                # Increment likes by 1
                supabase.table("Posts").update({"likes": p["likes"] + 1}).eq("post_id", p["post_id"]).execute()
                st.rerun()  # Refresh to show updated likes
            st.markdown("---")
     
    else:
        st.info("No posts yet.")
