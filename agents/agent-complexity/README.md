# 5 Levels of AI Agents Complexity

| Level | Pattern | Code |
|---|---|---|
| 1 | Augmented LLM | [`1-augmented-llm.py`](1-augmented-llm.py)|
| 2 | Prompt Chains & Routing | [`2-prompt-chains.py`](2-prompt-chains.py)|
| 3 | Tool-Calling Agent | [`3-tool-calling-agent.py`](3-tool-calling-agent.py)|
| 4 | Agent Harness | [`4-agent-harness.py`](4-agent-harness.py) |
| 5 | Multi-Agent Orchestration | [`5-multi-agent.py`](5-multi-agent.py) |

---

## Level 1: Augmented LLM - Single API Call

One model call with the right context: system prompt, few-shot examples, structured output, retrieval. No loops, no tools, no autonomy. This handles more than most people think.

```mermaid
%%{init: {'theme': 'default'}}%%
flowchart LR
    IN(["Input"]) --> LLM["LLM"]

    RAG["Retrieved<br>Context"] -.-> LLM
    FEW["Few-Shot<br>Examples"] -.-> LLM
    SYS["System<br>Prompt"] -.-> LLM

    LLM --> OUT(["Structured<br>Output"])
```

---

## Level 2: Prompt Chains & Routing - Deterministic DAGs

Multiple LLM calls orchestrated through fixed paths. Each step validates its output before passing to the next. No model makes decisions about control flow - the code does.

```mermaid
%%{init: {'theme': 'default'}}%%
flowchart LR
    IN(["Ticket In"]) --> CLASSIFY["Classify<br>Intent"]
    CLASSIFY --> BILLING["Billing<br>Handler"]
    CLASSIFY --> TECH["Technical<br>Handler"]
    CLASSIFY --> GEN["General<br>Handler"]
    BILLING --> VALIDATE{"Can we<br>resolve?"}
    TECH --> VALIDATE
    GEN --> VALIDATE
    VALIDATE --> RESPOND["Generate<br>Response"]
    VALIDATE --> ESCALATE["Escalate to<br>Human"]:::escalate
    RESPOND --> OUT(["Done"])

    classDef escalate fill:#fee2e2,stroke:#f87171,color:#991b1b
```

---

## Level 3: Tool-Calling Agent - Scoped Autonomy

The agent decides which tools to call and in what order, but only within a fixed set of well-defined capabilities. This is where real autonomy starts.

```mermaid
%%{init: {'theme': 'default'}}%%
flowchart TB
    ROUTE(["Routed to: Billing Agent"]) --> AGENT["Billing<br>Agent"]:::agent

    AGENT <--> DB[("Customer<br>DB")]
    AGENT <--> CUSTOMER["Ask<br>Customer"]
    AGENT <--> POLICY["Policy<br>Lookup"]
    AGENT <--> CALC["Refund<br>Calculator"]

    AGENT --> RESULT(["Resolution"])

    classDef agent fill:#dcfce7,stroke:#4ade80,color:#166534
```

---

## Level 4: Agent Harness - Full Runtime Access

Instead of hand-picking tools, you give the agent a full runtime - the same capabilities you see in coding agents like Claude Code or Cursor. Bash execution, file system access, grep and search, web research, external APIs. The agent reasons about what to do, executes, observes, and iterates autonomously.

```mermaid
%%{init: {'theme': 'default'}}%%
flowchart TB
    ROUTE(["Routed to: Deep Analysis"]) --> HARNESS["Agent<br>Harness"]:::harness

    subgraph SHELL ["Shell & System"]
        direction LR
        BASH["Bash"]
        READ["Read /<br>Write"]
        GREP["Grep /<br>Glob"]
    end

    subgraph RESEARCH ["Web & Research"]
        direction LR
        SEARCH["Web<br>Search"]
        FETCH["Web<br>Fetch"]
    end

    subgraph APIS ["External APIs via MCP"]
        direction LR
        GATEWAY["Payment<br>Gateway"]
        CRM["CRM<br>System"]
        TICKETS["Ticketing<br>System"]
    end

    HARNESS <--> SHELL
    HARNESS <--> RESEARCH
    HARNESS <--> APIS

    HARNESS --> RESULT(["Report + Artifacts"])

    classDef harness fill:#fef3c7,stroke:#f59e0b,color:#92400e

    style SHELL fill:#f1f5f9,stroke:#cbd5e1,color:#334155
    style RESEARCH fill:#f1f5f9,stroke:#cbd5e1,color:#334155
    style APIS fill:#f1f5f9,stroke:#cbd5e1,color:#334155
```

---

## Level 5: Multi-Agent Orchestration - Delegated Autonomy

An orchestrator decomposes the task and delegates to specialized agents, each with their own tools, prompts, and (optionally) their own models. How delegation works depends on the architecture you choose:

- **Subagents (this example - Claude Agent SDK):** Each worker spins up in its own context window with its own system prompt and tools. It does its job independently and returns a result to the orchestrator. The orchestrator never sees the worker's internal reasoning - only the final output. This is how tools like Claude Code and Cursor handle it.
- **Passed-down agents (e.g. PydanticAI, LangGraph):** Instead of isolated subagents, you wire agents together in code - passing outputs from one to the next, sharing dependencies, or nesting agent calls. The control flow is more explicit and the context can be shared.

```mermaid
%%{init: {'theme': 'default'}}%%
flowchart TB
    IN(["Complex Request"]) --> ORCH["Orchestrator"]:::orch

    ORCH <--> W1["Research<br>Agent"]:::agent
    ORCH <--> W2["Drafting<br>Agent"]:::agent
    ORCH <--> W3["Compliance<br>Agent"]:::agent

    ORCH --> OUT(["Final Output"])

    classDef orch fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f
    classDef agent fill:#dcfce7,stroke:#4ade80,color:#166534
```

---

## The Full Picture: All Five Combined

The routing decision isn't about severity - it's about what the task *needs*. Each level trades off cost, latency, reliability, and capability differently. Use the simplest level that gets the job done.

```mermaid
%%{init: {'theme': 'default'}}%%
flowchart LR
    IN(["Customer<br>Request"]) --> CLASSIFY["Classify<br>Intent"] --> ROUTE{"Route"}

    ROUTE --> L1["Augmented<br>LLM"]
    ROUTE --> L3["Tool-Calling<br>Agent"]:::agent
    ROUTE --> L4["Agent<br>Harness"]:::harness
    ROUTE --> L5["Multi-Agent<br>Orchestrator"]:::orch

    L1 --> OUT(["Response"])
    L3 --> OUT
    L4 --> OUT
    L5 --> OUT

    classDef agent fill:#dcfce7,stroke:#4ade80,color:#166534
    classDef harness fill:#fef3c7,stroke:#f59e0b,color:#92400e
    classDef orch fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f
```

| | Augmented LLM | Tool-Calling Agent | Agent Harness | Multi-Agent |
|---|---|---|---|---|
| **Cost** | $ | $$ | $$$ | $$$$ |
| **Latency** | ~1s | ~5s | ~30s+ | ~60s+ |
| **Reliability** | Deterministic | High | Medium | Lower |
| **When to use** | Answer is retrievable | Needs a few specific tools | Needs exploration and reasoning | Needs parallel domain expertise |
