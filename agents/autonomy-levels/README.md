# The 5 Levels of AI Autonomy

The best production AI systems use the simplest level of autonomy at each step — and only escalate complexity when the task demands it.

| Level | Pattern | Code | Framework |
|---|---|---|---|
| 1 | Augmented LLM | [`1-augmented-llm.py`](1-augmented-llm.py) | PydanticAI |
| 2 | Prompt Chains & Routing | [`2-prompt-chains.py`](2-prompt-chains.py) | PydanticAI |
| 3 | Tool-Calling Agent | [`3-tool-calling-agent.py`](3-tool-calling-agent.py) | PydanticAI |
| 4 | Agent Harness | [`4-agent-harness.py`](4-agent-harness.py) | Claude Agent SDK |
| 5 | Multi-Agent Orchestration | [`5-multi-agent.py`](5-multi-agent.py) | Claude Agent SDK |

---

## Level 1: Augmented LLM — Single API Call

One model call with the right context: system prompt, few-shot examples, structured output, retrieval. No loops, no tools, no autonomy. This handles more than most people think.

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#dbeafe"
    primaryTextColor: "#1e3a5f"
    primaryBorderColor: "#93c5fd"
    lineColor: "#94a3b8"
  flowchart:
    curve: linear
    padding: 16
    nodeSpacing: 50
    rankSpacing: 70
---
flowchart LR
    IN(["Input"]):::input --> LLM["LLM"]:::llm

    RAG["Retrieved<br>Context"]:::context -.-> LLM
    FEW["Few-Shot<br>Examples"]:::context -.-> LLM
    SYS["System<br>Prompt"]:::context -.-> LLM

    LLM --> OUT(["Structured<br>Output"]):::input

    classDef input fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f,stroke-width:2px
    classDef llm fill:#f0f9ff,stroke:#93c5fd,color:#1e3a5f,stroke-width:2px
    classDef context fill:#f1f5f9,stroke:#cbd5e1,color:#475569,stroke-width:1px
```

---

## Level 2: Prompt Chains & Routing — Deterministic DAGs

Multiple LLM calls orchestrated through fixed paths. Each step validates its output before passing to the next. No model makes decisions about control flow — the code does.

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#dbeafe"
    primaryTextColor: "#1e3a5f"
    primaryBorderColor: "#93c5fd"
    lineColor: "#94a3b8"
  flowchart:
    curve: linear
    padding: 16
    nodeSpacing: 50
    rankSpacing: 70
---
flowchart LR
    IN(["Ticket In"]):::input --> CLASSIFY["Classify<br>Intent"]:::process
    CLASSIFY --> BILLING["Billing<br>Handler"]:::process
    CLASSIFY --> TECH["Technical<br>Handler"]:::process
    CLASSIFY --> GEN["General<br>Handler"]:::process
    BILLING --> VALIDATE{"Can we<br>resolve?"}:::decision
    TECH --> VALIDATE
    GEN --> VALIDATE
    VALIDATE --> RESPOND["Generate<br>Response"]:::process
    VALIDATE --> ESCALATE["Escalate to<br>Human"]:::escalate
    RESPOND --> OUT(["Done"]):::input

    classDef input fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f,stroke-width:2px
    classDef process fill:#f0f9ff,stroke:#93c5fd,color:#1e3a5f,stroke-width:1px
    classDef decision fill:#fef3c7,stroke:#fbbf24,color:#92400e,stroke-width:2px
    classDef escalate fill:#fee2e2,stroke:#f87171,color:#991b1b,stroke-width:1px
```

---

## Level 3: Tool-Calling Agent — Scoped Autonomy

The agent decides which tools to call and in what order, but only within a fixed set of well-defined capabilities. This is where real autonomy starts.

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#dbeafe"
    primaryTextColor: "#1e3a5f"
    primaryBorderColor: "#93c5fd"
    lineColor: "#94a3b8"
  flowchart:
    curve: linear
    padding: 16
    nodeSpacing: 50
    rankSpacing: 70
---
flowchart TB
    ROUTE(["Routed to: Billing Agent"]):::input --> AGENT["Billing<br>Agent"]:::agent

    AGENT <--> DB[("Customer<br>DB")]:::tool
    AGENT <--> CUSTOMER["Ask<br>Customer"]:::tool
    AGENT <--> POLICY["Policy<br>Lookup"]:::tool
    AGENT <--> CALC["Refund<br>Calculator"]:::tool

    AGENT --> RESULT(["Resolution"]):::input

    classDef input fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f,stroke-width:2px
    classDef agent fill:#dcfce7,stroke:#4ade80,color:#166534,stroke-width:2px
    classDef tool fill:#f0f9ff,stroke:#93c5fd,color:#1e3a5f,stroke-width:1px
