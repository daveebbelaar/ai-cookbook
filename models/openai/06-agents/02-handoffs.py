from agents import Agent, Runner
from pprint import pprint

tech_support_agent = Agent(
    name="Tech Support Agent",
    instructions="You handle technical issues with our product. Be concise and helpful.",
)

billing_agent = Agent(
    name="Billing Agent",
    instructions="You handle billing and payment inquiries. Be concise and helpful.",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Analyze the customer ticket and handoff to the appropriate specialist agent.",
    handoffs=[tech_support_agent, billing_agent],
)

# result = await Runner.run(
#     triage_agent, input="My app keeps crashing when I try to open it."
# )

# result = await Runner.run(
#     triage_agent, input="I was charged twice for my subscription."
# )

result = await Runner.run(
    triage_agent, input="I can't log in and I also have a billing question."
)

print("\n=== FINAL OUTPUT ===\n")
print(result.final_output)

print("\n=== LAST AGENT ===\n")
print(result.last_agent.name if result.last_agent else None)

print("\n=== NEW ITEMS (simplified) ===\n")
for i, item in enumerate(result.new_items, start=1):
    print(f"Item #{i}")
    print("type:", item.type)

    if hasattr(item, "agent") and item.agent:
        print("agent:", item.agent.name)

    if hasattr(item, "raw_item"):
        print("raw_item:")
        pprint(item.raw_item)

    print()

print("\n=== RAW RESPONSES ===\n")
for i, response in enumerate(result.raw_responses, start=1):
    print(f"Raw Response #{i}")

    print("Response ID:", response.response_id)
    print("Tokens Used:", response.usage.total_tokens)

    print("\nOutput:")
    for item in response.output:
        print(" →", type(item).__name__)
        pprint(item)

    print()


# --------------------------------------------------------------
# Agents as a tool
# --------------------------------------------------------------

tech_support_agent = Agent(
    name="Tech Support Agent",
    instructions="You handle technical issues with our product. Be concise and helpful.",
)

billing_agent = Agent(
    name="Billing Agent",
    instructions="You handle billing and payment inquiries. Be concise and helpful.",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Analyze the request and call the appropriate specialists. "
        "You may call more than one specialist if needed."
    ),
    tools=[
        tech_support_agent.as_tool(
            tool_name="ask_tech_support",
            tool_description="Ask the tech support specialist about technical issues.",
        ),
        billing_agent.as_tool(
            tool_name="ask_billing",
            tool_description="Ask the billing specialist about payments, charges, or subscriptions.",
        ),
    ],
)

# result = await Runner.run(
#     triage_agent, input="My app keeps crashing when I try to open it."
# )

# result = await Runner.run(
#     triage_agent, input="I was charged twice for my subscription."
# )

result = await Runner.run(
    triage_agent, input="I can't log in and I also have a billing question."
)


print("\n=== FINAL OUTPUT ===\n")
print(result.final_output)

print("\n=== LAST AGENT ===\n")
print(result.last_agent.name if result.last_agent else None)

print("\n=== NEW ITEMS (simplified) ===\n")
for i, item in enumerate(result.new_items, start=1):
    print(f"Item #{i}")
    print("type:", item.type)

    if hasattr(item, "agent") and item.agent:
        print("agent:", item.agent.name)

    if hasattr(item, "raw_item"):
        print("raw_item:")
        pprint(item.raw_item)

    print()

print("\n=== RAW RESPONSES ===\n")
for i, response in enumerate(result.raw_responses, start=1):
    print(f"Raw Response #{i}")

    print("Response ID:", response.response_id)
    print("Tokens Used:", response.usage.total_tokens)

    print("\nOutput:")
    for item in response.output:
        print(" →", type(item).__name__)
        pprint(item)

    print()
