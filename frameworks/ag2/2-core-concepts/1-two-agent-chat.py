"""
AG2 Two-Agent Conversation Pattern

The fundamental building block: an AssistantAgent (LLM) talks to a
UserProxyAgent (human/executor). The UserProxy controls the conversation
flow — when to stop, whether to ask for human input, and how to execute tools.

Key parameters:
- human_input_mode: "NEVER" (automated), "ALWAYS" (manual), "TERMINATE" (hybrid)
- max_consecutive_auto_reply: Safety limit on conversation length
- is_termination_msg: Custom function to detect when to stop
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

    # Assistant with a specific role
    assistant = AssistantAgent(
        name="TechAdvisor",
        system_message=(
            "You are a senior tech advisor. Provide practical, actionable advice "
            "on software architecture and AI systems. Be concise but thorough."
        ),
        llm_config=llm_config,
    )

    # UserProxy with termination detection
    user_proxy = UserProxyAgent(
        name="Developer",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=3,  # Allow up to 3 exchanges
        code_execution_config=False,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    # Multi-turn conversation
    run_response = user_proxy.run(
        assistant,
        message=(
            "I'm building a customer support chatbot. What architecture would you "
            "recommend? Consider scalability, cost, and user experience."
        ),
    )
    run_response.process()

    print(f"\nConversation had {len(run_response.messages)} messages")


if __name__ == "__main__":
    main()
