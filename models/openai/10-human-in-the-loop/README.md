# Human-in-the-Loop Patterns

When building AI agents that perform real-world actions, you need human oversight for high-risk operations. This tutorial shows how to pause execution and require approval before proceeding.

## The Banking Example

Both examples implement the same banking workflow with three operations:

```mermaid
flowchart LR
    subgraph Input
        A[User Request]
    end

    subgraph LLM["LLM Processing"]
        B{Intent<br/>Classification}
    end

    subgraph Actions
        C[Check Balance]
        D[Deposit]
        E[Transfer]
    end

    subgraph Approval
        F{Amount > $100?}
        G[Human Approval]
    end

    subgraph Execution
        H[Execute]
    end

    A --> B
    B --> C --> H
    B --> D --> H
    B --> E --> F
    F -->|No| H
    F -->|Yes| G --> H
```

The key insight: **transfers over $100 require human approval before execution**.

## Two Approaches

### Approach 1: LLM as Router (Structured Output)

The LLM outputs a structured action plan with multiple actions. Your code loops through and executes each one.

```mermaid
flowchart LR
    A[Request] --> B[LLM]
    B --> C[ActionPlan]
    C --> D{Router}
    D --> E[check_balance]
    D --> F[deposit]
    D --> G[transfer]
    G --> H{Approval?}
    H -->|Required| I[Wait for Human]
    I --> J[Execute]
    H -->|Not Required| J
```

**File:** `1-structured-output.py`

- LLM returns `ActionPlan` with list of typed actions
- Loop through each action and route to function
- Pydantic validator enforces approval rule
- Your code executes each action

### Approach 2: LLM with Tool Calls

The LLM decides which tools to call. You intercept, execute, and return results in a loop.

```mermaid
flowchart LR
    A[Request] --> B[LLM]
    B --> C[Tool Calls]
    C --> D{Intercept}
    D --> E[get_balance]
    D --> F[deposit_money]
    D --> G[transfer_money]
    G --> H{Approval?}
    H -->|Required| I[Wait for Human]
    I --> J[Execute]
    H -->|Not Required| J
    J --> K[Return Result to LLM]
    K --> B
```

**File:** `2-tool-call-approval.py`

- LLM returns tool calls with arguments
- Loop through each call, check approval, execute
- Return all results to LLM for next iteration

### When to Use Each

| Approach | Recommendation |
|----------|----------------|
| Structured Output | **Recommended for most use cases.** Gives you full control over execution. Ideal for DAGs, graph-based orchestration, and smaller workflows. More reliable and predictable in production. |
| Tool Calls | **Recommended for interactive chat applications.** Better for multi-step agents, larger agentic loops, and scenarios where the LLM needs to adapt based on previous results. |

---

## Production Patterns

The examples above use `input()` to block for approval. In production, you need to **persist state** and **resume later**. Two patterns:

### Pattern 1: SSE Streaming (Real-time Chat)

For interactive chat applications where a user is actively engaged.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Agent
    participant StateStore

    User->>Frontend: "Transfer $150 to Alice"
    Frontend->>API: POST /chat (SSE stream)
    API->>Agent: Process request
    Agent->>Agent: Determine action:<br/>transfer(amount=150)
    Agent->>Agent: Approval required
    Agent->>StateStore: Save agent state +<br/>pending tool call
    Agent-->>API: Stream: tool_call_pending
    API-->>Frontend: SSE: approval_required
    Note over Frontend,API: Connection closes
    Frontend-->>User: Show approval UI
    User->>Frontend: Click "Approve"
    Frontend->>API: POST /execute {approved: true}
    API->>StateStore: Load saved state
    StateStore-->>API: Agent state + pending call
    API->>Agent: Resume with approval
    Agent->>Agent: Execute action
    Agent-->>API: Stream response
    API-->>Frontend: SSE: "Transfer complete"
    Frontend-->>User: Show result
```

### Pattern 2: Async with State Persistence

For backend workflows where no user is actively waiting. Works the same whether triggered by API, webhook, or queue.

```mermaid
sequenceDiagram
    participant API
    participant Worker
    participant Agent
    participant StateStore
    participant Notification
    participant User

    API->>Worker: Start workflow
    Worker->>Agent: Process request
    Agent->>Agent: Approval required
    Agent->>Notification: Send approval request
    Notification-->>User: Email/Slack notification
    Agent->>StateStore: Save state + pending action
    StateStore-->>Agent: Saved
    Note over Worker: Worker released
    
    User->>API: Approve via link/button
    API->>Worker: Resume workflow
    Worker->>StateStore: Load state
    StateStore-->>Worker: Agent state + pending action
    Worker->>Agent: Resume with approval
    Agent->>Agent: Execute action
    Agent->>Notification: Send completion notice
    Notification-->>User: "Transfer complete"
```

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Deferred Execution** | When approval is needed, save state instead of executing |
| **State Serialization** | Persist agent context, message history, and pending actions |
| **Stateless Resume** | Load state from storage, don't hold in memory |