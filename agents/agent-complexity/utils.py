from pydantic_ai.messages import ModelResponse, ModelRequest


def print_agent_trace(result):
    print("\n" + "=" * 60)
    print("AGENT TRACE")
    print("=" * 60)

    step = 0

    for message in result.all_messages():
        # What the model said
        if isinstance(message, ModelResponse):
            for part in message.parts:
                part_type = type(part).__name__

                if part_type == "ToolCallPart":
                    step += 1
                    print(f"\n[Step {step}] Model requested tool: {part.tool_name}")
                    print(f"         Model-supplied args: {part.args}")

                elif part_type == "TextPart":
                    step += 1
                    print(f"\n[Step {step}] Model text response")
                    print(f"         {part.content[:200]}")

        # What the framework sent back after running tools
        elif isinstance(message, ModelRequest):
            for part in message.parts:
                part_type = type(part).__name__

                if part_type == "ToolReturnPart":
                    print(
                        f"         ← Tool returned from {part.tool_name}: {str(part.content)[:150]}"
                    )

    print("\n" + "=" * 60)
