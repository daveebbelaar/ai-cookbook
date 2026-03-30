"""
AG2 Hello World: Your First Multi-Agent Conversation

AG2 (formerly AutoGen) uses a conversation-centric design where
an AssistantAgent (LLM-powered) and a UserProxyAgent (human/executor)
collaborate through natural dialogue.

More info: https://docs.ag2.ai/
"""

import os
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, LLMConfig

load_dotenv()


def main():
    # Configure LLM — AG2 supports OpenAI, Azure, Bedrock, Ollama, Mistral, and more
    llm_config = LLMConfig({
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    })

    # Create agents
    assistant = AssistantAgent(
        name="Assistant",
        system_message="You are a helpful AI assistant. Provide clear, concise answers.",
        llm_config=llm_config,
    )

    user_proxy = UserProxyAgent(
        name="User",
        human_input_mode="NEVER",  # Fully automated (no manual input)
        max_consecutive_auto_reply=1,  # One exchange only
        code_execution_config=False,  # No code execution for safety
    )

    # Start the conversation
    run_response = user_proxy.run(
        assistant,
        message="What are the 3 most important things to know about building AI agents?",
    )
    run_response.process()

    # Print the result
    print("\n" + "=" * 50)
    print("Assistant's response:")
    print("=" * 50)
    print(run_response.summary)


if __name__ == "__main__":
    main()
