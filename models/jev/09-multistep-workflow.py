"""Some decisions need evidence that is only available after an earlier step completes.
This example selects a tool, fetches support data, and sends that evidence to Jev for a follow-up decision.
Python applies the business rules and prepares the final response.

More info: https://docs.typesafe.ai/patterns
"""

import logging

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)
logging.basicConfig(level=logging.INFO, format="%(message)s")

# --------------------------------------------------------------
# Step 1: Define the tools and fixed reply templates
# --------------------------------------------------------------


def get_order(order_id: str) -> dict:
    return {"A-104": {
        "captured_charges": [49, 49], "expected_total": 49,
        "support_note": "A checkout retry caused an extra payment to settle.",
    }}[order_id]


def get_service_status(order_id: str) -> dict:
    return {"login": "operational", "checkout": "operational"}


tools = {"get_order": get_order, "get_service_status": get_service_status}
replies = {
    "refund_review": "Your order has an extra charge. Our billing team will review it.",
    "human_review": "Our support team will review your request.",
}

# --------------------------------------------------------------
# Step 2: Select a lookup from the customer's message
# --------------------------------------------------------------


def handle_ticket(client: TypeSafeClient, ticket: dict) -> str:
    triage = client.system_one(
        state=ticket,
        questions={"tool": Choice(
            instructions="Which lookup would help answer `message`?",
            criteria={
                "get_order": "Look up charges or shipping for an order.",
                "get_service_status": "Check if login or checkout is down.",
                "none": "Neither lookup is relevant.",
            },
        ), "refund_requested": Noul(
            instructions="Does `message` explicitly request money back?",
        )},
    )
    route = triage.choices["tool"]
    logging.info("Selected %s (confidence %.2f)", route.choice, route.confidence)
    if route.confidence < 0.8 or route.choice == "none":
        return replies["human_review"]

    # The order ID comes from the application's ticket record, not generated text.
    evidence = tools[route.choice](ticket["order_id"])
    logging.info("Tool result: %s", evidence)

    # --------------------------------------------------------------
    # Step 3: Enrich the state and ask the dependent question
    # --------------------------------------------------------------

    follow_up = client.system_one(
        state={"ticket": ticket, "lookup": route.choice, "evidence": evidence},
        questions={"complaint_supported": Noul(
            instructions=(
                "Does `evidence.support_note` describe the same problem reported "
                "in `ticket.message`? Answer no if there is no support note."
            ),
        )},
    )
    refund_probability = triage.nouls["refund_requested"].noul
    supported = follow_up.nouls["complaint_supported"].noul
    logging.info("Refund request probability: %.2f", refund_probability)

    # --------------------------------------------------------------
    # Step 4: Keep arithmetic and business rules in Python
    # --------------------------------------------------------------

    if route.choice == "get_order":
        overcharge = sum(evidence["captured_charges"]) > evidence["expected_total"]
        if overcharge and refund_probability >= 0.9 and supported >= 0.9:
            return replies["refund_review"]
    return replies["human_review"]


ticket = {
    "order_id": "A-104",
    "message": "I was charged twice for order A-104. Please refund the duplicate.",
}
print(handle_ticket(client, ticket))
