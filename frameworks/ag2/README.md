# AG2 (formerly AutoGen)

Build multi-agent AI systems with [AG2](https://ag2.ai/) — an open-source framework
where agents collaborate through natural conversation.

AG2 provides a conversation-centric approach to building AI agents:
agents communicate through dialogue, tools are registered declaratively,
and multi-agent orchestration happens automatically via GroupChat.

## What's Inside

```
ag2/
├── 1-getting-started/     # Your first AG2 agent
├── 2-core-concepts/       # Two-agent chat, tools, human-in-the-loop
└── 3-multi-agent/         # GroupChat orchestration with specialist agents
```

## Quick Setup

```bash
# Install dependencies
uv add ag2[openai] python-dotenv

# Or with pip
pip install ag2[openai] python-dotenv
```

Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your-api-key
```

## Resources

- [AG2 Documentation](https://docs.ag2.ai/)
- [AG2 GitHub](https://github.com/ag2ai/ag2)
