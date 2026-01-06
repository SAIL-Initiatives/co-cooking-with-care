import streamlit as st
from supabase import create_client
import os
import numpy as np; 
from datetime import datetime
from streamlit_quill import st_quill


import uuid, json, base64
import requests
from bs4 import BeautifulSoup 

    
        
def process_images(html, supabase):
    img_pattern = r'<img src="data:image/(png|jpeg);base64,([^"]+)"'
    matches = re.findall(img_pattern, html)

    for img_type, img_data in matches:
        img_bytes = base64.b64decode(img_data)
        filename = f"editor/{uuid.uuid4()}.{img_type}"

        supabase.storage.from_("uploads").upload(
            filename,
            img_bytes,
            file_options={"content-type": f"image/{img_type}"}
        )

        public_url = supabase.storage.from_("uploads").get_public_url(filename)
        html = html.replace(
            f"data:image/{img_type};base64,{img_data}",
            public_url
        )
    return html


def fetch_link_preview(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    res = requests.get(
        url,
        headers=headers,
        timeout=8,
        allow_redirects=True
    )

    soup = BeautifulSoup(res.text, "html.parser")

    def meta(prop):
        tag = soup.find("meta", property=prop)
        return tag["content"] if tag else None

    return {
        "final_url": res.url,
        "title": meta("og:title"),
        "description": meta("og:description"),
        "image": meta("og:image"),
    }

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

tabs= st.tabs(['Share', 'Signup to join/host a cooking event', 'System history', 'Terms of services' ] )

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

    # url = st.text_input("Paste a link (Quora, Medium, etc.)")
    
    if 0:# st.button("Preview"):
        preview = fetch_link_preview(url)

        st.write( preview )
        st.subheader(preview["title"])
        st.write(preview["description"])
    
        if preview["image_url"]:
            st.image(preview["image_url"], width=400)
    
        if 0: #st.button("Save link"):
            user = supabase.auth.get_user()
            supabase.table("external_links").insert({
                "user_id": user.data.user.id,
                **preview
            }).execute()    
            st.success("Link saved!")
            
    st.subheader("Add a Post")
    with st.form("add_post"):        
        # content = st.text_area("Please tell us your story")

        content = st_quill(
            placeholder="Paste text or images here...",
            html=True
        )

        display_name = st.text_input(
            "Your display name"
        )

        
        sharable = st.checkbox("If someone shares your story, they should* credit you (for example, by mentioning your name). Check this box if you’d like to remain anonymous instead.")
        sharable = int( sharable )
        st.html("<p>*We believe your story belongs to you. If others reshare it, they should credit the original author whenever possible.</p>")
        
        submitted = st.form_submit_button("Submit")
    
        if submitted:            
            post_id = str(uuid.uuid4())  # generate random UUID
              
            # Insert record
            supabase.table("posts").insert(
                {
                    "post_id": post_id,
                    "content": content, 
                    "sharable": sharable,
                    "user_id": st.session_state["user"].id,
                    "display_name": display_name,
                    "likes": 0,
                }
            ).execute()
            st.success("Post added successfully!")
            st.rerun()
    
    
with tabs[1]: #st.sidebar.header("Signup / Login")

    

    if "user" in st.session_state:
        user = st.session_state['user']
        st.write( user ) 
        if st.button("Logout"):
            supabase.auth.sign_out()
            st.session_state.user = None
            st.success("Logged out!")        
    else:
        choice = st.radio("Choose", ["Login", "Signup"])
        if choice == "Signup":
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            display_name = st.text_input("Display Name")
            if st.button("Signup"):
                response = supabase.auth.sign_up({"email": email, "password": password})
                user = response.user
                st.text( f'User ID: {user.id}' ) 
                
                if user:
                    st.write( user ) 
                    
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
