'''
This is an enhanced version of example 1-prompt-chaining.py

It demonstrates end-to-end agentic worflow - setting up meeting in Google Calendar based on user's voice command.

Detailed flow:
- get voice command from user and transcribe it to text (using OpenAI whisper)
- analyze the text whether it contains request to create a meeting (using OpenAI gpt-4o-mini)
- based on the text details, set up a new meeting in the Google Calendar (using Google Calendar API)
- generate confirmation message about the new meeting (using OpenAI gpt-4o-mini)

 IMPORTANT! Before running this example:
 1. Install required libraries: pip install -r rquirements_for_1a.txt
 2. Add .env file with your OpenAI API key
 3. Complete authenticatication setup in Google Cloud. See calendar_tools.py file for details.

'''


import calendar_tools

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import logging
import speech_recognition as sr
from dotenv import load_dotenv

# --------------------------------------------------------------
# Step 0: Setup and helper functions
# --------------------------------------------------------------

# method for audio recording and transcription
# returns full text transcription
def live_transcription() -> str:
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Listening... (Press Ctrl+C to stop)")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        
        while True:
            try:
                print("\nListening...")
                audio = recognizer.listen(source, timeout=15, phrase_time_limit=30) 

                # Save audio as a temporary file
                with open("temp_audio.wav", "wb") as f:
                    f.write(audio.get_wav_data())

                # Transcribe audio using OpenAI Whisper API
                with open("temp_audio.wav", "rb") as audio_file:
                    transcript = audio_client.audio.transcriptions.create(
                        model=audio_model,
                        file=audio_file
                    )
                print(f"Transcript object: {transcript}")
                return transcript.text               


            except sr.WaitTimeoutError:
                print("⏳ No speech detected, waiting...")
            except Exception as e:
                print("⚠️ Error:", e)
                break
    return None

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# setting up OpenAI clients
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o-mini"

audio_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
audio_model = "whisper-1"


# --------------------------------------------------------------
# Step 1: Define the data models for each stage
# --------------------------------------------------------------

class EventExtraction(BaseModel):
    """First LLM call: Extract basic event information"""

    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(
        description="Whether this text describes a calendar event"
    )
    confidence_score: float = Field(description="Confidence score between 0 and 1")


class EventDetails(BaseModel):
    """Second LLM call: Parse specific event details"""

    name: str = Field(description="Name of the event")
    date: str = Field(
        description="Date and time of the event. Use '%Y-%m-%d %H:%M' syntax to format this value."
    )
    duration_minutes: int = Field(description="Expected duration in minutes")
    participants: list[str] = Field(description="List of participants e-mails")


class EventConfirmation(BaseModel):
    """Third LLM call: Generate confirmation message"""

    confirmation_message: str = Field(
        description="Natural language confirmation message"
    )
    calendar_link: Optional[str] = Field(
        description="Generated calendar link if applicable"
    )


# --------------------------------------------------------------
# Step 2: Define the functions
# --------------------------------------------------------------


def extract_event_info(user_input: str) -> EventExtraction:
    """First LLM call to determine if input is a calendar event"""
    logger.info("Starting event extraction analysis")
    logger.debug(f"Input text: {user_input}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Analyze if the text describes a calendar event.",
            },
            {"role": "user", "content": user_input},
        ],
        response_format=EventExtraction,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Extraction complete - Is calendar event: {result.is_calendar_event}, Confidence: {result.confidence_score:.2f}"
    )
    return result


def parse_event_details(description: str) -> EventDetails:
    """Second LLM call to extract specific event details"""
    logger.info("Starting event details parsing")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed event information. When dates reference 'next Tuesday' or similar relative dates, use this current date as reference. Assume Europe West timezone. If extracted participand e-mail info doesn't contain @ sign, then add @ sign to create valid e-mail address. ",
            },
            {"role": "user", "content": description},
        ],
        response_format=EventDetails,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Parsed event details - Name: {result.name}, Date: {result.date}, Duration: {result.duration_minutes}min"
    )
    logger.debug(f"Participants: {', '.join(result.participants)}")
    return result


def generate_confirmation(event_details: EventDetails) -> EventConfirmation:
    """Third LLM call to generate a confirmation message"""
    logger.info("Generating confirmation message")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Generate a natural confirmation message for the event. Sign off with your name; Susie",
            },
            {"role": "user", "content": str(event_details.model_dump())},
        ],
        response_format=EventConfirmation,
    )
    result = completion.choices[0].message.parsed
    logger.info("Confirmation message generated successfully")
    return result


# --------------------------------------------------------------
# Step 3: Chain the functions together
# --------------------------------------------------------------


def process_calendar_request(user_input: str) -> Optional[EventConfirmation]:
    """Main function implementing the prompt chain with gate check"""
    logger.info("Processing calendar request")
    logger.debug(f"Raw input: {user_input}")

    # First LLM call: Extract basic info
    initial_extraction = extract_event_info(user_input)

    # Gate check: Verify if it's a calendar event with sufficient confidence
    if (
        not initial_extraction.is_calendar_event
        or initial_extraction.confidence_score < 0.7
    ):
        logger.warning(
            f"Gate check failed - is_calendar_event: {initial_extraction.is_calendar_event}, confidence: {initial_extraction.confidence_score:.2f}"
        )
        return None

    logger.info("Gate check passed, proceeding with event processing")

    # Second LLM call: Get detailed event information
    event_details = parse_event_details(initial_extraction.description)

    # The following lines create new meeting in user's Google Calendar.
    # We utilize Google Calendar API (see detailed explanation and source code in calendar_tools.py)
    service = calendar_tools.authenticate_and_connect_to_GoogleCalendarAPI()

    patricipants_emails: list[str] = []
    for participant_email in event_details.participants:
        patricipants_emails.append(participant_email)
    
    if service:
        meeting_created = calendar_tools.create_event(service,
                                                      title=event_details.name,
                                                      start_datetime=event_details.date,
                                                      duration_minutes=event_details.duration_minutes,
                                                      attendees_emails=patricipants_emails,
                                                      description=None,
                                                      location=None,
                                                      reminders=True,
                                                      visibility='default',
                                                      color_id='1',
                                                      add_meet_link=True)
    else:
        logger.warning("Could not connect to the calendar using Calendar API!")
        return "The meeting has not been created - there were technical problems."

    if meeting_created:
        # Third LLM call: Generate confirmation
        confirmation = generate_confirmation(event_details)
        logger.info("Calendar request processing completed successfully")
    else:
        logger.warning("Could not create a meeting in the calendar!")
        return "The meeting has not been created - there were technical problems."

    return confirmation


# --------------------------------------------------------------
# Step 4: Test the chain with a valid input
# --------------------------------------------------------------

if __name__ == "__main__":

    user_input = live_transcription()

    # You can say one of these example voice inputs or say uncomment one of these lines just to run the workflow for plain text 
    # user_input = "Schedule 1h team meeting next Tuesday at 1pm with Alice@xyz.ai and Bob@xyz.ai to discuss the project roadmap."
    # user_input = "Ustaw 30 minutowe spotkanie w przyszły czwartek o 14tej z Jacek@ai.pl oraz Agatka@ai.pl żeby zademostrować możliwości agentów sztucznej inteligencji."
    # user_input = "And I think to myself what a wonderful world!" # this is not going to create a calendar event
    result = process_calendar_request(user_input)
    if result:
        print(f"Confirmation: {result.confirmation_message}")
        if result.calendar_link:
            print(f"Calendar Link: {result.calendar_link}")
    else:
        print("This doesn't appear to be a calendar event request.")

