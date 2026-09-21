"""State is the information Jev evaluates when answering your questions.
The examples route a billing ticket as a string, a technical ticket as a JSON object, and an unrelated request as a JSON array.
In Python, pass a string, dictionary, or list directly; an array is one state, not a batch.

More info: https://docs.typesafe.ai/concepts/state
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

question = Choice(
    instructions="Which team should handle this support ticket?",
    criteria={
        "billing": "Payments, charges, or refunds.",
        "technical": "Errors, bugs, or login failures.",
        "other": "Anything else.",
    },
)

# --------------------------------------------------------------
# Step 1: String state, billing ticket
# --------------------------------------------------------------

string_state = "I was charged twice for order A-104. Please refund the duplicate."

string_response = client.system_one(
    state=string_state,
    questions={"team": question},
)
print("Team:", string_response.choices["team"].choice)
print("Confidence:", string_response.choices["team"].confidence)

# --------------------------------------------------------------
# Step 2: JSON object state, technical ticket
# --------------------------------------------------------------

object_state = {
    "page": "Dashboard",
    "error_code": "500",
    "message": "The dashboard crashes every time I log in. Can you fix this bug?",
}

object_response = client.system_one(
    state=object_state,
    questions={"team": question},
)
print("Team:", object_response.choices["team"].choice)
print("Confidence:", object_response.choices["team"].confidence)

# --------------------------------------------------------------
# Step 3: JSON array state, other request
# --------------------------------------------------------------

array_state = [
    "I organize a local developer meetup.",
    "We would love someone from your team to give a guest talk.",
    "Who should I contact about speaking at our event?",
]

array_response = client.system_one(
    state=array_state,
    questions={"team": question},
)
print("Team:", array_response.choices["team"].choice)
print("Confidence:", array_response.choices["team"].confidence)
