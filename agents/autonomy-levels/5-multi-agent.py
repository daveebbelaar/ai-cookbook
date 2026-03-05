"""
Level 5: Multi-Agent Orchestration — Delegated Autonomy
An orchestrator delegates to specialized subagents defined via the Claude Agent SDK.
Each subagent has its own prompt, tools, and model. The orchestrator coordinates.

NOTE: Run with `python 5-multi-agent.py` (not IPython/Jupyter).

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
from claude_agent_sdk.types import AgentDefinition
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


# --- External API tools (shared across agents via MCP) ---


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


# --- Subagent definitions ---


AGENTS = {
    "researcher": AgentDefinition(
        description="Investigates billing issues by reading customer files and checking the payment gateway.",
        prompt=(
            "You are a billing research specialist. You have access to a knowledge base "
            "with customer profiles, policies, and templates. Investigate the issue thoroughly:\n"
            "1. Read the customer file to understand their history\n"
            "2. Check the payment gateway to verify the transaction\n"
            "3. Read the refund policy to determine eligibility\n"
            "Return a clear, factual summary of your findings."
        ),
        tools=[
            "Read",
            "Glob",
            "Grep",
            "mcp__billing-api__check_payment_gateway",
        ],
        model="haiku",
    ),
    "drafter": AgentDefinition(
        description="Drafts customer-facing responses using templates from the knowledge base.",
        prompt=(
            "You are a customer communications specialist. Draft a professional, empathetic "
            "response based on the research findings you receive. Use the response templates "
            "in the knowledge base as a starting point, then personalize for the customer."
        ),
        tools=["Read", "Glob"],
        model="haiku",
    ),
    "compliance_reviewer": AgentDefinition(
        description="Reviews proposed actions and responses for policy compliance.",
        prompt=(
            "You are a compliance reviewer. Verify that the proposed refund action and "
            "customer response follow company policy. Check the escalation matrix and "
            "refund policy. Flag any issues or approve the action."
        ),
        tools=["Read", "Glob"],
        model="haiku",
    ),
}


# --- Orchestrator ---


class CustomerEmail(BaseModel):
    subject: str
    body: str


class OrchestratorOutput(BaseModel):
    research_summary: str
    duplicate_confirmed: bool
    refund_amount: float
    compliance_approved: bool
    final_action: str
    customer_email: CustomerEmail


async def run_orchestrator(task: str):
    server = create_sdk_mcp_server(
        name="billing-api",
        version="1.0.0",
        tools=[check_payment_gateway, issue_refund],
    )

    options = ClaudeAgentOptions(
        system_prompt=(
            "You are a senior case manager. Resolve customer issues by delegating "
            "to your specialized team using the Task tool:\n\n"
            "1. 'researcher' — investigates billing data and payment gateway\n"
            "2. 'drafter' — writes customer-facing responses from templates\n"
            "3. 'compliance_reviewer' — checks policy compliance before sending\n\n"
            "Coordinate the workflow: research first, then draft, then compliance review. "
            "Pass findings between agents. After all agents report back, synthesize "
            "a final decision and present the approved response.\n\n"
            f"Knowledge base location: {KNOWLEDGE_DIR}"
        ),
        allowed_tools=[
            "Task",
            "Read",
            "Glob",
            "mcp__billing-api__check_payment_gateway",
            "mcp__billing-api__issue_refund",
        ],
        agents=AGENTS,
        mcp_servers={"billing-api": server},
        output_format={
            "type": "json_schema",
            "schema": OrchestratorOutput.model_json_schema(),
        },
        permission_mode="acceptEdits",
        max_turns=20,
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
                    output = OrchestratorOutput.model_validate(raw)
                    print("\nStructured output:")
                    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(
        run_orchestrator(
            "Customer cust_12345 reports a duplicate charge on their February bill. "
            "Delegate to your team: have the researcher investigate, the drafter prepare "
            "a response, and compliance review the final action before we send it."
        )
    )
