import nest_asyncio
from dataclasses import dataclass
from typing import Union
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from pydantic_ai import Agent, RunContext, ToolDenied
from pydantic_ai.messages import ModelMessage
from dotenv import load_dotenv

# Specific imports for human-in-the-loop
from pydantic_ai import ApprovalRequired, DeferredToolRequests, DeferredToolResults

load_dotenv()

# Apply nest_asyncio for interactive environments
nest_asyncio.apply()

# Initialize rich console for better UI
console = Console()


class BankAccount:
    def __init__(self, balance: float = 1000.0):
        self.balance = balance

    def withdraw(self, amount: float) -> float:
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance


class Contact(BaseModel):
    name: str
    account_number: str


@dataclass
class Deps:
    account: BankAccount
    contacts: dict[str, Contact]


# Define the agent
# We specify output_type to include DeferredToolRequests so type inference works
agent = Agent(
    "openai:gpt-5.1-chat-latest",
    deps_type=Deps,
    output_type=Union[str, DeferredToolRequests],
    instructions=(
        "You are a helpful banking assistant. "
        "You can check balances, list contacts, and transfer money. "
    ),
)


@agent.tool
def check_balance(ctx: RunContext[Deps]) -> str:
    """Check the current account balance."""
    return f"Current balance: ${ctx.deps.account.balance:.2f}"


@agent.tool
def search_contacts(ctx: RunContext[Deps]) -> list[str]:
    """Search for contacts by name."""
    return ctx.deps.contacts


@agent.tool
def transfer_money(ctx: RunContext[Deps], amount: float, contact_name: str) -> str:
    """Transfer money to another account. Use the search_contacts tool to browse the list of contacts."""
    try:
        contact = ctx.deps.contacts[contact_name]
    except KeyError:
        return f"Contact '{contact_name}' not found."

    if amount > 100 and not ctx.tool_call_approved:
        raise ApprovalRequired(
            metadata={
                "amount": amount,
                "to_account": contact.name,
                "account_number": contact.account_number,
                "risk_level": "high" if amount > 1000 else "medium",
            }
        )

    try:
        new_balance = ctx.deps.account.withdraw(amount)
        return f"Successfully transferred ${amount:.2f} to {contact.name} ({contact.account_number}). New balance: ${new_balance:.2f}"
    except ValueError as e:
        return f"Transfer failed: {str(e)}"


def main():
    contacts = {
        "Alice": Contact(name="Alice", account_number="1234567890"),
        "Bob": Contact(name="Bob", account_number="1234567891"),
        "Charlie": Contact(name="Charlie", account_number="1234567892"),
    }

    deps = Deps(
        account=BankAccount(balance=1000.0),
        contacts=contacts,
    )

    console.print(
        Panel.fit(
            "🏦 Banking Assistant",
            style="bold blue",
        )
    )
    console.print("Type 'quit' to exit. Try asking: 'Transfer $500 to Alice'")

    # Keep track of message history to resume conversations
    message_history: list[ModelMessage] = []

    while True:
        try:
            user_input = console.input("\n[bold green]User > [/bold green]")
            if user_input.lower() in ("quit", "exit"):
                break

            # Run the agent
            # Pass existing message history to maintain context
            result = agent.run_sync(
                user_input, deps=deps, message_history=message_history
            )

            # Check if the agent stopped for tool approval
            if isinstance(result.output, DeferredToolRequests):
                requests = result.output

                # Create a results object to hold our approvals/denials
                tool_results = DeferredToolResults()

                # Iterate through all calls requiring approval
                for approval in requests.approvals:
                    tool_name = approval.tool_name
                    tool_args = approval.args
                    tool_id = approval.tool_call_id
                    metadata = requests.metadata.get(tool_id, {})

                    console.print(
                        f"\n[bold yellow]⚠️  Approval Required for tool: {tool_name}[/bold yellow]"
                    )
                    console.print(f"Arguments: {tool_args}")
                    if metadata:
                        to_account = metadata.get("to_account", "Unknown")
                        account_number = metadata.get("account_number", "")
                        console.print(f"Transfer to: {to_account} ({account_number})")
                        console.print(
                            f"Risk Level: {metadata.get('risk_level', 'unknown')}"
                        )

                    # Physically ask the user
                    is_approved = Confirm.ask("Do you approve this transaction?")

                    if is_approved:
                        tool_results.approvals[tool_id] = True
                        console.print("[green]Transaction Approved[/green]")
                    else:
                        # We can provide a reason for the denial
                        tool_results.approvals[tool_id] = ToolDenied(
                            "User denied the high-value transaction."
                        )
                        console.print("[red]Transaction Denied[/red]")

                # Resume the agent with the results and message history
                # We use the messages from the first run (which include the tool call requests)
                resume_result = agent.run_sync(
                    message_history=result.all_messages(),
                    deps=deps,
                    deferred_tool_results=tool_results,
                )

                console.print(
                    f"\n[bold blue]Agent > [/bold blue]{resume_result.output}"
                )
                message_history = resume_result.all_messages()

            else:
                # Normal response
                console.print(f"\n[bold blue]Agent > [/bold blue]{result.output}")
                message_history = result.all_messages()

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    main()
