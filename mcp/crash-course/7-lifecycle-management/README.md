[نسخهٔ فارسی](README.fa.md)
# Lifecycle Management in MCP

Lifecycle management is a crucial aspect of the Model Context Protocol (MCP) that helps you control the initialization, operation, and termination of MCP servers and clients. Understanding lifecycle management is essential for building robust MCP applications.

## What is Lifecycle Management?

Lifecycle management in MCP refers to the process of properly initializing, maintaining, and terminating connections between MCP clients and servers. It ensures that resources are properly allocated and released, and that communication channels are established and closed correctly.

## Key Components of Lifecycle Management

### 1. Initialization

Initialization is the first step in the MCP lifecycle:

- **Client Initialization**: The client establishes a connection to the server and negotiates protocol versions
- **Server Initialization**: The server validates the client's request and prepares to handle tool calls
- **Version Negotiation**: Both parties agree on a compatible protocol version to use for the session

```python
# Client initialization example
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize the connection
        await session.initialize()
```

### 2. Operation

During the operation phase:

- **Tool Registration**: The server exposes its tools to the client
- **Tool Discovery**: The client discovers available tools from the server
- **Tool Execution**: The client calls tools and the server executes them
- **Resource Management**: The server manages resources needed for tool execution

```python
# Tool discovery example
tools_result = await session.list_tools()
print("Available tools:")
for tool in tools_result.tools:
    print(f"  - {tool.name}: {tool.description}")

# Tool execution example
result = await session.call_tool(
    tool_call.function.name,
    arguments=json.loads(tool_call.function.arguments),
)
```

### 3. Termination

Termination ensures proper cleanup:

- **Resource Cleanup**: All resources allocated during the session are released
- **Connection Closure**: Communication channels are properly closed
- **State Reset**: Server state is reset for the next session

```python
# Termination happens automatically when exiting the context manager
async with ClientSession(read, write) as session:
    # Session operations
    # ...
# Session is automatically terminated here
```

## Advanced Lifecycle Management with the Lifespan Object

For more complex applications, MCP provides a feature called the **lifespan object** that helps manage application-level resources throughout the entire lifecycle of an MCP server.

### What is the Lifespan Object?

The lifespan object is an asynchronous context manager that:

1. Initializes resources when the server starts
2. Makes those resources available to all tools during the server's operation
3. Properly cleans up resources when the server shuts down

### How to Use the Lifespan Object

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

# Define a type-safe context class
@dataclass
class AppContext:
    db: Database  # Replace with your actual resource type

# Create the lifespan context manager
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    # Initialize resources on startup
    db = await Database.connect()
    try:
        # Make resources available during operation
        yield AppContext(db=db)
    finally:
        # Clean up resources on shutdown
        await db.disconnect()

# Create the MCP server with the lifespan
mcp = FastMCP("My App", lifespan=app_lifespan)

# Use the lifespan context in tools
@mcp.tool()
def query_db(ctx: Context) -> str:
    """Tool that uses initialized resources"""
    db = ctx.request_context.lifespan_context.db
    return db.query()
```

### Benefits of Using the Lifespan Object

1. **Type Safety**: The lifespan context is strongly typed, providing better IDE support and error checking
2. **Resource Management**: Ensures resources are properly initialized and cleaned up
3. **Dependency Injection**: Provides a clean way to inject dependencies into tools
4. **Separation of Concerns**: Separates resource management from tool implementation

## Conclusion

By understanding and implementing the initialization, operation, and termination phases correctly, and leveraging the lifespan object for application-level resources, you can create more reliable, efficient, and secure MCP integrations.

For more detailed information on lifecycle management, refer to the [MCP Lifecycle](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle#lifecycle).