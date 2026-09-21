import json
from pathlib import Path

import openai
from dotenv import load_dotenv
from tools import add

# Interactive cells have no __file__; open them from this lesson folder.
SCRIPT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

load_dotenv(SCRIPT_DIR.parent / ".env")

"""
This is a simple example to demonstrate that MCP simply enables a new way to call functions.
"""

# Define tools for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer", "description": "First number"},
                    "b": {"type": "integer", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        },
    }
]


# Call LLM
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Calculate 25 + 17"}],
    tools=tools,
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)

    # Execute directly
    result = add(**tool_args)

    # Send result back to model
    final_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "Calculate 25 + 17"},
            response.choices[0].message,
            {"role": "tool", "tool_call_id": tool_call.id, "content": str(result)},
        ],
    )
    print(final_response.choices[0].message.content)
