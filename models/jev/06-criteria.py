"""Criteria define the available options or the rubric for a question.
Choice uses a dictionary, Score uses an ordered list, and Noul accepts optional true/false criteria.
A description inside criteria can be a string or structured content; the whole criteria field is not a plain string.

More info: https://docs.typesafe.ai/primitives
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, NoulCriteria, Score, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)
ticket = "I was charged twice. This is frustrating. Please refund the duplicate."

# --------------------------------------------------------------
# Choice: a dictionary of option names and string descriptions
# --------------------------------------------------------------

response = client.system_one(
    state=ticket,
    questions={
        "team": Choice(
            instructions="Which team should handle this ticket?",
            criteria={
                "billing": "Payments, charges, or refunds.",
                "technical": "Errors, bugs, or login failures.",
                "other": "Anything else.",
            },
        )
    },
)
print("Team:", response.choices["team"].choice)

# --------------------------------------------------------------
# Choice: structured descriptions inside the same dictionary
# --------------------------------------------------------------

response = client.system_one(
    state=ticket,
    questions={
        "team": Choice(
            instructions="Which team should handle this ticket?",
            criteria={
                "billing": {
                    "covers": "Payments, charges, and refunds.",
                    "examples": ["Charged twice", "Missing refund"],
                    "excludes": "Login failures.",
                },
                "technical": ["Application errors", "Bugs", "Login failures"],
                "other": "Anything else.",
            },
        )
    },
)
print("Team:", response.choices["team"].choice)

# --------------------------------------------------------------
# Score: an ordered list of level descriptions
# --------------------------------------------------------------

response = client.system_one(
    state=ticket,
    questions={
        "frustration": Score(
            instructions="How frustrated is the customer?",
            criteria=[
                "Calm or neutral.",
                "Frustrated but civil.",
                "Very angry or abusive.",
            ],
        )
    },
)
print("Frustration:", response.scores["frustration"].score)

# --------------------------------------------------------------
# Noul: optional descriptions of what true and false mean
# --------------------------------------------------------------

# Omit criteria when the instructions alone make the boundary clear.
response = client.system_one(
    state=ticket,
    questions={
        "refund": Noul(
            instructions="Does the customer explicitly request a refund?",
            criteria=NoulCriteria(
                true="Explicitly asks for money to be returned.",
                false="Reports a problem without asking for money back.",
            ),
        )
    },
)
print("Refund probability:", response.nouls["refund"].noul)
