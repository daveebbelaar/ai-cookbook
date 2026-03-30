"""
AG2 Human-in-the-Loop Patterns

For production systems, you often need human oversight. AG2 provides
three modes via human_input_mode:

- "NEVER"     → Fully automated, no human input
- "ALWAYS"    → Human reviews every message
- "TERMINATE" → Human reviews only at conversation end

This example shows how to set up human approval for critical actions.
"""

import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, LLMConfig

load_dotenv()


def main():
    llm_config = LLMConfig({
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    })

    assistant = AssistantAgent(
        name="Assistant",
        system_message=(
            "You are a helpful assistant. When you have a complete answer, "
            "end your message with TERMINATE."
        ),
        llm_config=llm_config,
    )

    # TERMINATE mode: runs automatically, but asks for human input at the end
    human_proxy = UserProxyAgent(
        name="Human",
        human_input_mode="TERMINATE",
        max_consecutive_auto_reply=3,
        code_execution_config=False,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    print("Human-in-the-Loop Demo")
    print("The agent will work autonomously, then ask for your feedback.")
    print("Type 'exit' to end, or provide feedback to continue.\n")

    run_response = human_proxy.run(
        assistant,
        message="Draft a brief project proposal for adding AI-powered search to our app.",
    )
    run_response.process()


if __name__ == "__main__":
    main()
