import streamlit as st
from supabase import create_client
import os
import numpy as np; 
from datetime import datetime
now = datetime.now()    

st.write( now )

# Supabase credentials
SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"

SUPABASE_URL = "https://krpvkkctdsqrfwthvndz.supabase.co"
SUPABASE_KEY = "sb_publishable_OQiidfTH2UMDKCwmDs6p7Q_Inzs0Z2D" # YOUR_ANON_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Cherish Chef")

# Input form
with st.form("add_message"):
    text = st.text_input("Message")
    submitted = st.form_submit_button("Add")

    if submitted and text:
        supabase.table("messages").insert({"text": text}).execute()
        st.success("Message added!")

st.divider()

# Fetch records
response = supabase.table("messages").select("*").order(
    "created_at", desc=True
).execute()

# Display records
for msg in response.data:
    st.write(f"• {msg['text']}")
