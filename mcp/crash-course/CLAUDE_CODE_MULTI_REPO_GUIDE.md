# Claude Code Multi-Repository Access Guide

## Use Case: Working Across Multiple GitHub Repositories

When working on projects that span multiple repositories (like integrating ai-cookbook with tool-claude-conduit), you need to start Claude Code from a parent directory that contains all relevant repos.

## Current Limitation

Claude Code can only access directories that are **children** of the starting working directory for security reasons. This means:

❌ **Won't Work**: Starting in `/ai-cookbook/mcp/crash-course/` and trying to access `/tool-claude-conduit/`
✅ **Will Work**: Starting in `/github/` and accessing both `/github/ai-cookbook/` and `/github/tool-claude-conduit/`

## Solution: Start from Parent Directory

### Step 1: Navigate to Parent Directory
```bash
cd /Users/norrisa/Documents/dev/github/
```

### Step 2: Start Claude Code with Project Context
```bash
# Option A: Use the project command for AI Cookbook context
claude-code --project ai-cookbook

# Option B: Start normally and navigate as needed
claude-code
```

### Step 3: Inform Claude of Repository Structure
When starting the session, provide this context:

```
I'm working from /Users/norrisa/Documents/dev/github/ which contains:
- ai-cookbook/ (main project)
- tool-claude-conduit/ (integration target)
- [other repos as needed]

Please start by understanding the ai-cookbook/mcp/crash-course project, then integrate with tool-claude-conduit for testing and comparison.
```

## Benefits of Multi-Repo Access

✅ **Cross-repository integration testing**
✅ **Direct npm/pip commands in any repo**
✅ **File comparison across projects**
✅ **Live testing of integrations**
✅ **Complete development workflows**

## Example Multi-Repo Commands

```bash
# Install dependencies in tool-claude-conduit
cd tool-claude-conduit && npm install

# Test MCP server from ai-cookbook
cd ai-cookbook/mcp/crash-course/3-simple-server-setup && python server.py

# Start claude-conduit bridge
cd tool-claude-conduit && npm start

# Test integration between both systems
curl http://localhost:3001/tools
```

## Workflow Recommendation

1. **Start Session**: `cd /Users/norrisa/Documents/dev/github/ && claude-code --project ai-cookbook`
2. **Establish Context**: Explain the multi-repo integration goal
3. **Sequential Setup**: Set up each repo's dependencies
4. **Cross-Testing**: Validate integrations between repos
5. **Documentation**: Update both repos with integration examples

## Project Command Usage

The `--project` flag helps Claude understand the primary project context while still having access to related repositories:

```bash
# Focus on ai-cookbook but access tool-claude-conduit
claude-code --project ai-cookbook

# Alternative: Let Claude discover context naturally
claude-code
```

## Security Considerations

- Claude Code's directory restrictions are intentional security features
- Starting from a parent directory is the recommended approach for multi-repo work
- Always verify the working directory before starting sensitive operations

## Template Prompt for Multi-Repo Sessions

```
I'm starting from /Users/norrisa/Documents/dev/github/ to work on integrating:
- ai-cookbook/mcp/crash-course (MCP educational module)
- tool-claude-conduit (HTTP bridge for MCP servers)

Goal: [Describe your specific integration goal]
Previous work: [Reference any prior work or context]
Next steps: [What you want to accomplish]
```

This approach enables Claude Code to work effectively across multiple repositories while respecting security boundaries.