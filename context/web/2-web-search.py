from typing import List

from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

MODEL = "gpt-5-nano"  # use a reasoning model for better performance

# --------------------------------------------------------------
# Define the output model
# --------------------------------------------------------------


class Citation(BaseModel):
    text: str
    url: str


class SearchResult(BaseModel):
    answer: str
    citations: List[Citation]


# --------------------------------------------------------------
# Configure domain restrictions
# --------------------------------------------------------------

domains = [
    "rijksoverheid.nl",
    "tweedekamer.nl",
    "cbs.nl",
]

# --------------------------------------------------------------
# Perform web search with domain filtering
# --------------------------------------------------------------

query = "What are the current policies and regulations regarding AI implementation in Dutch government services, and what are the key requirements for public sector AI adoption?"

response = client.responses.parse(
    model=MODEL,
    reasoning={"effort": "medium"},
    tools=[
        {
            "type": "web_search",
            "filters": {
                "allowed_domains": domains,
            },
        }
    ],
    tool_choice="auto",
    include=["web_search_call.action.sources"],
    input=query,
    instructions="You are a policy research assistant for Dutch governmental agencies. You search official government websites to find relevant policy documents, regulations, and official information. For each piece of information in your answer, provide a citation that includes the specific text excerpt and the URL where it came from. Make sure to answer in English.",
    text_format=SearchResult,
)

result = response.output[-1].content[-1].parsed
print(result.model_dump_json(indent=2))

print(result.answer)
