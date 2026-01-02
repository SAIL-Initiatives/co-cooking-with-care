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

# --- Form to add a post ---
st.subheader("Add a Post")
with st.form("add_post"):
    content = st.text_area("Please tell us your story")

    user_name = st.text_input(
        "Your name (optional)"
    )
    
    sharable  = st.checkbox("If someone shares your story again, they must mention your name.")
    st.markdown("We believe your story belongs to you. If others share it, they should be encouraged to mention you.<br />")
    
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
                "user_name": user_name,
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
        if st.button( "Like Post"):
            # Increment likes by 1
            supabase.table("Posts").update({"likes": p["likes"] + 1}).eq("post_id", p["post_id"]).execute()
            st.rerun()  # Refresh to show updated likes
        st.markdown("---")
 
else:
    st.info("No posts yet.")
