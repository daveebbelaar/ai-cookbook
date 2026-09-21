# From Text to Decisions

[Back to the tutorial](../README.md)

Many AI tasks end with a small decision. A support ticket needs a team, a priority, or a next action. With Jev, you describe the possible answers before sending the request, and the model returns a decision together with probabilities. **The answer space is part of the request.** [System One interface](https://docs.typesafe.ai/concepts/system-one).

## How this compares with an LLM

Generative LLMs can also return structured data. Claude, for example, supports schema-constrained JSON and strict tool use. The comparison is therefore about the model's intended job and interface, rather than whether its response can be parsed. [Claude structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

| Question | General-purpose generative LLM | Jev |
| --- | --- | --- |
| What can I request? | Text, code, structured fields, or tool arguments, depending on the API | Typed questions over supplied state |
| What comes back? | Generated content, potentially constrained by a schema | Choice, Score, or Noul answers |
| Can it write a reply? | Yes | No |
| How do I get uncertainty? | Requires an appropriate method and evaluation; a written confidence claim is not enough | Native probabilities; Choice and Score also expose confidence |
| Who executes a tool? | Your application | Your application |

TypeSafe presents Jev as trained specifically for these decisions. A general-purpose LLM covers a broader range of work, including writing the response after the decision has been made. [Training primer](https://docs.typesafe.ai/introduction/machine-learning-primer).

## Three building blocks

Consider a customer who writes, "I was charged twice for order A-104. Please refund the duplicate." The three primitives describe different questions about that same ticket:

| Primitive | Support question | Illustrative answer |
| --- | --- | --- |
| Choice | Which team: billing, technical, or other? | `billing`, plus a probability for each option |
| Score | How frustrated: calm, frustrated, or very angry? | `1.3` on levels numbered 0, 1, 2 |
| Noul | Does the customer explicitly request money back? | `0.95` probability of yes |

These numbers illustrate the interface; they are not recorded predictions. **A Score is a position on a rubric; a Noul is uncertainty about a yes-or-no judgment.** A Noul of 0.5 does not mean the customer wants half a refund. Choice and Score include a distribution and confidence; Noul has no separate confidence field. [Primitives](https://docs.typesafe.ai/primitives).

All three questions can share one request because each reads the same ticket independently. If a later question requires a tool's returned evidence, make that question in a subsequent request. [Question dependencies](https://docs.typesafe.ai/primitives#when-one-question-depends-on-another).

## What calibrated means

TypeSafe describes RLCD as training for decisions whose probabilities track outcomes. **Calibration is a property of many predictions.** In an illustrative set of 100 comparable predictions assigned 80% probability, a well-calibrated model would be right about 80 times. That does not tell us which 20 are wrong. [Training primer](https://docs.typesafe.ai/introduction/machine-learning-primer).

Choice and Score `confidence` is calculated from their probability distributions. **It is not automatically the probability that the selected answer is correct.** In an application, the full distribution and task-specific evaluation help determine useful routing thresholds. [Confidence reference](https://docs.typesafe.ai/confidence).

## A valid answer can still be wrong

Consider two hypothetical outputs: `billing` and `technical`. Both belong to our schema, but only one fits this duplicate-charge ticket. **Restricting the answer space prevents an invalid label, not a mistaken judgment.** TypeSafe's launch discussion ties its zero-hallucination claim to schema matching; it does not mean zero semantic errors. [Launch explanation](https://typesafe.ai/blog/introducing-system-one-models-and-jev).

For a vague ticket such as "something is wrong," I would gather more context or route it for review. Even a confident result can be based on insufficient information. This is why the surrounding application still needs a way to handle uncertain or mistaken decisions.

Continue with [designing a workflow](03-designing-a-workflow.md).
