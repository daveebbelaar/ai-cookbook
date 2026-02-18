'''
Krzysztof Kućmierz, krzysztof.kucmierz@artificiuminformatica.pl
'LICENSE' file in the ai-cookbook project contains license details.

IMPORTANT! Before authenticating to Google Calendar you need to enable Calendar API and create OAuth credentials in Google Cloud.
Follow detailed steps -> https://developers.google.com/calendar/api/quickstart/python

This file contains helper methods to access Google Calendar using Google Calendar API:
- authentication
- create a meeting
- list upcoming meetings
- show details of a meeting
'''

import os
import sys
from datetime import datetime, timezone, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scopes required
SCOPES = ['https://www.googleapis.com/auth/calendar']


'''
Connect to user's calendar using open authentication (OAuth)
Returns: service object or None in case of HttpError
'''
def authenticate_and_connect_to_GoogleCalendarAPI():
    creds = None

    # Load credentials if previously saved
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If credentials are not available or invalid, request login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Connect to Google Calendar API
        service = build('calendar', 'v3', credentials=creds)
        
    except HttpError as error:
        print(f"An error occurred: {error}.")
        service = None
    
    return service

'''
Shows event details on console output
Input parameters:
event       calndar event object
Returns:    None
'''
def show_event_details(event):
    # Extract event URI
    event_uri = event['htmlLink']
    # Extract Google Meet link (if added)        
    meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', 'No Meet link')
    print(f"✅ Event Created Successfully: {event['summary']}")
    print(f"🔗 Event URI: {event_uri}")
    print(f"📍 Location: {event.get('location', 'Not provided')}")
    print(f"🕒 Start: {event['start']['dateTime']}")
    print(f"🕒 End: {event['end']['dateTime']}")
    print(f"📧 Attendees: {[attendee['email'] for attendee in event.get('attendees', [])]}")
    print(f"🎨 Color ID: {event.get('colorId', 'Default')}")
    default_reminders = event.get('reminders', {}).get('useDefault', True)
    print(f"🔔 Reminders: {'Default' if default_reminders else 'Non default or disabled'}")        
    print(f"📹 Google Meet Link: {meet_link}")


'''
Creates a calendar event (meeting)
Input parameters:
service             resource object (client allowing to call Google Calendar API methods)
title               meeting title
start_datetime      day and time of the meeting
duration_minutes    meeting duration
attendees_emails    list of e-mails
description         (optional) short description of the meeting
location            (optional) meeting location
reminders           (optional) if True meeting reminders will be sent
visibility          (optional) visibility of the meeting. Options are: 'default', 'public', or 'private'
color_id            (optional) color assigned to the meeting
add_meet_link       (optional) if True add Google Meet link to a meeting

Returns:    True if event created, False if not created
'''
def create_event(service, 
                 title: str, 
                 start_datetime: str, 
                 duration_minutes: int,
                 attendees_emails: list[str], 
                 description: str = None, 
                 location: str = None, 
                 reminders: bool = True, 
                 visibility: str = 'default', 
                 color_id: str = '1', 
                 add_meet_link: bool = False):

    # Convert start time to ISO 8601 format (RFC3339)
    start_time = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    end_time = start_time + timedelta(minutes=duration_minutes)

    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',  # Adjust to your timezone if needed
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
        'location': location if location else "",  # Optional location
        'attendees': [{'email': email} for email in attendees_emails],
        'visibility': visibility,  
        'colorId': color_id,  # Color-coded event (1-11)
        'reminders': {
            'useDefault': False if reminders else True,
            'overrides': [
                {'method': 'email', 'minutes': 30},  # Email reminder 30 mins before
                {'method': 'popup', 'minutes': 10}   # Pop-up reminder 10 mins before
            ] if reminders else [],
        },
        
        # Add Google Meet link if requested
        'conferenceData': {
            'createRequest': {
                'requestId': f"meet-{start_time.timestamp()}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        } if add_meet_link else None
    }

    # Insert event with conference data enabled
    try:
        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1  # Required for Google Meet links
        ).execute()
        
    except HttpError as error:
        print(f"An error occurred: {error}.")

    # Verify event creation
    if 'id' in event and 'htmlLink' in event:
        print(f"✅ Event Created Successfully.")
        show_event_details(event)
        return True
    else:
        print("❌ Event creation failed: No valid response received.")
        return False


'''
Shows up to 10 future events in the calendar
Input parameters:
service     resource object (client allowing to call Google Calendar API methods)
Returns:    None
'''
# 
def show_upcoming_events(service):
    # Fetch upcoming events
    print('\nFetching upcoming events...')
    now = datetime.now(timezone.utc).isoformat()

    try:
        events_result = service.events().list(calendarId='primary', maxResults=10, singleEvents=True,
                                            orderBy='startTime', timeMin=now).execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
        else:
            print("\n📅 Upcoming Events:\n" + "="*30)
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))  # Handles all-day events
                start_dt = datetime.fromisoformat(start) if 'T' in start else datetime.strptime(start, "%Y-%m-%d")
                formatted_start = start_dt.strftime("%A, %d %B %Y %I:%M %p") if 'T' in start else start_dt.strftime("%A, %d %B %Y")

                print(f"🕒 {formatted_start} - {event.get('summary', 'No Title')}")
            print("="*30)
            
    except HttpError as error:
        print(f"An error occurred: {error}.")


'''
A flow to test above methods
'''
def test_calendar_tools():

    service = authenticate_and_connect_to_GoogleCalendarAPI()
    
    if service is None:
        print("Couldn't connect to Calendar API. Exiting!")        
        sys.exit(1)

    # if connected to service, add a meeting
    create_event(
        service=service,  
        title="Let's talk about AI agents and workflows.",
        description="Meeting generated using Calendar API.",
        start_datetime="2025-03-28 11:00",  # Format: YYYY-MM-DD HH:MM (24-hour)
        duration_minutes=45,
        attendees_emails=["architect@xyz.ai", "program_manager@xyz.ai"],
        location="Google Meet",
        reminders=True,
        visibility="public",  # Can be 'default', 'public', or 'private'
        color_id="4",  # Google Calendar color ID (1-11)
        add_meet_link=True
    )

    show_upcoming_events(service)


if __name__ == '__main__':
    test_calendar_tools()