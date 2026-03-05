"""
Level 3: Tool-Calling Agent — Scoped Autonomy
The agent decides which tools to call and in what order,
but only within a fixed set of well-defined capabilities.
"""

from dataclasses import dataclass

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
from utils import print_agent_trace
import nest_asyncio

load_dotenv()

nest_asyncio.apply()


# --- Dependencies ---


@dataclass
class CustomerDeps:
    customer_id: str
    db: dict  # simplified — in production this would be a real DB client


# --- Output ---


class BillingResolution(BaseModel):
    action_taken: str
    refund_amount: float | None
    follow_up_needed: bool


# --- Agent ---


billing_agent = Agent(
    "anthropic:claude-sonnet-4-6",
    deps_type=CustomerDeps,
    output_type=BillingResolution,
    system_prompt=(
        "You are a billing support agent. Use the available tools to look up "
        "customer data, check policies, and resolve billing issues. "
        "Always verify the charge before issuing a refund."
    ),
)


# --- Tools (the agent decides when and how to use these) ---


@billing_agent.tool
async def get_customer_balance(ctx: RunContext[CustomerDeps]) -> str:
    balance = ctx.deps.db.get("balance", 0)
    return f"Current balance: ${balance:.2f}"


@billing_agent.tool
async def get_recent_charges(ctx: RunContext[CustomerDeps]) -> str:
    charges = ctx.deps.db.get("charges", [])
    return "\n".join(
        f"- ${c['amount']:.2f} on {c['date']}: {c['description']}" for c in charges
    )


@billing_agent.tool
async def check_refund_policy(
    ctx: RunContext[CustomerDeps], charge_description: str
) -> str:
    return (
        f"Policy for '{charge_description}': "
        "Duplicate charges are eligible for automatic refund within 30 days. "
        "Refunds over $100 require manager approval."
    )


@billing_agent.tool
async def issue_refund(
    ctx: RunContext[CustomerDeps], amount: float, reason: str
) -> str:
    return f"Refund of ${amount:.2f} issued successfully. Reason: {reason}"


# --- Run ---


if __name__ == "__main__":
    import asyncio

    deps = CustomerDeps(
        customer_id="cust_12345",
        db={
            "balance": 149.97,
            "charges": [
                {
                    "amount": 49.99,
                    "date": "2025-02-01",
                    "description": "Monthly subscription",
                },
                {
                    "amount": 49.99,
                    "date": "2025-02-01",
                    "description": "Monthly subscription",
                },
                {
                    "amount": 49.99,
                    "date": "2025-01-01",
                    "description": "Monthly subscription",
                },
            ],
        },
    )

    result = asyncio.run(
        billing_agent.run(
            "I was charged twice on Feb 1st for my subscription. Please fix this.",
            deps=deps,
        )
    )

    print_agent_trace(result)

    print(f"\nAction: {result.output.action_taken}")
    print(f"Refund: ${result.output.refund_amount}")
    print(f"Follow-up needed: {result.output.follow_up_needed}")
