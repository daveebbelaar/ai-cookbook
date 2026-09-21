"""A schema-valid team label can still route the ticket to the wrong team.
This customer wants a settings how-to and says the charge is not in dispute.
The model still classifies it as billing.

More info: https://docs.typesafe.ai/model-jaggedness/jev-1.13
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: A ticket that mentions a charge, but is not a billing request
# --------------------------------------------------------------

ticket = (
    "How do I turn off auto-renew? I see a $49 charge from last week "
    "but I am not disputing it. I just need the setting."
)
expected = "other"
question = Choice(
    instructions="Which team should handle this support ticket?",
    criteria={
        "billing": "Payments, charges, or refunds.",
        "technical": "Errors, bugs, or login failures.",
        "other": "Anything else.",
    },
)

# --------------------------------------------------------------
# Step 2: Compare Jev's team with the label the criteria imply
# --------------------------------------------------------------

response = client.system_one(state=ticket, questions={"team": question})
answer = response.choices["team"]

print("Ticket:", ticket)
print("Expected team:", expected)
print("Jev team:", answer.choice)
print("Confidence:", answer.confidence)
print("Probabilities:", answer.probabilities)
print("Match:", answer.choice == expected)
