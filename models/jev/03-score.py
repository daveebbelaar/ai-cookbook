"""Score places an input on an ordered rubric and can return a value between rubric levels.
This example rates customer frustration using descriptions that define what each level means.

More info: https://docs.typesafe.ai/primitives/score
"""

from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()
model = "jev-1.13.0"
client = TypeSafeClient(model=model)

# --------------------------------------------------------------
# Step 1: Define the ticket and ordered levels
# --------------------------------------------------------------

ticket = "I was charged twice. This is frustrating. Can you please fix it."
question = Score(
    instructions="How frustrated is the customer in this support ticket?",
    criteria=[
        "Calm or neutral.",
        "Frustrated but civil.",
        "Very angry or abusive.",
    ],
)

# --------------------------------------------------------------
# Step 2: Read the score and its probability distribution
# --------------------------------------------------------------


response = client.system_one(state=ticket, questions={"frustration": question})

answer = response.scores["frustration"]
# Levels are numbered from zero; the score can fall between levels.
print("Score:", answer.score)
print("Legend:", answer.legend)
print("Probabilities:", answer.probabilities)
print("Confidence:", answer.confidence)
