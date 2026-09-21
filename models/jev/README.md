# Jev - System One

The [background articles](docs/README.md) explain the company behind Jev, what is known about the model, and how its decisions fit into a Python application. The setup instructions and runnable examples are below.

## What is different?

[Jev](https://docs.typesafe.ai/introduction) is TypeSafe's System One model. You send **state plus typed questions**, and receive decisions and probabilities. It does not generate a chat reply. Its API and Python SDK differ from OpenAI's, but the examples below follow the same small, step-by-step style as the [OpenAI examples](../openai/05-responses/).

| Primitive | Support example | Result |
| --- | --- | --- |
| Choice | Which team handles this ticket? | A known label, probabilities, and confidence |
| Score | How frustrated is the customer? | A numeric position on your rubric, probabilities, and confidence |
| Noul | Does the customer request a refund? | Probability of yes, from 0 to 1 |

**Define the options yourself.** Choice selects from them; Score can fall between rubric levels; Noul is a probability, not a severity score. Independent questions can share one request. They cannot read one another's answers. [Primitive reference](https://docs.typesafe.ai/primitives).

**Typed output does not guarantee a correct decision.** Jev can misunderstand a ticket. It also has documented weaknesses with arithmetic, dates, indirection, and adversarial text. Keep calculations in Python, test decisions on representative tickets, and use a generative model when you need free-form writing. [Known limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13).

## API pricing

**Jev 1.13 costs $0.042 per million input tokens, with free output tokens** through TypeSafe's direct API. That is $42 per billion input tokens, not $0.42 per million. [Official model pricing](https://docs.typesafe.ai/models).

Checked September 21, 2026. USD per million tokens at standard paid API rates for text input, excluding caching, batch discounts, tool fees, and gateway markups. These are price comparisons, not claims of equal capability or token usage.

**For a simple cost illustration**, 100,000 requests of 500 input tokens cost $2.10 with Jev. Haiku costs $50 for those input tokens, plus $5 if each response uses 10 output tokens: $55 total. This assumes the stated token counts, no caching, and no extra reasoning tokens; actual tokenization and prompts differ. The roughly 26x difference in this illustration is not a universal per-task saving. Against Flash-Lite, the same arithmetic is $5.40, around 2.6x Jev. Cheap alternatives make the comparison more useful than only comparing against flagship models.

## Examples

| File | What you learn |
| --- | --- |
| [01-basic.py](01-basic.py) | Make one request and print the answer |
| [02-choice.py](02-choice.py) | Choice: connect and route one ticket |
| [03-score.py](03-score.py) | Score: rate frustration on an ordered rubric |
| [04-noul.py](04-noul.py) | Noul: estimate the probability of a refund request |
| [05-state.py](05-state.py) | Send state as a string, JSON object (dict), or JSON array (list) |
| [06-criteria.py](06-criteria.py) | Define Choice options, Score levels, and optional Noul criteria |
| [07-ticket-triage.py](07-ticket-triage.py) | Ask Choice, Score, and Noul questions together |
| [09-multistep-workflow.py](09-multistep-workflow.py) | Fetch evidence, ask a dependent question, apply business rules |
| [10-speed-comparison.py](10-speed-comparison.py) | Compare Jev with Claude Haiku, Opus 5, and Fable 5.1 |

## Patterns from the Jev docs

Each of the four [documented patterns](https://docs.typesafe.ai/patterns) has a standalone customer-support example. These build on the basic examples above. Timing is limited to the four-model speed comparison in [10-speed-comparison.py](10-speed-comparison.py).

| File | Pattern | What to watch |
| --- | --- | --- |
| [01-speculative-fan-out.py](patterns/01-speculative-fan-out.py) | [Speculative fan-out](https://docs.typesafe.ai/patterns/fan-out) | Ask bug and billing questions together, then ignore irrelevant answers |
| [02-confidence-gated-routing.py](patterns/02-confidence-gated-routing.py) | [Confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing) | Apply different thresholds to a lookup and a cancellation request |
| [03-composite-scoring.py](patterns/03-composite-scoring.py) | [Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring) | Normalize impact, urgency, and frustration, then rank with explicit weights |
| [04-intent-routing.py](patterns/04-intent-routing.py) | [Intent routing](https://docs.typesafe.ai/patterns/intent-routing) | Route to a local lookup, a real Haiku draft, or a local human-review record |

## Reading the latency

The [speed comparison](10-speed-comparison.py) runs Jev, Claude Haiku 4.5, Opus 5, and Fable 5.1 three times on the same ticket. It prints each answer and request duration, then the average for each model. Nothing is saved to disk.

Clients are created before timing starts. The first request includes connection setup. Reusing a client does not guarantee a reused connection: the installed Jev SDK defaults to a five-second idle expiry, and the other models can take longer than that between Jev calls. This demo can therefore include reconnection overhead on later rounds too. There are no warm-up calls or retries. Claude is prompted to return only the category name, using its default thinking behavior. These are end-to-end request times for one small task, not model-only inference times or a general speed ranking.

The comparison and `patterns/04-intent-routing.py` require both `TYPESAFE_API_KEY` and `ANTHROPIC_API_KEY`.
