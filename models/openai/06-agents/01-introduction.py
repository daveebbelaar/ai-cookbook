from agents import Agent, Runner, function_tool
from pprint import pprint
# import nest_asyncio

# nest_asyncio.apply()

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
result = await Runner.run(agent, "Write a haiku about recursion in programming.")

print(result.final_output)  # the last message text
pprint(result.raw_responses)  # what the model said
pprint(result.new_items)  # what the agent did


# --------------------------------------------------------------
# Agent with Function Calling
# --------------------------------------------------------------


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


agent = Agent(
    name="Weather assistant",
    instructions="Answer weather questions using the weather tool.",
    tools=[get_weather],
)

result = await Runner.run(agent, "What is the weather in Dubai?")

print(result.final_output)  # the last message text
pprint(result.raw_responses)  # what the model said
pprint(result.new_items)  # what the agent did


# --------------------------------------------------------------
# Agent streaming
# --------------------------------------------------------------


agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
)

result = Runner.run_streamed(agent, "Write a haiku about recursion in programming.")

async for event in result.stream_events():
    print("\n====================")
    print("EVENT TYPE:", type(event).__name__)
    pprint(event)

print("\n=== FINAL OUTPUT ===\n")
print(result.final_output)


# --------------------------------------------------------------
# Agent streaming with Toolcall
# --------------------------------------------------------------


@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."


agent = Agent(
    name="Weather assistant",
    instructions="Answer weather questions using the weather tool.",
    tools=[get_weather],
)

result = Runner.run_streamed(agent, "What is the weather in Dubai?")

async for event in result.stream_events():
    print("\n====================")
    print("EVENT TYPE:", type(event).__name__)
    pprint(event)

print("\n=== FINAL OUTPUT ===\n")
print(result.final_output)

print("\n=== NEW ITEMS AFTER STREAM ===\n")
for item in result.new_items:
    print(item.type)
    pprint(item.raw_item)
    print("\n====================")
