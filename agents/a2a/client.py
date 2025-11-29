"""
Minimal A2A Client: Connects to an A2A agent and sends a message.
Run: python client.py (after starting server.py)
"""

import asyncio
from a2a.client import ClientFactory, create_text_message_object


AGENT_URL = "http://localhost:9000"


async def main():
    client = await ClientFactory.connect(AGENT_URL)
    agent_card = await client.get_card()

    print(f"Connected to: {agent_card.name}")
    print(f"Description: {agent_card.description}")
    print(f"Skills: {[s.name for s in agent_card.skills]}\n")

    message = create_text_message_object(content="Hello from Python!")
    print(f"Sending: {message.parts[0].root.text}")

    async for event in client.send_message(message):
        if isinstance(event, tuple):
            task, update = event
            print(f"Task ID: {task.id}")
            print(f"Status: {task.status.state}")
            if task.status.message and task.status.message.parts:
                reply = task.status.message.parts[0].root.text
                print(f"Response: {reply}")


if __name__ == "__main__":
    asyncio.run(main())
