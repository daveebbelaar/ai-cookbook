from mcp.server.fastmcp import FastMCP
import sys

# Create an MCP server
mcp = FastMCP(
    name="Calculator",
    host="127.0.0.1",  # HTTP transports stay local
    port=8050,  # used for SSE and Streamable HTTP
    stateless_http=True,
)


# Add a simple calculator tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


# Run the server
if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if transport == "stdio":
        print("Running server with stdio transport", file=sys.stderr)
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("Running server with SSE transport")
        mcp.run(transport="sse")
    elif transport == "streamable-http":
        print("Running server with Streamable HTTP transport")
        mcp.run(transport="streamable-http")
    else:
        raise ValueError(f"Unknown transport: {transport}")
