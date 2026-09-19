from openai import OpenAI
from mem0 import Memory
from dotenv import load_dotenv

load_dotenv("../.env")


class CustomerSupportAIAgent:
    def __init__(self):
        """
        Initialize the CustomerSupportAIAgent with memory configuration and OpenAI client.
        """
        # ! Make sure qdrant is running (see docker-compose.yml)
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": "localhost",
                    "port": 6333,
                },
            },
        }
        self.memory = Memory.from_config(config)
        self.client = OpenAI()
        self.app_id = "customer-support"

    def handle_query(self, query, user_id=None):
        """
        Handle a customer query and store the relevant information in memory.

        :param query: The customer query to handle.
        :param user_id: Optional user ID to associate with the memory.
        """
        # Start a streaming chat completion request to the AI
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a customer support AI agent."},
                {"role": "user", "content": query},
            ],
        )
        # Store the query in memory
        self.memory.add(query, user_id=user_id, metadata={"app_id": self.app_id})
        print(response.choices[0].message.content)

    def get_memories(self, user_id=None):
        """
        Retrieve all memories associated with the given customer ID.

        :param user_id: Optional user ID to filter memories.
        :return: List of memories.
        """
        return self.memory.get_all(filters={"user_id": user_id})


# Instantiate the CustomerSupportAIAgent
support_agent = CustomerSupportAIAgent()

# Define a customer ID
customer_id = "default_user"

# Handle a customer query
support_agent.handle_query(
    "I need help with my recent order. It hasn't arrived yet.", user_id=customer_id
)
