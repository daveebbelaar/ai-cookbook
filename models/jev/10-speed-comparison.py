"""Compare Jev, Claude Haiku, Opus 5, and Fable 5.1 on one ticket-routing task.
Run each model three times and print each result plus its average request time.
The first request includes connection setup; this small demo is not a general speed ranking.
"""

from time import perf_counter

from anthropic import Anthropic
from dotenv import load_dotenv
from typesafe_sdk import Choice, RetryPolicy, TypeSafeClient

load_dotenv()
jev = TypeSafeClient(model="jev-1.13.0", retry=RetryPolicy(max_retries=0))
claude = Anthropic(max_retries=0)

# --------------------------------------------------------------
# Give every model the same ticket and answer options
# --------------------------------------------------------------

ticket = "I was charged twice. Please refund the duplicate."
instructions = "Which team should handle this support ticket?"
criteria = {
    "billing": "Payments, charges, or refunds.",
    "technical": "Errors, bugs, or login failures.",
    "other": "Anything else.",
}
question = Choice(instructions=instructions, criteria=criteria)
# --------------------------------------------------------------
# Run each model three times, then print the averages
# --------------------------------------------------------------

models = [
    "jev-1.13.0",
    "claude-haiku-4-5-20251001",
    "claude-opus-5",
    "claude-fable-5-1",
]
timings = {model: [] for model in models}

for run in range(3):
    print(f"\nRun {run + 1}")
    for model in models:
        start = perf_counter()
        if model == "jev-1.13.0":
            response = jev.system_one(state=ticket, questions={"team": question})
            team = response.choices["team"].choice
        else:
            response = claude.messages.create(
                model=model,
                max_tokens=2048,
                system=instructions
                + " Options: "
                + str(criteria)
                + " Return only the category name: billing, technical, or other.",
                messages=[{"role": "user", "content": ticket}],
            )
            team = "".join(
                block.text for block in response.content if block.type == "text"
            ).strip()
        assert team in criteria, f"Unexpected category from {model}: {team!r}"
        elapsed_ms = (perf_counter() - start) * 1000
        timings[model].append(elapsed_ms)
        print(f"{model}: {team}, {elapsed_ms:.0f} ms")

print("\nAverage of 3 runs (including the first request)")
for model, times in timings.items():
    print(f"{model}: {sum(times) / len(times):.0f} ms")
