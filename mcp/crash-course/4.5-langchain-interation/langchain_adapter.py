from langchain_mcp_adapters.client import MultiServerMCPClient
import nest_asyncio
import json
import asyncio

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv("../../../.env")
os.getenv("AIRTABLE_API_KEY", "")

# Allow nested event loops (for interactive environments)
nest_asyncio.apply()

async def main():
    # Connect to MCP server
    client = MultiServerMCPClient(
        {
            # "weather": {
            #     "command": "python",
            #     "args": ["/home/safeer/Documents/devops/mcp/mcp/crash-course/4.5-langchain-interation/server.py"],
            #     "transport": "stdio",
            # },
            "weather_n8n": {
                "url": "http://localhost:5678/mcp/mcp-weather-triger/sse",
                "transport": "sse",
            }
            # You can add more tools here if needed
        }
    )

    # Get available tools from the MCP server
    tools = await client.get_tools()
    print("Available tools:", tools)

    # Set up the LLM
    llm = ChatOpenAI(model="gpt-4o-mini")
    agent = create_react_agent(llm , tools=tools)
    # llm_with_tools = agent.get (tools)

    # LLM-driven tool call
    # response = llm_with_tools.invoke("What is the grid for Seattle?")
    # print("LLM response:", response)

    # # Direct tool call (async)
    # tool_result = await tools[0].invoke(
    #     input={"longitude": "-122.3321", "latitude": "47.6062"}
    # )
    # print("Direct tool result:", tool_result)

    # LLM-driven tool call with agent
    # response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "What is the grid for Seattle?"}]} 
    #     )
    
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "What is the weather of Seattle and Toronto?"}]}
    )

    print( response["messages"][-1].content) 

    # Test direct tool call
    # tool_result = await tools[0].ainvoke(input={"longitude": "-122.3321", "latitude": "47.6062"})
    # print("Direct tool result:", tool_result)



if __name__ == "__main__":
    asyncio.run(main())

# Who to call mcp tool in langchian or langgraph