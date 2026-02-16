# Snowflake MCP Server

A minimal MCP (Model Context Protocol) server that exposes Snowflake SQL queries as a tool for LLMs like Claude and Cursor.

## Minimal MCP Server Requirements

To create a basic MCP server, you need just **three things**:

### 1. Create the Server Instance
```python
mcp = FastMCP("SnowflakeMCP")
```
**What it does**: Creates an MCP server instance with a name. This is your server object that will manage tools, resources, and client connections.

### 2. Register Tools with `@mcp.tool()`
```python
@mcp.tool()
def run_query(sql: str) -> dict:
    ...
```
**What it does**: The decorator registers your Python function as an MCP tool. It extracts the function name, docstring, and type hints to create the tool schema that clients can discover via `list_tools()`.

### 3. Start the Server
```python
mcp.run(transport="stdio")
```
**What it does**: Starts the MCP server loop. With `transport="stdio"`, it communicates via standard input/output (stdin/stdout), which is the default for MCP servers integrated with Claude Desktop or Cursor.

---

### FastMCP vs Low-Level SDK

**FastMCP (what we use here)**:
- ✅ **No async required**: Write normal synchronous Python functions
- ✅ **Simple**: Just `mcp.run(transport="stdio")` and you're done
- ✅ **Hides complexity**: All async plumbing (event loops, stdio streams, message parsing) happens inside the library

**Low-Level MCP SDK**:
- ⚙️ **Async required**: You must write `async def` functions and manage the event loop yourself
- ⚙️ **More control**: You manually handle stdio streams and server lifecycle:
  ```python
  async def main():
      async with stdio_server() as (read, write):
          await server.run(read, write)
  asyncio.run(main())
  ```
- ⚙️ **More boilerplate**: More code to write, but gives you fine-grained control

**Bottom line**: FastMCP is a convenience wrapper that makes MCP servers easier to build by hiding the async complexity. The low-level SDK gives you more control but requires understanding async/await patterns.

---

## Going Deeper

Now that you understand the minimal requirements, let's dive deeper into how this Snowflake server works. The sections below explain:

- **What this specific server does** — the Snowflake query tool and its behavior
- **How `@mcp.tool()` works** — detailed explanation of the decorator's magic
- **How to set it up and use it** — practical steps to get it running

## What It Does

This server provides a single tool: `run_query(sql: str)` that:
- Connects to Snowflake using credentials from environment variables
- Only allows **read-only** SQL queries (SELECT, WITH, SHOW, DESCRIBE, EXPLAIN)
- Returns query results as structured data (columns, row count, and rows as dictionaries)

## Understanding `@mcp.tool()`

The `@mcp.tool()` decorator is what makes your Python function available to MCP clients. Here's what it does:

**Conceptually**: It tells the MCP server: *"This Python function is a tool you can expose to clients."*

**Concretely**, when you write:

```python
@mcp.tool()
def run_query(sql: str) -> dict:
    ...
```

The decorator:

1. **Registers the function with the MCP server**:
   - Stores its name (`"run_query"`), docstring, argument schema (from type hints), and return type
   - When a client calls `list_tools()`, this function appears as an available tool with its description

2. **Wraps it in MCP plumbing**:
   - When an MCP client sends `"call_tool": {"name": "run_query", "arguments": {...}}`
   - FastMCP automatically deserializes JSON → Python types, calls your function, then serializes the result back to MCP responses

3. **Keeps your function "normal"**:
   - You just write regular Python (synchronous, in this case)
   - No need to manually parse requests or build MCP JSON responses

So `@mcp.tool()` is the bridge that turns `run_query(sql: str)` into a first-class MCP tool that Claude/Cursor can discover and invoke.

## Setup

### 1. Install Dependencies

```bash
uv pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in this directory with your Snowflake credentials:

```env
# Required
SNOWFLAKE_ACCOUNT=your-account-id
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password

# Optional but recommended
SNOWFLAKE_ROLE=ANALYST
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=MY_DB
SNOWFLAKE_SCHEMA=PUBLIC
```

### 3. Run the Server

**Option A: Run with MCP Inspector (for testing)**

The Inspector runs **two** processes that work together (1:1): the **client** (web UI you open in the browser) and the **proxy** (bridge between the UI and your MCP server). Each has its own port:

| Port type   | Env var       | Default | Meaning |
|------------|----------------|---------|--------|
| **Client** | `CLIENT_PORT`  | 6274    | Web UI — open this in your browser |
| **Server** | `SERVER_PORT`  | 6277    | Proxy — the UI talks to it; it talks to `server.py` via stdio |

From this directory (`mcp/snowflake-mcp`):

```bash
uv run mcp dev server.py
```

Then open **http://localhost:6274** (or whatever `CLIENT_PORT` you set). If the default ports are in use, override one or both:

```bash
CLIENT_PORT=8080 SERVER_PORT=9000 uv run mcp dev server.py
```

**Option B: Direct execution**
```bash
uv run server.py
```

**Option C: With Claude Desktop**

Add to your Claude Desktop MCP configuration:
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/path/to/mcp/snowflake-mcp"
    }
  }
}
```

## Usage

Once the server is running, clients can:

1. **List available tools**: `list_tools()` → returns `run_query`
2. **Call the tool**: `call_tool("run_query", {"sql": "SELECT * FROM users LIMIT 10"})`
3. **Receive structured results**:
   ```json
   {
     "columns": ["id", "name", "email"],
     "row_count": 10,
     "rows": [
       {"id": 1, "name": "Alice", "email": "alice@example.com"},
       ...
     ]
   }
   ```

## Safety

The server only allows read-only SQL queries. Queries starting with `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `ALTER`, `DROP`, etc. will be rejected with an error.

## Architecture Notes

- **Transport**: Uses `stdio` transport (standard input/output)
- **Connection Strategy**: Opens a fresh Snowflake connection per query call (simple and robust)
- **Framework**: Built with FastMCP, which handles all the async plumbing internally
