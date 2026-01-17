"""
Human-in-the-Loop: Structured Output with Router

This pattern uses Pydantic models and a router to:
1. Analyze the user request and create action plan(s)
2. Pause for approval on sensitive actions
3. Execute each action

No tool calls - only chained LLM calls with structured output.

Run: python 1-structured-output.py
"""

from typing import Literal, Self
from openai import OpenAI
from pydantic import BaseModel, model_validator
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# --------------------------------------------------------------
# Account State
# --------------------------------------------------------------

BALANCE = 1000.0


# --------------------------------------------------------------
# Action Functions
# --------------------------------------------------------------


def get_balance() -> str:
    return f"Current balance: ${BALANCE:.2f}"


def transfer_money(to_account: str, amount: float) -> str:
    global BALANCE
    if amount > BALANCE:
        return f"Error: Insufficient funds. Current balance: ${BALANCE:.2f}"
    BALANCE -= amount
    return f"Transferred ${amount:.2f} to {to_account}. New balance: ${BALANCE:.2f}"


def deposit_money(amount: float) -> str:
    global BALANCE
    BALANCE += amount
    return f"Deposited ${amount:.2f}. New balance: ${BALANCE:.2f}"


# --------------------------------------------------------------
# Structured Output Models
# --------------------------------------------------------------


class Action(BaseModel):
    action_type: Literal["check_balance", "transfer", "deposit"]
    to_account: str | None = None
    amount: float | None = None
    requires_confirmation: bool = False

    @model_validator(mode="after")
    def enforce_confirmation_rule(self) -> Self:
        if self.action_type == "transfer" and self.amount and self.amount > 100:
            self.requires_confirmation = True
        return self


class ActionPlan(BaseModel):
    actions: list[Action]


# --------------------------------------------------------------
# Example confirmation enforcement
# --------------------------------------------------------------

confirmation_example = Action(
    action_type="transfer",
    to_account="Alice",
    amount=500,  # over $100
    requires_confirmation=False,  # but we set to False
)

print(confirmation_example.model_dump_json(indent=2))


# --------------------------------------------------------------
# Human-in-the-Loop with Prompt Chaining
# --------------------------------------------------------------


def run_with_confirmation(prompt: str) -> str:
    # Step 1: Analyze request and create action plan
    response = client.responses.parse(
        model="gpt-4o",
        instructions=(
            "You are a banking assistant. Analyze the user request and create a list of actions. "
            "Use 'check_balance' for balance inquiries, 'transfer' for money transfers, "
            "'deposit' for adding money to the account. "
            "Set requires_confirmation=True for transfers over $100. "
            "Extract to_account and amount for transfers, amount for deposits."
        ),
        temperature=0,
        input=prompt,
        text_format=ActionPlan,
    )

    plan = response.output_parsed
    print(plan.model_dump_json(indent=2))
    results = []

    # Step 2: Execute each action (router)
    for action in plan.actions:
        if action.action_type == "check_balance":
            results.append(get_balance())

        elif action.action_type == "transfer":
            # Human-in-the-loop: Check if confirmation is needed
            if action.requires_confirmation:
                print("\n⚠️  Approval Required")
                print(f"Transfer ${action.amount:.2f} to {action.to_account}")

                if input("\nApprove? (y/n): ").strip().lower() != "y":
                    results.append(
                        f"Transfer of ${action.amount:.2f} to {action.to_account} cancelled by user."
                    )
                    continue

            result = transfer_money(action.to_account, action.amount)
            results.append(result)

        elif action.action_type == "deposit":
            result = deposit_money(action.amount)
            results.append(result)

    return "\n".join(results)


# --------------------------------------------------------------
# Demo
# --------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Human-in-the-Loop: Structured Output with Prompt Chaining")
    print("=" * 60)

    # Multiple actions - check balance and small transfer
    print("\n--- Check Balance + Small Transfer ($50) ---")
    result = run_with_confirmation("Check my balance and transfer $50 to Alice")
    print(f"\nResult:\n{result}")

    # Deposit money
    print("\n--- Deposit ---")
    result = run_with_confirmation("Deposit $200 into my account")
    print(f"\nResult:\n{result}")

    # Large transfer - requires approval
    print("\n--- Large Transfer ($500) ---")
    result = run_with_confirmation("Transfer $500 to Bob for rent")
    print(f"\nResult:\n{result}")
