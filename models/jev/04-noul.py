"""Noul returns a probability from 0 to 1 for a yes-or-no question.
This example checks whether a customer requests a refund and uses thresholds to choose a next step.
A value near 0.5 indicates uncertainty, not a medium level of severity.

More info: https://docs.typesafe.ai/primitives/noul
"""

from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: Ask one yes-or-no question about a ticket
# --------------------------------------------------------------

ticket = "I was charged twice for order A-104. Please refund the duplicate."
question = Noul(
    instructions="Does the customer explicitly ask for money to be returned?",
)

# --------------------------------------------------------------
# Step 2: Use the probability to choose the next step
# --------------------------------------------------------------


response = client.system_one(state=ticket, questions={"refund_requested": question})

probability = response.nouls["refund_requested"].noul
# Noul has no separate confidence: 0.5 means uncertainty, not medium severity.
print("Probability of a refund request:", probability)
# Teaching thresholds, tune against labeled tickets before real use.
if probability >= 0.9:
    print("Next step: check the refund policy.")
elif probability <= 0.1:
    print("Next step: continue normal ticket triage.")
else:
    print("Next step: ask a human to review the request.")
