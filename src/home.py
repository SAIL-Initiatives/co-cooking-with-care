import streamlit as st
from supabase import create_client
import os
import numpy as np; 
from datetime import datetime

import uuid, json

now = datetime.now()    

st.write( now )

# Supabase credentials
SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_KEY = os.environ['SUPABASE_KEY']  # YOUR_ANON_KEY
SUPABASE_URL = "https://krpvkkctdsqrfwthvndz.supabase.co"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Cherish Chef")


# --- Form to add a post ---
st.subheader("Add a Post")
with st.form("add_post"):
    user_id_input = st.text_input(
        "User ID (optional, leave blank for random UUID)"
    )
    content = st.text_area("Tell us your story")
    
    submitted = st.form_submit_button("Submit")

    if submitted:
        # Handle user_id
        if user_id_input.strip() == "":
            user_id_input = str(uuid.uuid4())  # generate random UUID
          
        # Insert record
        supabase.table("Posts").insert(
            {
                "user_id": user_id_input,
                "content": content,
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
        st.markdown(f"**ID:** {p['id']} | **Created:** {p['created_at']} | **User ID:** {p['user_id']}")
        st.html( '<hr>'+ p["content"] + '<hr>' )
        st.markdown( f"**Likes:** {p['likes']}")
        
        # Like button
        if st.button(f"Like Post {p['id']}"):
            # Increment likes by 1
            supabase.table("Posts").update({"likes": p["likes"] + 1}).eq("id", p["id"]).execute()
            st.rerun()  # Refresh to show updated likes
        st.markdown("---")
 
else:
    st.info("No posts yet.")
