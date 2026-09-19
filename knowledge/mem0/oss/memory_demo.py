from openai import OpenAI
from mem0 import Memory
from dotenv import load_dotenv

load_dotenv("../.env")

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333},
    },
}

openai_client = OpenAI()
memory = Memory.from_config(config)


def chat_with_memories(message: str, user_id: str = "default_user") -> str:
    # Retrieve relevant memories
    relevant_memories = memory.search(query=message, filters={"user_id": user_id}, top_k=3)
    memories_str = "\n".join(
        f"- {entry['memory']}" for entry in relevant_memories["results"]
    )
    print(memories_str)

    # Generate Assistant response
    system_prompt = f"You are a helpful AI. Answer the question based on query and memories.\nUser Memories:\n{memories_str}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=messages
    )
    assistant_response = response.choices[0].message.content

    # Create new memories from the conversation
    messages.append({"role": "assistant", "content": assistant_response})
    # This is where the magic happens
    memory.add(messages, user_id=user_id, metadata={"source": "demo"})

    return assistant_response


def main():
    print("Chat with AI (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        print(f"AI: {chat_with_memories(user_input)}")


if __name__ == "__main__":
    main()
