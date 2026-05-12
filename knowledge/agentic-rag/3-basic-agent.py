"""
Basic Agentic RAG: a Pydantic AI agent with three tools (list_files, grep, read_file).
The agent picks tools to call iteratively until it has enough context to answer.
No vector database, no embeddings, no chunking. Just an LLM that knows how to grep.

More info: https://ai.pydantic.dev/agents/
"""

from pydantic_ai import Agent
import nest_asyncio

from utils.tools import grep, list_files, read_file

nest_asyncio.apply()

# --------------------------------------------------------------
# Step 1: Define the agent
# --------------------------------------------------------------

agent = Agent(
    "openai:gpt-5.5",
    tools=[list_files, grep, read_file],
    instructions=(
        "Search notes with list_files, grep, read_file. Cite files. "
        "If evidence is missing, say so."
    ),
)


# --------------------------------------------------------------
# Step 2: Ask a needle-in-haystack question
# --------------------------------------------------------------

if __name__ == "__main__":
    question = "Why does our nightly deploy job run at 03:47 UTC specifically?"

    result = agent.run_sync(question)

    print(f"\nQ: {question}\n")
    print("A:", result.output)
    print(f"\nUsage: {result.usage()}")
