"""Confidence-gated routing uses confidence thresholds to decide whether to act or request review.
This example applies different thresholds to an order lookup and a cancellation request.
The thresholds are teaching examples that need validation on representative tickets before real use.

More info: https://docs.typesafe.ai/patterns/confidence-routing
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: Classify the requested action
# --------------------------------------------------------------

question = Choice(
    instructions="What action is the customer explicitly requesting?",
    criteria={
        "order_status": "Check where an order is or when it will arrive.",
        "cancel_order": "Cancel an existing order.",
        "other": "Another request, or the desired action is unclear.",
    },
)


# --------------------------------------------------------------
# Step 2: Let both the action and confidence determine the route
# --------------------------------------------------------------


def choose_route(action):
    # Teaching thresholds: confidence is not a guarantee or authorization.
    if action.confidence < 0.6 or action.choice == "other":
        return "Human review: clarify what the customer wants."
    if action.choice == "order_status":
        return "Read-only order lookup."
    if action.confidence < 0.9:
        return "Ask the customer to clarify whether they want cancellation."
    return "Cancellation review: verify identity, policy, and confirmation."


tickets = [
    "Where is order A-104?",
    "Please cancel order A-104. I no longer need it.",
    "Something about my order isn't right. Can you help?",
]
for ticket in tickets:
    print("\nTicket:", ticket)
    action = client.system_one(state=ticket, questions={"action": question}).choices["action"]
    print("Action:", action.choice, "Confidence:", action.confidence)
    print(choose_route(action))
# These routes are printed locally; no orders are changed.
