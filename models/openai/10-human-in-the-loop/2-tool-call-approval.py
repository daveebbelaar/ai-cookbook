"""
Human-in-the-Loop: Tool Call Approval

This pattern intercepts tool calls before execution and asks
for user approval on sensitive actions.

Run: python 2-tool-call-approval.py
"""

import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# --------------------------------------------------------------
# Define Tools
# --------------------------------------------------------------

tools = [
    {
        "type": "function",
        "name": "get_balance",
        "description": "Get the current account balance",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "type": "function",
        "name": "transfer_money",
        "description": "Transfer money to another account",
        "parameters": {
            "type": "object",
            "properties": {
                "to_account": {
                    "type": "string",
                    "description": "Recipient account name",
                },
                "amount": {"type": "number", "description": "Amount to transfer"},
            },
            "required": ["to_account", "amount"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "deposit_money",
        "description": "Deposit money into the account",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount to deposit"},
            },
            "required": ["amount"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


# --------------------------------------------------------------
# Tool Implementations
# --------------------------------------------------------------

BALANCE = 1000.0


def get_balance() -> str:
    return f"Current balance: ${BALANCE:.2f}"


def transfer_money(to_account: str, amount: float) -> str:
    global BALANCE
    if amount > BALANCE:
        return "Error: Insufficient funds"
    BALANCE -= amount
    return f"Transferred ${amount:.2f} to {to_account}. New balance: ${BALANCE:.2f}"


def deposit_money(amount: float) -> str:
    global BALANCE
    BALANCE += amount
    return f"Deposited ${amount:.2f}. New balance: ${BALANCE:.2f}"


def execute_tool(name: str, args: dict) -> str:
    if name == "get_balance":
        return get_balance()
    elif name == "transfer_money":
        return transfer_money(**args)
    elif name == "deposit_money":
        return deposit_money(**args)
    return f"Unknown tool: {name}"


# --------------------------------------------------------------
# Human-in-the-Loop Functions
# --------------------------------------------------------------


def requires_approval(tool_name: str, args: dict) -> bool:
    if tool_name == "transfer_money":
        return args.get("amount", 0) > 100
    return False


def get_user_approval(tool_name: str, args: dict) -> bool:
    print("\n⚠️  Approval Required")
    print(f"Tool: {tool_name}")
    print(f"Arguments: {json.dumps(args, indent=2)}")
    response = input("\nApprove? (y/n): ").strip().lower()
    return response == "y"


# --------------------------------------------------------------
# Agent Loop with Tool Approval
# --------------------------------------------------------------


def run_with_approval(prompt: str) -> str:
    messages = [
        {"role": "user", "content": prompt},
    ]

    while True:
        response = client.responses.create(
            instructions=(
                "You are a helpful banking assistant. "
                "You can check balances, list contacts, and transfer money."
            ),
            model="gpt-4o",
            temperature=0,
            input=messages,
            tools=tools,
        )

        # Check if model wants to call tools
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            return response.output_text

        # Process each tool call
        for tool_call in tool_calls:
            args = json.loads(tool_call.arguments)

            # Human-in-the-loop: Check if approval is needed
            if requires_approval(tool_call.name, args):
                if not get_user_approval(tool_call.name, args):
                    messages.append(tool_call)
                    messages.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": "DENIED: User rejected this action",
                        }
                    )
                    continue

            # Execute approved tool
            result = execute_tool(tool_call.name, args)
            messages.append(tool_call)
            messages.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result,
                }
            )


# --------------------------------------------------------------
# Demo
# --------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Human-in-the-Loop: Tool Call Approval")
    print("=" * 60)

    # Multiple actions - check balance and small transfer
    print("\n--- Check Balance + Small Transfer ($50) ---")
    result = run_with_approval("Check my balance and transfer $50 to Alice")
    print(f"\nResult: {result}")

    # Deposit money
    print("\n--- Deposit ---")
    result = run_with_approval("Deposit $200 into my account")
    print(f"\nResult: {result}")

    # Large transfer - requires approval
    print("\n--- Large Transfer ($500) ---")
    result = run_with_approval("Transfer $500 to Bob for rent")
    print(f"\nResult: {result}")
