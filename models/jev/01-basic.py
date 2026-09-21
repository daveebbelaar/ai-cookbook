"""Make your first Jev request by sending a support ticket and a Choice question.
The model selects the team that should handle the ticket from the options you provide.

- State: The content or context you want the model to evaluate.
- Question: A named judgment defined using a primitive such as Choice, Score, or Noul.
- Instructions: The task you want the model to perform for that question.
- Criteria: The options or rubric that define how the question should be answered.

Choice and Score require criteria; Noul can use instructions alone.
"""

from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Send a ticket and choose the team that should handle it
# --------------------------------------------------------------

response = client.system_one(
    state="I was charged twice. Please refund the duplicate.",
    questions={
        "team": Choice(
            instructions="Which team should handle this support ticket?",
            criteria={
                "billing": "Payments, charges, or refunds.",
                "technical": "Errors, bugs, or login failures.",
                "other": "Anything else.",
            },
        ),
    },
)

print("Team:", response.choices["team"].choice)
