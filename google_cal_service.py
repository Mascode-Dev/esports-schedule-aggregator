from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build

class GoogleCalendarService:
    def __init__(self, credentials):
        """Initialize the service with credentials obtained via Streamlit."""
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_existing_ids(self, days_ahead=30):
        """
        Retrieve the IDs of matches already present in the calendar 
        for avoiding duplicates.
        """
        now = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
        
        limit_date = (datetime.utcnow() + timedelta(days=days_ahead)).replace(microsecond=0).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=limit_date,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        existing_ids = set()

        for event in events:
            desc = event.get('description', '')
            if "Match ID:" in desc:
                # Extraction de l'ID après "Match ID: "
                try:
                    m_id = desc.split("Match ID: ")[1].split("\n")[0].strip()
                    existing_ids.add(m_id)
                except IndexError:
                    continue
        
        return existing_ids

    def create_match_event(self, match_data):
        """
        Prepare and insert a Leaguepedia match into Google Calendar.
        """
        m = match_data['title']
        
        # 1. Manage timings (Leaguepedia is in UTC)
        start_str = m['datetime_utc']
        start_dt = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        if m['best_of'] == '1' and m['match_id'].split('/')[0] == 'LEC':
            end_dt = start_dt + timedelta(hours=0.75)  # LEC Bo1 are estimated at 45 minutes
        else:
            end_dt = start_dt + timedelta(hours=1*int(m['best_of'])) # Estimated time based on BestOf length

        # 2. Construction of the Event object
        event_body = {
            'summary': f"[{m['match_id'].split('/')[0]}] {m['team1']} vs {m['team2']}",
            'location': f'{m["stream"]}',
            'description': f"Match ID: {m['match_id']}\nImported via Esports Aggregator.",
            'start': {
                'dateTime': start_dt.replace(microsecond=0).isoformat() + 'Z',
            },
            'end': {
                'dateTime': end_dt.replace(microsecond=0).isoformat() + 'Z',
            },
            'colorId': self._get_color_by_league(m['match_id'].split('/')[0]),
        }

        # 3. Envoi à Google
        return self.service.events().insert(calendarId='primary', body=event_body).execute()

    def _get_color_by_league(self, tournament):
        """Helper interne pour colorer les events selon la ligue."""
        t = tournament.upper()
        if 'LFL' in t: return '1'  # Blue
        if 'LEC' in t: return '6'  # Orange
        if 'LCK' in t: return '9'  # Violet
        if 'LPL' in t: return '11' # Red
        return '5' # Yellow by default