# Jev, TypeSafe AI, and System One Models

[Back to the tutorial](../README.md)

Jev is a model from TypeSafe AI for making structured decisions inside software. Given some context and a set of questions, it can choose a category, rate a property, or estimate the probability of a yes-or-no answer. **Its output is a decision that your code can use directly.** Writing a customer reply or generating code still calls for a generative model. [System One overview](https://docs.typesafe.ai/concepts/system-one).

For a support application, that might mean deciding whether a ticket belongs to billing, whether the customer wants a refund, and which lookup to run. These are small judgments, but they often sit between several steps in a larger workflow.

## The company behind Jev

TypeSafe AI announced Jev in early access on September 15, 2026. Its team page lists founders Diogo Almeida (CEO), Sasha Sheng (COO), and Erik Gafni (CTO), with an office in San Francisco. Almeida previously worked at OpenAI on the research behind InstructGPT, while Sheng's background includes Meta/FAIR. [Company team](https://typesafe.ai/team), [launch announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev).

The company calls this category **System One models**, borrowing Daniel Kahneman's description of fast, intuitive judgment. The name describes the role TypeSafe wants these models to play in software. It does not establish that they reproduce human cognition.

## What is known about the model

TypeSafe describes its training approach as Reinforcement Learning for Calibrated Decisions, or RLCD. Its AI primer presents RLCD as a post-training approach starting from pretrained language models. The launch announcement also describes a new architecture and parallel sampler. [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer), [launch announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev).

The public sources reviewed for this article do not identify Jev's base checkpoint or parameter count. They also leave its exact pretraining history unclear. There is therefore no established basis in those sources for calling it a Llama, Qwen, or GPT derivative, or for saying it was trained entirely from scratch.

**The clearest distinction for developers is its training objective and output interface.** Jev is presented as a model trained for typed, probabilistic decisions. The published information gives us enough to understand how to use it, but not enough to reconstruct its internals.

## How you use it

Jev 1.13.0 is accessed through a hosted API with text-based state. According to the model reference, the same weights serve all accounts, and customer-specific fine-tuning or LoRA adaptation is not offered in that setup. Application-specific knowledge goes into the request. [Model reference](https://docs.typesafe.ai/models).

I find it useful to think about Jev in terms of the decisions an application needs. A billing ticket already contains language that needs interpreting. The application can ask Jev to interpret it, then use Python to retrieve records, calculate amounts, and apply exact rules. That division of work is the basis of the examples in this tutorial.

Continue with [from text to decisions](02-from-text-to-decisions.md).

*Sources reviewed September 20, 2026. Product details refer to Jev 1.13.0.*
