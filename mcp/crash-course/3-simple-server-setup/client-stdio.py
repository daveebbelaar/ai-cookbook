import asyncio
import sys
from pathlib import Path
import nest_asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Interactive cells have no __file__; open them from this lesson folder.
SCRIPT_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

nest_asyncio.apply()  # Needed to run interactive python


async def main():
    # Define server parameters
    server_params = StdioServerParameters(
        command=sys.executable,  # Use the same environment as the client
        args=[str(SCRIPT_DIR / "server.py")],
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
