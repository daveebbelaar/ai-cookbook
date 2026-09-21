from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Create an MCP server
mcp = FastMCP(
    name="Calculator",
    host="0.0.0.0",  # Required inside Docker; publish only to loopback
    port=8050,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["localhost:8050", "127.0.0.1:8050"],
        allowed_origins=["http://localhost:8050", "http://127.0.0.1:8050"],
    ),
)


# Add a simple calculator tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


# Run the server
if __name__ == "__main__":
    print("Running server with SSE transport")
    mcp.run(transport="sse")
