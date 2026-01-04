import streamlit as st
import os
from dotenv import load_dotenv
from google_cal_service import GoogleCalendarService
from leaguepedia_client import get_upcoming_matches, get_tournament
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PROJECT_ID = os.getenv("PROJECT_ID")
URI= os.getenv("URI")

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
            URI,
        ],
        "javascript_origins": [
            URI
        ]
    }
}

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Login Flow
flow = Flow.from_client_config(
    CLIENT_CONFIG,
    scopes=SCOPES,
    redirect_uri=URI
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
        st.write("Please login to your calendar to continue:")
        st.link_button("Login with Google", auth_url)

# Once connected
else:
    st.success("✅ You are connected to Google Calendar!")
    
    # Initialize Google Calendar API service
    service = build('calendar', 'v3', credentials=st.session_state.credentials)
    
    # --- YOUR SYNC INTERFACE ---
    st.divider()
    league = st.multiselect("Select the league to synchronize", ["LFL", "LEC", "LCK", "LPL"])
    
    cal_manager = GoogleCalendarService(st.session_state.credentials)
    if st.button(f"Import {league} matches"):
        tournaments = get_tournament(league)
        tournament_names = [t[1] for t in tournaments]
        matches = get_upcoming_matches(tournament_names)
        
        existing_ids = cal_manager.get_existing_ids(days_ahead=60)
        
        new_events_count = 0
        for match in matches:
            if match['match_id'] not in existing_ids:
                cal_manager.create_match_event({'title': match})
                new_events_count += 1
        
        st.success(f"Import completed! {new_events_count} new events added to your calendar.")

    if st.button("Disconnect"):
        del st.session_state.credentials
        st.rerun()