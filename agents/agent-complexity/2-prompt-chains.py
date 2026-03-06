"""
Level 2: Prompt Chains & Routing — Deterministic DAGs
Multiple LLM calls in a fixed sequence. Code controls the flow, not the model.
"""

from enum import Enum

from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv
import nest_asyncio

load_dotenv()

nest_asyncio.apply()


# --- Models ---


class Category(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    GENERAL = "general"


class TicketClassification(BaseModel):
    category: Category
    confidence: float


class Resolution(BaseModel):
    response: str
    escalate: bool


# --- Agents (each is a single focused LLM call) ---


classifier = Agent(
    "anthropic:claude-sonnet-4-6",
    output_type=TicketClassification,
    system_prompt="Classify the customer ticket into a category. Be precise.",
)

billing_handler = Agent(
    "anthropic:claude-sonnet-4-6",
    output_type=Resolution,
    system_prompt=(
        "You handle billing issues. Generate a resolution. "
        "Set escalate=true if a refund over $100 is needed."
    ),
)

technical_handler = Agent(
    "anthropic:claude-sonnet-4-6",
    output_type=Resolution,
    system_prompt=(
        "You handle technical issues. Generate a resolution. "
        "Set escalate=true if the issue requires engineering intervention."
    ),
)

general_handler = Agent(
    "anthropic:claude-sonnet-4-6",
    output_type=Resolution,
    system_prompt="You handle general inquiries. Be helpful and concise.",
)


# --- DAG: classify → route → handle → validate ---


HANDLERS = {
    Category.BILLING: billing_handler,
    Category.TECHNICAL: technical_handler,
    Category.GENERAL: general_handler,
}


def process_ticket(ticket: str) -> Resolution:
    classification = classifier.run_sync(ticket)
    print(
        f"Classified as: {classification.output.category} ({classification.output.confidence:.0%})"
    )

    handler = HANDLERS[classification.output.category]
    result = handler.run_sync(ticket)

    if result.output.escalate:
        print("Escalating to human agent")

    return result.output


if __name__ == "__main__":
    ticket = (
        "I was charged twice for my subscription last month. "
        "Order ID: #12345. The duplicate charge was $49.99."
    )
    resolution = process_ticket(ticket)
    print(f"\nResponse: {resolution.response}")
