"""
Google Calendar MCP Integration
Provides calendar access through Model Context Protocol
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarMCP:
    """Google Calendar integration using MCP pattern"""
    
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.path.join(
            os.path.dirname(__file__), '..', 'credentials.json'
        )
        self.token_path = os.path.join(
            os.path.dirname(__file__), '..', 'token.pickle'
        )
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load token if exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google Calendar credentials not found at {self.credentials_path}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        """Get upcoming calendar events"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def create_event(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: str = "",
        location: str = ""
    ) -> Optional[Dict]:
        """Create a new calendar event"""
        try:
            event = {
                'summary': summary,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Toronto',  # Adjust to user's timezone
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Toronto',
                },
            }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return {
                'id': created_event['id'],
                'summary': created_event.get('summary'),
                'start': created_event['start'].get('dateTime'),
                'link': created_event.get('htmlLink')
            }
            
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> Optional[Dict]:
        """Update an existing calendar event"""
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            if summary:
                event['summary'] = summary
            if description is not None:
                event['description'] = description
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Toronto',
                }
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Toronto',
                }
            
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                'id': updated_event['id'],
                'summary': updated_event.get('summary'),
                'start': updated_event['start'].get('dateTime')
            }
            
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for events by keyword"""
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                formatted_events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'description': event.get('description', '')
                })
            
            return formatted_events
            
        except Exception as e:
            print(f"Error searching events: {e}")
            return []


# Global calendar instance
_calendar_mcp = None

def get_calendar_mcp() -> GoogleCalendarMCP:
    """Get or create calendar MCP instance"""
    global _calendar_mcp
    if _calendar_mcp is None:
        _calendar_mcp = GoogleCalendarMCP()
    return _calendar_mcp
