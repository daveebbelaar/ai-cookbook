"""
AG2 GroupChat: Automatic Multi-Agent Orchestration

GroupChat is AG2's flagship feature. Instead of building routing graphs
or writing transfer functions, you define agents and let the
GroupChatManager automatically select the next speaker.

How it works:
1. User sends a message to the GroupChatManager
2. GroupChatManager uses the LLM to pick the best next speaker
3. Selected agent responds
4. Cycle repeats until max_round or TERMINATE

Speaker selection methods:
- "auto"        → LLM decides (best for complex workflows)
- "round_robin" → Agents take turns (predictable pipelines)
- "random"      → Random selection (testing)
"""

import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, LLMConfig

load_dotenv()


def main():
    llm_config = LLMConfig({
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    })

    researcher = AssistantAgent(
        name="Researcher",
        system_message=(
            "You are a research analyst. Gather facts, analyze data, "
            "and provide well-sourced findings."
        ),
        llm_config=llm_config,
    )
    writer = AssistantAgent(
        name="Writer",
        system_message=(
            "You are a technical writer. Create clear, well-structured "
            "content from research findings."
        ),
        llm_config=llm_config,
    )
    critic = AssistantAgent(
        name="Critic",
        system_message=(
            "You review content for accuracy and clarity. "
            "Provide constructive feedback. Say TERMINATE when satisfied."
        ),
        llm_config=llm_config,
    )
    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        code_execution_config=False,
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
    )

    # GroupChat — automatic speaker selection
    groupchat = GroupChat(
        agents=[user_proxy, researcher, writer, critic],
        messages=[],
        max_round=10,
        speaker_selection_method="auto",
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    # Kick off the collaboration
    run_response = user_proxy.run(
        manager,
        message=(
            "Write a brief overview of how AI agents are being used in "
            "customer support. Cover current trends and best practices."
        ),
    )
    run_response.process()

    print(f"\nGroupChat completed in {len(run_response.messages)} messages")


if __name__ == "__main__":
    main()
