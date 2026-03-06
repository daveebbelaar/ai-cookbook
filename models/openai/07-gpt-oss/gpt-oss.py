from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
import nest_asyncio

nest_asyncio.apply()


class CityLocation(BaseModel):
    city: str
    country: str


ollama_model = OpenAIChatModel(
    model_name="gpt-oss:20b",
    provider=OpenAIProvider(base_url="http://localhost:11434/v1"),
)

agent = Agent(
    ollama_model,
    output_type=CityLocation,
)

result = agent.run_sync("Where were the olympics held in 2012?")
print(result.output)
