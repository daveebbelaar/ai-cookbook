from mem0 import MemoryClient
from dotenv import load_dotenv
import os

load_dotenv(".env")

# --------------------------------------------------------------
# Initialize Mem0 client (Cloud)
# --------------------------------------------------------------

client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))

# --------------------------------------------------------------
# Message sequence
# --------------------------------------------------------------

messages = [
    {
        "role": "user",
        "content": "Hi, I'm Aamir. I like to build AI automations!.",
    },
    {
        "role": "assistant",
        "content": "Hello Aamir! I've noted that you like to build AI automations!. I'll keep this in mind for any AI automation related recommendations or discussions.",
    },
]

client.add(messages, user_id="default_user")

# --------------------------------------------------------------
# Search for related memories
# --------------------------------------------------------------

query = "What shall we build today?"

# --------------------------------------------------------------
# Search for related memories
# --------------------------------------------------------------

response = client.search(query, filters={"user_id": "default_user"})
