"""Independent questions can share one state and run together in a single Jev request.
This example combines Choice, Score, and Noul to triage a support ticket.
Each question sees the ticket, but cannot use the answers to the other questions.

More info: https://docs.typesafe.ai/primitives
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: Define the state and three different kinds of question
# --------------------------------------------------------------

ticket = "I was charged twice for order A-104. This is frustrating. Please refund me."
questions = {
    "team": Choice(
        instructions="Which team should handle this support ticket?",
        criteria={
            "billing": "Payments, charges, or refunds.",
            "technical": "Errors, bugs, or login failures.",
            "other": "Anything else.",
        },
    ),
    "frustration": Score(
        instructions="How frustrated is the customer in this ticket?",
        criteria=[
            "Calm or neutral.",
            "Frustrated but civil.",
            "Very angry or abusive.",
        ],
    ),
    "refund_requested": Noul(
        instructions="Does the customer explicitly ask for money to be returned?",
    ),
}

# --------------------------------------------------------------
# Step 2: Read the results and branch in ordinary Python
# --------------------------------------------------------------

response = client.system_one(state=ticket, questions=questions)

team = response.choices["team"]
frustration = response.scores["frustration"]
refund = response.nouls["refund_requested"].noul
print("Team:", team.choice, "Confidence:", team.confidence)
print("Frustration:", frustration.score, "Legend:", frustration.legend)
print("Probability of a refund request:", refund)
# Teaching thresholds, tune against labeled tickets before real use.
print("Queue:", team.choice if team.confidence >= 0.8 else "human_review")
print("Check refund policy:", refund >= 0.9)
