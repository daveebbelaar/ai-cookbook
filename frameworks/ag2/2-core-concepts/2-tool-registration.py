"""
AG2 Tool Registration Pattern

AG2 uses a dual registration pattern for tools:
1. register_for_llm() — Tells the LLM what tools exist (generates JSON schema)
2. register_for_execution() — Tells the UserProxy how to execute them

This separation enables:
- The LLM decides WHEN to call a tool
- The UserProxy controls HOW it's executed (sandboxing, logging, approval)

Tools use Python type hints and Annotated for parameter descriptions.
"""

import os
from typing import Annotated
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, LLMConfig

load_dotenv()


# --- Tools ---

def search_docs(
    query: Annotated[str, "Search query for the documentation"],
    max_results: Annotated[int, "Maximum number of results"] = 3,
) -> str:
    """Search the product documentation for relevant information."""
    # Simulated search for demo purposes
    docs = {
        "pricing": "Plans start at $10/month. Enterprise pricing available on request.",
        "api": "REST API available at api.example.com. Rate limit: 100 req/min.",
        "setup": "Install via pip install example-sdk. Requires Python 3.10+.",
        "auth": "Use API keys for authentication. OAuth2 supported for enterprise.",
        "billing": "Invoices sent monthly. Payment via credit card or wire transfer.",
    }
    results = []
    for topic, info in docs.items():
        if any(word in topic for word in query.lower().split()):
            results.append(f"[{topic}]: {info}")
    return "\n".join(results[:max_results]) if results else "No results found."


def create_ticket(
    title: Annotated[str, "Ticket title"],
    priority: Annotated[str, "Priority level: low, medium, or high"],
    description: Annotated[str, "Detailed ticket description"],
) -> str:
    """Create a support ticket in the ticketing system."""
    ticket_id = f"TICK-{hash(title) % 10000:04d}"
    return f"Created ticket {ticket_id}: '{title}' (Priority: {priority})"


def main():
    llm_config = LLMConfig({
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    })

    support_agent = AssistantAgent(
        name="SupportAgent",
        system_message=(
            "You are a customer support agent. Use tools to search documentation "
            "and create tickets when needed. Always search docs before answering."
        ),
        llm_config=llm_config,
    )

    executor = UserProxyAgent(
        name="Customer",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config=False,
    )

    # Dual registration — decorator pattern (preferred in AG2 notebooks)
    @executor.register_for_execution()
    @support_agent.register_for_llm(description="Search product docs")
    def search_docs_tool(
        query: Annotated[str, "Search query"],
        max_results: Annotated[int, "Max results"] = 3,
    ) -> str:
        return search_docs(query, max_results)

    @executor.register_for_execution()
    @support_agent.register_for_llm(description="Create support ticket")
    def create_ticket_tool(
        title: Annotated[str, "Title"],
        priority: Annotated[str, "Priority"],
        description: Annotated[str, "Description"],
    ) -> str:
        return create_ticket(title, priority, description)

    run_response = executor.run(
        support_agent,
        message="I need help setting up the API. Also, I'm getting rate limited — "
                "can you create a ticket to increase my limit?",
    )
    run_response.process()


if __name__ == "__main__":
    main()
