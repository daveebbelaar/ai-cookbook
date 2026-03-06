"""
Level 1: Augmented LLM — Single API Call
One model call with structured output, system prompt, and context. No loops, no tools.
"""

from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv
import nest_asyncio

load_dotenv()


nest_asyncio.apply()


class TicketClassification(BaseModel):
    category: str
    priority: str
    summary: str
    can_auto_resolve: bool


agent = Agent(
    "anthropic:claude-sonnet-4-6",
    output_type=TicketClassification,
    system_prompt=(
        "You are a customer support classifier. "
        "Classify incoming tickets by category (billing, technical, general), "
        "priority (low, medium, high), and whether they can be auto-resolved."
    ),
)

result = agent.run_sync(
    "I was charged twice for my subscription last month. "
    "Order ID: #12345. Please refund the duplicate charge."
)

print(result.output)
# category='billing' priority='high' summary='Duplicate subscription charge, requesting refund for order #12345' can_auto_resolve=True
