"""
Streaming the agent's intermediate steps with agent.iter().
This is where 'agentic' becomes visible. Every grep, every read, printed live.

If you've ever watched Claude Code work, this is the same loop.

More info: https://ai.pydantic.dev/agents/#iterating-over-an-agents-graph
"""

import asyncio

import nest_asyncio
from pydantic_ai import Agent
from pydantic_ai.messages import FunctionToolCallEvent, FunctionToolResultEvent

from utils.tools import grep, list_files, read_file
from utils.streaming import format_tool_result

nest_asyncio.apply()

# --------------------------------------------------------------
# Step 1: Same agent as before
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
# Step 2: Iterate over the agent's graph and print each tool call
# --------------------------------------------------------------


async def run_with_visible_steps(question: str, debug: bool = False) -> str:
    print(f"\nQ: {question}\n")
    print("--- agent steps ---")
    tool_names: dict[str, str] = {}

    async with agent.iter(question) as run:
        async for node in run:
            if Agent.is_call_tools_node(node):
                async with node.stream(run.ctx) as tool_stream:
                    async for event in tool_stream:
                        if isinstance(event, FunctionToolCallEvent):
                            tool_names[event.tool_call_id] = event.part.tool_name
                            print(
                                f"-> {event.part.tool_name}({event.part.args_as_json_str()})"
                            )
                        elif debug and isinstance(event, FunctionToolResultEvent):
                            print(format_tool_result(event, tool_names))

    print("--- done ---\n")
    return run.result.output


# --------------------------------------------------------------
# Step 3: Run it
# --------------------------------------------------------------

if __name__ == "__main__":
    answer = asyncio.run(
        run_with_visible_steps(
            "Why does our nightly deploy job run at 03:47 UTC specifically?",
            debug=False,
        )
    )
    print("A:", answer)
