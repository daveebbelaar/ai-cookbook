[نسخهٔ فارسی](README.fa.md)
## Part 3: Simple Server Setup with Python SDK

### Building Your First MCP Server

Let's create a simple demo server with a tool:

```python
# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("DemoServer")

# Simple tool
@mcp.tool()
def say_hello(name: str) -> str:
    """Say hello to someone

    Args:
        name: The person's name to greet
    """
    return f"Hello, {name}! Nice to meet you."

# Run the server
if __name__ == "__main__":
    mcp.run()
```

### Running the Server

There are several ways to run your MCP server:

#### 1. Development Mode with MCP Inspector

The easiest way to test your server is using the MCP Inspector:

```bash
mcp dev server.py
```

This runs your server locally and connects it to the MCP Inspector, a web-based tool that lets you interact with your server's tools and resources directly. This is great for testing.

#### 2. Claude Desktop Integration

If you have Claude Desktop installed, you can install your server to use with Claude:

```bash
mcp install server.py
```

This will add your server to Claude Desktop's configuration, making it available to Claude.

#### 3. Direct Execution (only needed or SSE)

You can also run the server directly:

```bash
# Method 1: Running as a Python script
python server.py

# Method 2: Using UV (recommended)
uv run server.py
```

### What Happens When You Run an MCP Server?

When you run an MCP server:

1. The server initializes with the capabilities you've defined (tools, resources, etc.)
2. It starts listening for connections on a specific transport

By default, MCP servers don't use a traditional web server port. Instead, they use either:

- **stdio transport**: The server communicates through standard input and output (the default for `mcp run` and integration with Claude Desktop)
- **SSE transport**: For HTTP-based communication (used when explicitly configured)

If you want to expose your server over HTTP with a specific port, you need to modify your server to use the SSE transport:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MyServer", host="127.0.0.1", port=8050)

# Add your tools and resources here...

if __name__ == "__main__":
    # Run with SSE transport on port 8000
    mcp.run(transport="sse")
```

Then you can run it with:

```bash
python server.py
```

This will start your server at `http://127.0.0.1:8050`.

### Client-Side Implementation (with Standard I/O)

Now, let's see how to create a client that uses our server:

```python
import asyncio
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Define server parameters
    server_params = StdioServerParameters(
        command="python",  # The command to run your server
        args=["server.py"],  # Arguments to the command
    )

    # Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("add", arguments={"a": 2, "b": 3})
            print(f"2 + 3 = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

This client:

1. Creates a connection to our server via stdio
2. Establishes an MCP session
3. Lists available tools
4. Calls the `add` tool with arguments

### Client-Side Implementation (with Server-Sent Events)

Here's how to connect to your server with SSE:

```python
import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    # Connect to the server using SSE
    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("add", arguments={"a": 2, "b": 3})
            print(f"2 + 3 = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Client-Side Implementation (with Streamable HTTP) - **NEW**

> **Note**: Streamable HTTP transport was introduced on **March 24, 2025** and is now the **recommended approach for production deployments**, superseding SSE transport. [Learn more in the official documentation](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http).

**Why Streamable HTTP?**

Streamable HTTP offers several advantages over SSE:
- **Better Performance**: 3-5x improvement under high concurrency
- **Simplified Architecture**: Single endpoint instead of separate HTTP + SSE endpoints
- **Enhanced Scalability**: Better support for multi-node deployments
- **Modern Standards**: Built on current HTTP streaming standards

**How It Works:**

Streamable HTTP uses a single HTTP endpoint (`/mcp`) that supports both stateful and stateless operation modes. Unlike SSE which requires maintaining separate endpoints, Streamable HTTP provides a unified interface for all MCP communication.

Here's how to connect using the new Streamable HTTP transport:

```python
import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    # Connect to the server using Streamable HTTP
    async with streamablehttp_client("http://localhost:8050/mcp") as (read_stream, write_stream, get_session_id):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call our calculator tool
            result = await session.call_tool("add", arguments={"a": 2, "b": 3})
            print(f"2 + 3 = {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
```

**Key Differences from SSE:**

| **SSE Transport** | **Streamable HTTP Transport** |
|-------------------|-------------------------------|
| `/sse` endpoint | `/mcp` endpoint |
| Returns 2 values: `(read, write)` | Returns 3 values: `(read, write, get_session_id)` |
| Separate HTTP + SSE streams | Unified HTTP streaming |
| Good for development | **Recommended for production** |

### Which Approach Should You Choose?

- **Use stdio** if your client and server will be running in the same process or if you're starting the server process directly from your client.
- **Use Streamable HTTP** for production deployments where you need the best performance and scalability.
- **Use SSE** for development or when working with older MCP implementations that don't yet support Streamable HTTP.

For most production backend integrations, the **Streamable HTTP** approach offers the best performance and modern architecture, while stdio might be simpler for development or tightly coupled systems.