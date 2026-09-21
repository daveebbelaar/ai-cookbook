"""Choice selects from a set of options you define, such as billing or technical support.
This example routes a support ticket and prints the selected team, option probabilities, and confidence.

More info: https://docs.typesafe.ai/primitives/choice
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: Give Jev the ticket and the possible answers
# --------------------------------------------------------------

ticket = "I was charged twice for order A-104. Please refund the duplicate."
question = Choice(
    instructions="Which team should handle this support ticket?",
    criteria={
        "billing": "Payments, charges, or refunds.",
        "technical": "Errors, bugs, or login failures.",
        "other": "Anything else.",
    },
)

# --------------------------------------------------------------
# Step 2: Make the call and read the typed answer
# --------------------------------------------------------------


response = client.system_one(state=ticket, questions={"team": question})

answer = response.choices["team"]
print("Team:", answer.choice)
print("Probabilities:", answer.probabilities)
print("Confidence:", answer.confidence)
