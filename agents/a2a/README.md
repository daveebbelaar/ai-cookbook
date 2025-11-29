# A2A Protocol: Agent-to-Agent Communication

A minimal implementation of Google's [Agent-to-Agent (A2A) Protocol](https://a2a-protocol.org/latest/).

## What is A2A?

**A2A is for agents talking to agents. MCP is for agents talking to tools.**

| Protocol | Purpose | Analogy |
|----------|---------|---------|
| **MCP** | Agent ↔ Tools | A developer using APIs |
| **A2A** | Agent ↔ Agent | Two colleagues collaborating |

### The Key Insight

With MCP, your agent calls a tool and gets a predictable response. With A2A, your agent delegates a task to another agent—which might think, ask clarifying questions, take time, or even fail gracefully. It's **opaque collaboration** between autonomous systems.

## Why A2A Matters

1. **Interoperability**: Agents built with different frameworks (LangGraph, CrewAI, custom) can communicate
2. **Delegation**: One agent can hand off complex sub-tasks to specialized agents
3. **Security**: Agents don't share internal state, memory, or proprietary logic
4. **Enterprise-ready**: Built on HTTP/JSON-RPC, works with existing infrastructure

## Core Concepts

### Agent Card
Every A2A agent publishes a "business card" at `/.well-known/agent-card.json`:
- Name, description, version
- Skills it can perform
- Input/output formats it accepts
- Whether it supports streaming

### Task
When you send a message to an agent, it creates a **Task**. Tasks have states:
- `submitted` → `working` → `completed`
- Can also be `input_required`, `failed`, or `canceled`

### Message
Communication happens through messages with **Parts** (text, data, files).

## Quick Start

```bash
# Create virtual environment and install dependencies
uv venv && uv pip install -r requirements.txt

# Terminal 1: Start the agent server
uv run python server.py

# Terminal 2: Run the client
uv run python client.py
```

**Expected output:**
```
✅ Connected to: Echo Agent
📝 Description: A minimal A2A agent that echoes your messages
🎯 Skills: ['Echo']

📤 Sending: Hello from Python!
📥 Task ID: 98b619af-f41a-4571-b6e0-8df0463f1a08
📊 Status: TaskState.completed
💬 Response: Echo: Hello from Python!
```

## Files

| File | Description |
|------|-------------|
| `server.py` | Minimal A2A agent that echoes messages |
| `client.py` | Client that connects and sends a message |

## How It Works

```
┌─────────────┐     HTTP/JSON-RPC      ┌─────────────┐
│   Client    │ ───────────────────▶   │   Server    │
│  (client.py)│      "Hello!"          │ (server.py) │
│             │ ◀───────────────────   │             │
│             │   Task + Response      │  EchoAgent  │
└─────────────┘                        └─────────────┘
```

1. **Client** discovers the agent via its Agent Card at `/.well-known/agent-card.json`
2. **Client** sends a message to the agent
3. **Server** creates a Task, processes it, returns a response
4. **Client** receives the completed task with the agent's response

## A2A vs MCP: A Practical Example

**MCP (Tool Calling):**
```python
# You call a tool, get a direct result
weather = await mcp_client.call_tool("get_weather", {"city": "Paris"})
# Returns: {"temp": 22, "conditions": "sunny"}
```

**A2A (Agent Delegation):**
```python
# You ask another agent, it may think, clarify, or take time
async for event in client.send_message(create_text_message_object(content="Plan a weekend trip to Paris")):
    task, update = event
    print(f"Status: {task.status.state}")  # submitted → working → completed
# Returns: Task with status updates, possibly follow-up questions, eventually a detailed plan
```

## Resources

- [A2A Protocol Documentation](https://a2a-protocol.org/latest/)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [A2A Samples Repository](https://github.com/a2aproject/a2a-samples)
