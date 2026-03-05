"""
Level 4: Agent Harness — Full Runtime Access
Give the agent a full runtime via the Claude Agent SDK.
It can search files, read docs, and reason through problems autonomously.

NOTE: Run with `python 4-agent-harness.py` (not IPython/Jupyter).
The Claude Agent SDK uses anyio TaskGroups incompatible with nest_asyncio.

https://platform.claude.com/docs/en/agent-sdk/python
"""

import asyncio
import json
from pathlib import Path

from pydantic import BaseModel
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    tool,
    create_sdk_mcp_server,
)
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


@tool(
    "check_payment_gateway",
    "Check payment processor for transaction status and refund eligibility",
    {"transaction_date": str, "amount": str},
)
async def check_payment_gateway(args):
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"Payment Gateway Response for {args['transaction_date']} — ${args['amount']}:\n"
                    "- Transaction ID: txn_8f3k2j1\n"
                    "- Status: SETTLED\n"
                    "- Refund eligible: YES\n"
                    "- Original payment method: Visa ending in 4242\n"
                    "- Settlement date: 2025-02-02"
                ),
            }
        ]
    }


@tool(
    "issue_refund",
    "Process a refund through the payment gateway",
    {"amount": str, "reason": str, "customer_id": str},
)
async def issue_refund(args):
    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"Refund processed successfully:\n"
                    f"- Customer: {args['customer_id']}\n"
                    f"- Amount: ${args['amount']}\n"
                    f"- Reason: {args['reason']}\n"
                    "- Refund ID: ref_9x2m4p7\n"
                    "- ETA: 3-5 business days"
                ),
            }
        ]
    }


class CustomerEmail(BaseModel):
    subject: str
    body: str


class HarnessOutput(BaseModel):
    action_taken: str
    refund_amount: float
    refund_id: str
    policy_compliant: bool
    customer_email: CustomerEmail


async def run_harness(task: str):
    server = create_sdk_mcp_server(
        name="billing-api",
        version="1.0.0",
        tools=[check_payment_gateway, issue_refund],
    )

    options = ClaudeAgentOptions(
        system_prompt=(
            "You are a senior support analyst with access to:\n\n"
            f"1. A knowledge base at: {KNOWLEDGE_DIR}\n"
            "   - policies/ — refund policy, escalation matrix, subscription management\n"
            "   - customers/ — customer profiles with transaction history\n"
            "   - templates/ — response templates\n\n"
            "2. External billing API tools:\n"
            "   - check_payment_gateway — verify transaction status\n"
            "   - issue_refund — process refunds\n\n"
            "Investigate issues by reading the relevant files AND calling the billing API. "
            "Always verify the transaction with the payment gateway before issuing a refund.\n"
            "Think step by step about what information you need before acting."
        ),
        allowed_tools=[
            "Read",
            "Glob",
            "Grep",
            "mcp__billing-api__check_payment_gateway",
            "mcp__billing-api__issue_refund",
        ],
        mcp_servers={"billing-api": server},
        output_format={
            "type": "json_schema",
            "schema": HarnessOutput.model_json_schema(),
        },
        permission_mode="acceptEdits",
        max_turns=15,
        max_budget_usd=1.00,
        model="sonnet",
        cwd=str(KNOWLEDGE_DIR),
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(task)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
                    elif isinstance(block, ToolUseBlock):
                        print(f"\n  [Tool] {block.name}({block.input})")
            elif isinstance(message, ResultMessage):
                cost = (
                    f"${message.total_cost_usd:.4f}"
                    if message.total_cost_usd
                    else "n/a"
                )
                print(f"\n--- Done in {message.num_turns} turns | cost: {cost} ---")
                if message.structured_output:
                    raw = (
                        json.loads(message.structured_output)
                        if isinstance(message.structured_output, str)
                        else message.structured_output
                    )
                    output = HarnessOutput.model_validate(raw)
                    print("\nStructured output:")
                    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(
        run_harness(
            "Customer cust_12345 reports a duplicate charge on their February bill. "
            "Investigate using the knowledge base, determine the right action per policy, "
            "and draft a personalized response using the appropriate template."
        )
    )
