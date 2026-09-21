"""Speculative fan-out asks several potentially useful questions before knowing which answers will be needed.
This example evaluates billing and bug-related questions together, then uses only the answers relevant to the selected route.

More info: https://docs.typesafe.ai/patterns/fan-out
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: Include questions for several possible branches
# --------------------------------------------------------------

questions = {
    "category": Choice(
        instructions="What is the main topic of this support ticket?",
        criteria={
            "bug": "Broken software or unexpected errors.",
            "billing": "Payments, charges, or refunds.",
            "other": "Any other request.",
        },
    ),
    "severity": Score(
        instructions="How much does the reported software bug block work?",
        criteria=["No blocking bug described.", "Workaround exists.", "Work cannot continue."],
    ),
    "reproducible": Noul(
        instructions="Does the ticket give concrete steps that reproduce a software bug?",
    ),
    "refund": Noul(instructions="Does the customer explicitly request money back?"),
}

# --------------------------------------------------------------
# Step 2: Make one call per ticket, not one call per question
# --------------------------------------------------------------



tickets = [
    "Open Reports, click Export, then get error 500 every time. No workaround; work is blocked.",
    "I was charged twice for order A-104. Please refund the duplicate.",
]
for ticket in tickets:
    print("\nTicket:", ticket)
    response = client.system_one(state=ticket, questions=questions)
    category = response.choices["category"]
    print("Category:", category.choice, "Confidence:", category.confidence)
    # Teaching thresholds, validate on your own tickets.
    if category.confidence < 0.8:
        print("Route: human review")
    elif category.choice == "bug":
        # Refund was evaluated too, but it is irrelevant to this branch.
        severity = response.scores["severity"]
        repro = response.nouls["reproducible"].noul
        print("Severity:", severity.score, "Reproducible:", repro)
        print("Route:", "engineering priority" if severity.score > 1.5 and repro > 0.8
              else "bug review")
    elif category.choice == "billing":
        # Ignore severity and reproducibility for billing tickets.
        refund = response.nouls["refund"].noul
        print("Route: billing; refund flag:", refund >= 0.9)
    else:
        print("Route: general support")
