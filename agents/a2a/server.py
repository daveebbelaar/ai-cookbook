"""
Minimal A2A Server: An agent that echoes messages back.
Run: python server.py
Test: curl http://localhost:9000/.well-known/agent.json
"""

import uvicorn
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.utils import new_task, new_agent_text_message


AGENT_URL = "http://localhost:9000"


def create_agent_card() -> AgentCard:
    return AgentCard(
        name="Echo Agent",
        description="A minimal A2A agent that echoes your messages",
        url=AGENT_URL,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=False, push_notifications=False),
        skills=[
            AgentSkill(
                id="echo",
                name="Echo",
                description="Echoes back whatever you send",
                tags=["echo", "test"],
                examples=["Hello!", "How are you?"],
            )
        ],
    )


class EchoAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        user_input = context.get_user_input() or "No message provided"
        response = new_agent_text_message(
            f"Echo: {user_input}", task.context_id, task.id
        )
        await updater.complete(response)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.current_task:
            updater = TaskUpdater(
                event_queue, context.current_task.id, context.current_task.context_id
            )
            await updater.cancel()


if __name__ == "__main__":
    agent_card = create_agent_card()
    executor = EchoAgentExecutor()
    handler = DefaultRequestHandler(
        agent_executor=executor, task_store=InMemoryTaskStore()
    )
    app = A2AFastAPIApplication(agent_card=agent_card, http_handler=handler).build()

    print(f"🚀 A2A Echo Agent running at {AGENT_URL}")
    print(f"📋 Agent Card: {AGENT_URL}/.well-known/agent.json")
    uvicorn.run(app, host="0.0.0.0", port=9000)
