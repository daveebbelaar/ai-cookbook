from pydantic_ai.messages import ModelResponse, ModelRequest


def print_agent_trace(result):
    print("\n" + "=" * 60)
    print("AGENT TRACE")
    print("=" * 60)

    step = 0
    for message in result.all_messages():
        if isinstance(message, ModelResponse):
            for part in message.parts:
                part_type = type(part).__name__
                if part_type == "ToolCallPart":
                    step += 1
                    print(f"\n[Step {step}] Tool call: {part.tool_name}")
                    print(f"         Args: {part.args}")
                elif part_type == "TextPart":
                    step += 1
                    print(f"\n[Step {step}] Final response")
                    print(f"         {part.content[:200]}")
        elif isinstance(message, ModelRequest):
            for part in message.parts:
                part_type = type(part).__name__
                if part_type == "ToolReturnPart":
                    print(f"         ← {part.tool_name} returned: {str(part.content)[:150]}")

    print("\n" + "=" * 60)
