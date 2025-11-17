[نسخهٔ فارسی](README.fa.md)
# Structured Output in LLM Applications

When working with the OpenAI API directly, you have two main options for obtaining structured output responses from GPT models: JSON mode and Function calling. While both are powerful tools, they also have their limitations. Understanding when to use each can enhance your workflow and give you more control over the output. After learning about these two methods, we'll dive into [Instructor](https://github.com/daveebbelaar/python-openai-tutorial/tree/main/04%20Structured%20Output/Instructor) to gain even greater control over the output from OpenAI's models. Instructor was covered in this great ["Pydantic is all you need"](https://www.youtube.com/watch?v=yj-wSRJwrrc) talk by Jason Liu.

## Why Use JSON Output?

Using JSON output in your LLM applications provides more control and validation over the generated responses. It ensures that the output is always a valid JSON string, making it easier to parse and process the data in your application.

## JSON Mode

In [JSON mode](https://platform.openai.com/docs/guides/text-generation/json-mode), the model generates outputs exclusively formatted as valid JSON strings. However, you need to explicitly specify the desired JSON structure within the system prompt to guide the model towards the expected format.

Here's an example of using JSON mode:

```python
query = "Hi there, I have a question about my bill. Can you help me?"

messages = [
    {
        "role": "system",
        "content": """
        You're a helpful customer care assistant that can classify incoming messages and create a response.
        Always response in the following JSON format: {"content": <response>, "category": <classification>}
        Available categories: 'general', 'order', 'billing'
        """,
    },
    {
        "role": "user",
        "content": query,
    },
]

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    response_format={"type": "json_object"},
)
message = response.choices[0].message.content

type(message)  # str

message_json = json.loads(message)
type(message_json)  # dict
```

It's important to note that OpenAI does not guarantee that the output text will have your specified JSON format. It only ensures that the output will be a valid string that can be parsed to JSON.

### API Reference

- `response_format`: An object specifying the format that the model must output. Compatible with GPT-4 Turbo and all GPT-3.5 Turbo models newer than gpt-3.5-turbo-1106. Setting to `{"type": "json_object"}` enables JSON mode, which guarantees the message the model generates is valid JSON.

Important: When using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if `finish_reason="length"`, which indicates the generation exceeded `max_tokens` or the conversation exceeded the max context length.

## Function Calling

[Function Calling](https://platform.openai.com/docs/guides/function-calling) allows you to provide a list of functions that the model can call. You can specify the function name, description, and parameters, including their types and required fields. You can find more examples in this [Cookbook](https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models).

Here's an example of using function calling:

```python
query = "Hi there, I have a question about my bill. Can you help me?"

function_name = "chat"

tools = [
    {
        "type": "function",
        "function": {
            "name": function_name,
            "description": f"Function to respond to a customer query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Your reply that we send to the customer.",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["general", "order", "billing"],
                        "description": "Category of the ticket.",
                    },
                },
                "required": ["content", "category"],
            },
        },
    }
]

messages = [
    {
        "role": "system",
        "content": "You're a helpful customer care assistant that can classify incoming messages and create a response.",
    },
    {
        "role": "user",
        "content": query,
    },
]

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": function_name}},
)

tool_call = response.choices[0].message.tool_calls[0]
type(tool_call)  # ChatCompletionMessageToolCall

function_args = json.loads(tool_call.function.arguments)
type(function_args)  # dict
```

### API Reference

- `tools`: A list of tools the model may call. Currently, only functions are supported as a tool. Use this to provide a list of functions the model may generate JSON inputs for. A max of 128 functions are supported.

- `tool_choice`: Controls which (if any) tool is called by the model. `none` means the model will not call any tool and instead generates a message. `auto` means the model can pick between generating a message or calling one or more tools. `required` means the model must call one or more tools. Specifying a particular tool via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool. `none` is the default when no tools are present. `auto` is the default if tools are present.

## When to Use Each Approach

1. **Function Calling**: If your use case can be framed to use function calling, it is recommended to use it. OpenAI will automatically optimize your prompt according to the specified functions, and the language models were trained with this prompt format. This increases the likelihood of better responses and reduces the frequency of hallucinations. Additionally, the response comes parsed in `ChatCompletionMessageToolCall` objects, which is convenient.

2. **JSON Mode**: JSON mode is a more flexible capability that forces the LLM to always output a valid JSON string, but the JSON structure is arbitrary. It's useful when you need JSON output but don't want to specify the exact structure.

Keep in mind that the LLM can still hallucinate in both approaches. In function calling, the LLM may ignore your instructions and output free-form text instead of using functions, or it may hallucinate argument names and values. In JSON mode, the LLM always produces JSON, but the specified format may not be respected.

## Conclusion

Both JSON mode and function calling are valuable tools for obtaining structured output from LLM applications. Function calling provides more control and is recommended when possible, while JSON mode offers flexibility when the exact structure is not critical. However, if you want even more control over your outputs, [Instructor](https://github.com/daveebbelaar/python-openai-tutorial/tree/main/04%20Structured%20Output/Instructor) is the way to go.