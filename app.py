import streamlit as st
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PROJECT_ID = os.getenv("PROJECT_ID")

st.title("Esports Schedule Aggregator 📅")

# OAuth 2.0 Configuration
CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "project_id": PROJECT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": CLIENT_SECRET,
        "redirect_uris": [
            "http://localhost:8501",
        ],
        "javascript_origins": [
            "http://localhost:8501"
        ]
    }
}

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Login Flow
flow = Flow.from_client_config(
    CLIENT_CONFIG,
    scopes=SCOPES,
    redirect_uri='http://localhost:8501'
)

# Authentication Steps
if 'credentials' not in st.session_state:
    query_params = st.query_params
    if "code" in query_params:
        # Token exchange
        flow.fetch_token(code=query_params["code"])
        st.session_state.credentials = flow.credentials

        # URL cleanup
        st.query_params.clear()
        st.rerun()
    else:
        # Display login button if no code present
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.write("Connecte ton calendrier pour commencer :")
        st.link_button("Se connecter à Google", auth_url)

# Once connected
else:
    st.success("✅ You are connected to Google Calendar!")
    
    # Initialize Google Calendar API service
    service = build('calendar', 'v3', credentials=st.session_state.credentials)
    
    # --- YOUR SYNC INTERFACE ---
    st.divider()
    league = st.multiselect("Select the league to synchronize", ["LFL", "LEC", "LCK", "LPL"])
    
    if st.button(f"Import {league} matches"):
        st.write(f"Searching for {league} matches on Leaguepedia...")
        # Here you will call your fetch and insert functions
        # matches = get_upcoming_matches(league)
        # ...
        st.info("Sync functionality is under development!")

    if st.button("Disconnect"):
        del st.session_state.credentials
        st.rerun()