```

---

## Level 4: Agent Harness — Full Runtime Access

Instead of hand-picking tools, you give the agent a full runtime — document analysis, web research, API access, dynamic data extraction. The agent reasons about what to do, executes, observes, and iterates.

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#dbeafe"
    primaryTextColor: "#1e3a5f"
    primaryBorderColor: "#93c5fd"
    lineColor: "#94a3b8"
  flowchart:
    curve: linear
    padding: 16
    nodeSpacing: 50
    rankSpacing: 70
---
flowchart TB
    ROUTE(["Routed to: Deep Analysis"]):::input --> HARNESS["Agent<br>Harness"]:::harness

    HARNESS <--> DOCS["Document<br>Analysis"]:::tool
    HARNESS <--> WEB["Web<br>Research"]:::tool
    HARNESS <--> APIS["External<br>APIs"]:::tool
    HARNESS <--> DATA["Data<br>Extraction"]:::tool
    HARNESS <--> CHECK["Cross-<br>Reference"]:::tool

    HARNESS --> RESULT(["Report + Artifacts"]):::input

    classDef input fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f,stroke-width:2px
    classDef harness fill:#fef3c7,stroke:#f59e0b,color:#92400e,stroke-width:2px
    classDef tool fill:#f0f9ff,stroke:#93c5fd,color:#1e3a5f,stroke-width:1px
```

---

## Level 5: Multi-Agent Orchestration — Delegated Autonomy

An orchestrator decomposes the task and delegates to specialized worker agents, each with their own tools and context. Every worker reports back to the orchestrator — it decides what to delegate next, what to retry, and when to finalize.

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#dbeafe"
    primaryTextColor: "#1e3a5f"
    primaryBorderColor: "#93c5fd"
    lineColor: "#94a3b8"
  flowchart:
    curve: linear
    padding: 16
    nodeSpacing: 50
    rankSpacing: 70
---
flowchart TB
    IN(["Complex Request"]):::input --> ORCH["Orchestrator"]:::orch

    ORCH <--> W1["Research<br>Agent"]:::agent
    ORCH <--> W2["Drafting<br>Agent"]:::agent
    ORCH <--> W3["Compliance<br>Agent"]:::agent

    ORCH --> OUT(["Final Output"]):::input

    classDef input fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f,stroke-width:2px
    classDef orch fill:#ede9fe,stroke:#8b5cf6,color:#5b21b6,stroke-width:2px
    classDef agent fill:#dcfce7,stroke:#4ade80,color:#166534,stroke-width:1px
```

---

## The Full Picture: All Five Combined

The routing decision isn't about severity — it's about what the task *needs*. Each level trades off cost, latency, reliability, and capability differently. Use the simplest level that gets the job done.

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#dbeafe"
    primaryTextColor: "#1e3a5f"
    primaryBorderColor: "#93c5fd"
    lineColor: "#94a3b8"
  flowchart:
    curve: linear
    padding: 16
    nodeSpacing: 40
    rankSpacing: 80
---
flowchart LR
    IN(["Customer<br>Request"]):::input --> CLASSIFY["Classify<br>Intent"]:::dag --> ROUTE{"Route"}:::decision

    ROUTE --> L1["Augmented<br>LLM"]:::dag
    ROUTE --> L3["Tool-Calling<br>Agent"]:::agent
    ROUTE --> L4["Agent<br>Harness"]:::harness
    ROUTE --> L5["Multi-Agent<br>Orchestrator"]:::orch

    L1 --> OUT(["Response"]):::input
    L3 --> OUT
    L4 --> OUT
    L5 --> OUT

    classDef input fill:#dbeafe,stroke:#60a5fa,color:#1e3a5f,stroke-width:2px
    classDef dag fill:#f0f9ff,stroke:#93c5fd,color:#1e3a5f,stroke-width:1px
    classDef decision fill:#fef3c7,stroke:#fbbf24,color:#92400e,stroke-width:2px
    classDef agent fill:#dcfce7,stroke:#4ade80,color:#166534,stroke-width:2px
    classDef harness fill:#fef3c7,stroke:#f59e0b,color:#92400e,stroke-width:2px
    classDef orch fill:#ede9fe,stroke:#8b5cf6,color:#5b21b6,stroke-width:2px
```

| | Augmented LLM | Tool-Calling Agent | Agent Harness | Multi-Agent |
|---|---|---|---|---|
| **Cost** | $ | $$ | $$$ | $$$$ |
| **Latency** | ~1s | ~5s | ~30s+ | ~60s+ |
| **Reliability** | Deterministic | High | Medium | Lower |
| **When to use** | Answer is retrievable | Needs a few specific tools | Needs exploration and reasoning | Needs parallel domain expertise |

