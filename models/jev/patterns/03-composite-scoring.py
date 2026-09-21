"""Composite scoring combines several independent model ratings into one application-defined score.
This example rates ticket impact, urgency, and frustration, then normalizes and weights those values in Python to rank tickets.

More info: https://docs.typesafe.ai/patterns/composite-scoring
"""

from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: Define three independent dimensions, each with three levels
# --------------------------------------------------------------

questions = {
    "impact": Score(
        instructions="How much does the reported problem disrupt the customer's work?",
        criteria=["No disruption.", "Some work disrupted.", "Essential work is blocked."],
    ),
    "urgency": Score(
        instructions="How soon does the customer say they need a resolution?",
        criteria=["No deadline stated.", "Within a week.", "Today or immediately."],
    ),
    "frustration": Score(
        instructions="How frustrated is the customer?",
        criteria=["Calm.", "Frustrated but civil.", "Very angry or abusive."],
    ),
}
weights = {"impact": 0.5, "urgency": 0.3, "frustration": 0.2}


# --------------------------------------------------------------
# Step 2: Normalize the scores, then apply visible business weights
# --------------------------------------------------------------


tickets = [
    "Checkout is down for our whole store. We need it fixed immediately! This is unacceptable!",
    "One chart label is clipped. I can still read it by hovering. No rush.",
]
ranked = []
for ticket in tickets:
    print("\nTicket:", ticket)
    response = client.system_one(state=ticket, questions=questions)
    normalized = {}
    for name, answer in response.scores.items():
        # Three rubric levels are numbered 0, 1, 2; divide by 2.
        normalized[name] = answer.score / (len(questions[name].criteria) - 1)
        print(name, "score:", answer.score, "confidence:", answer.confidence)
    priority = sum(normalized[name] * weight for name, weight in weights.items())
    review = any(answer.confidence < 0.6 for answer in response.scores.values())
    ranked.append((priority, ticket, review))

print("\nSuggested priority order (0 to 1):")
for priority, ticket, review in sorted(ranked, key=lambda row: row[0], reverse=True):
    print(f"{priority:.2f} | review={review} | {ticket}")
# This is a weighted business score, not a probability. Tune weights and gates.
