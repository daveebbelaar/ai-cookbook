"""Intent routing selects a handler based on what the customer needs and how complex the request is.
This example routes tickets to a local order lookup, a Claude Haiku draft, or a human-review record.
The generated reply is a draft and is not sent to a customer.

More info: https://docs.typesafe.ai/patterns/intent-routing
"""

from anthropic import Anthropic
from dotenv import load_dotenv
from typesafe_sdk import Choice, Score, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)
haiku = Anthropic()

# --------------------------------------------------------------
# Step 1: Define the intent and complexity questions
# --------------------------------------------------------------

questions = {
    "intent": Choice(
        instructions="What is the main request in `message`?",
        criteria={
            "order_status": "Find an order's shipping or delivery status.",
            "product_question": "Ask about product features or use.",
            "complaint": "Resolve dissatisfaction with a service experience.",
            "other": "None of these, or unclear.",
        },
    ),
    "complexity": Score(
        instructions="How complex is resolving the complaint in `message`?",
        criteria=["Simple issue or no complaint.", "Needs investigation.", "Serious dispute needing escalation."],
    ),
}


# --------------------------------------------------------------
# Step 2: Define actual handlers using fictional support data
# --------------------------------------------------------------


def get_order_status(order_id):
    return {"A-104": "Order A-104 is shipped; expected delivery is tomorrow."}[order_id]


def draft_reply(ticket, specialist):
    # The shared client drafts without sending.
    response = haiku.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=180,
        system=(f"You are a {specialist} support specialist. Draft a reply in two sentences. "
                "Use only these facts: CSV export is on the Pro plan under Reports > Export. "
                "Support can investigate issues but no compensation is promised. "
                "If facts are missing, ask a clarifying question."),
        messages=[{"role": "user", "content": ticket["message"]}],
    )
    return " ".join(block.text for block in response.content if block.type == "text")


def human_review(ticket):
    return {"queue": "human_review", "ticket_id": ticket["id"]}

# --------------------------------------------------------------
# Step 3: Dispatch to the appropriate handler
# --------------------------------------------------------------


def route_ticket(client, ticket):
    response = client.system_one(state=ticket, questions=questions)
    intent = response.choices["intent"]
    complexity = response.scores["complexity"]
    print("Intent:", intent.choice, "Confidence:", intent.confidence)
    if intent.confidence < 0.8 or intent.choice == "other":
        return human_review(ticket)
    if intent.choice == "order_status":
        return get_order_status(ticket["order_id"])
    if intent.choice == "product_question":
        return draft_reply(ticket, "product")
    if complexity.confidence < 0.6 or complexity.score > 1:
        return human_review(ticket)
    return draft_reply(ticket, "complaint resolution")


tickets = [
    {"id": "T-1", "order_id": "A-104", "message": "Where is my order?"},
    {"id": "T-2", "message": "Does the Pro plan let me export reports as CSV?"},
    {"id": "T-3", "message": "You keep charging me after cancellation. This is my fifth complaint. I demand a manager and am taking legal action."},
]
for ticket in tickets:
    print("\nTicket:", ticket["message"])
    print(route_ticket(client, ticket))
