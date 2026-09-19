from mem0 import Memory
from dotenv import load_dotenv

load_dotenv(".env")
m = Memory()  # Requires OpenAI API key

# --------------------------------------------------------------
# Message sequence
# --------------------------------------------------------------

messages = [
    {
        "role": "user",
        "content": "I'm planning to watch a movie tonight. Any recommendations?",
    },
    {
        "role": "assistant",
        "content": "How about a thriller movies? They can be quite engaging.",
    },
    {
        "role": "user",
        "content": "I'm not a big fan of thriller movies but I love sci-fi movies.",
    },
    {
        "role": "assistant",
        "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future.",
    },
]

# --------------------------------------------------------------
# Store inferred memories (default behavior)
# --------------------------------------------------------------

result = m.add(
    messages, user_id="default_user", metadata={"category": "movie_recommendations"}
)

# --------------------------------------------------------------
# Get all memories
# --------------------------------------------------------------

all_memories = m.get_all(filters={"user_id": "default_user"})

# --------------------------------------------------------------
# Search for related memories
# --------------------------------------------------------------

related_memories = m.search(
    query="What do you know about me?",
    filters={"user_id": "default_user"},
)

print(related_memories)
