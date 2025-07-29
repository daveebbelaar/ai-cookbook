[نسخهٔ فارسی](README.fa.md)
# Instructor: Structured LLM Outputs

[Instructor](https://github.com/jxnl/instructor) is a Python library that makes easy to work with structured outputs from large language models (LLMs). Built on top of [Pydantic](https://docs.pydantic.dev/latest/), it provides a simple, transparent, and user-friendly API to manage validation, retries, and streaming responses. The library leverages Function Calling, Tool Calling and constrained sampling modes like JSON mode to get structured output based on Pydantic schemas. You can find more examples in the [Cookbook](https://python.useinstructor.com/examples/) and explanations of all the concepts covered in the library are [listed here](https://python.useinstructor.com/concepts/types/).

## Key Features

- **Response Models**: Specify Pydantic models to define the structure of your LLM outputs
- **Retry Management**: Configure the number of retry attempts for your requests
- **Validation**: Ensure LLM responses conform to your expectations with Pydantic validation
- **Streaming Support**: Work with Lists and Partial responses
- **Flexible Backends**: Integrate with various LLM providers beyond OpenAI

## Installation

Install Instructor with a single command:

```bash
pip install -U instructor
```

Now, let's see Instructor in action with a simple example:

```python
import instructor
from pydantic import BaseModel
from openai import OpenAI


# Define your desired output structure
class UserInfo(BaseModel):
    name: str
    age: int


# Patch the OpenAI client
client = instructor.from_openai(OpenAI())

# Extract structured data from natural language
user_info = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=UserInfo,
    messages=[{"role": "user", "content": "John Doe is 30 years old."}],
)

print(user_info.name)
#> John Doe
print(user_info.age)
#> 30
```


## Using Instructor for Output Validation in LLM Applications

Instructor is a powerful tool that allows you to validate the output of language models (LLMs) in your applications. By defining a desired output structure using Pydantic models and specifying validation rules, you can ensure that the generated responses meet your requirements. If a query fails, you can instruct it to [automatically retry](https://python.useinstructor.com/concepts/retrying/).

### Validating Enum Categories

One common use case is validating the category of a response using an [enumeration (Enum)](https://python.useinstructor.com/examples/classification/#defining-the-structures). Here's an example:

```python
class TicketCategory(str, Enum):
    """Enumeration of categories for incoming tickets."""

    GENERAL = "general"
    ORDER = "order"
    BILLING = "billing"

class Reply(BaseModel):
    content: str = Field(description="Your reply that we send to the customer.")
    category: TicketCategory
    confidence: float = Field(
        ge=0, le=1, description="Confidence in the category prediction."
    )
```

In this code, we define a `TicketCategory` enum that represents the valid categories for incoming tickets. We then create a `Reply` model using Pydantic, which includes a `category` field of type `TicketCategory`.

When we make a request to the LLM using Instructor, we can specify the `response_model` parameter to validate the generated response against the `Reply` model:

```python
reply = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=Reply,
    max_retries=1,
    messages=[
        {
            "role": "system",
            "content": "You're a helpful customer care assistant that can classify incoming messages and create a response. Set the category to 'banana'.",
        },
        {"role": "user", "content": query},
    ],
)
```

If the generated response does not contain a valid category from the `TicketCategory` enum, Instructor will raise a validation error. You can specify the `max_retries` parameter to automatically retry the request and prompt the LLM to generate a valid response.

### Validating Confidence Scores

Another common validation scenario is ensuring that the generated confidence scores [fall within a specific range](https://docs.pydantic.dev/latest/concepts/fields/#numeric-constraints). Here's an example:

```python
class Reply(BaseModel):
    content: str = Field(description="Your reply that we send to the customer.")
    category: TicketCategory
    confidence: float = Field(
        ge=0, le=1, description="Confidence in the category prediction."
    )
```

In the `Reply` model, we define the `confidence` field as a float and use the `ge` (greater than or equal to) and `le` (less than or equal to) validators to restrict the confidence score to a range between 0 and 1.

When making a request to the LLM, we can specify the desired range in the system message:

```python
reply = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=Reply,
    max_retries=3,
    messages=[
        {
            "role": "system",
            "content": "You're a helpful customer care assistant that can classify incoming messages and create a response. Set confidence between 1-100.",
        },
        {"role": "user", "content": query},
    ],
)
```

If the generated confidence score does not fall within the specified range, Instructor will raise a validation error. By setting `max_retries=3`, Instructor will automatically [retry](https://python.useinstructor.com/concepts/retrying/) the request up to three times, prompting the LLM to generate a valid confidence score.


## Content Filtering

In addition to validating categories and confidence scores, Instructor also provides a powerful feature for content filtering and [Self Correction](https://python.useinstructor.com/examples/self_critique/) using the `llm_validator`. This allows you to ensure that the generated responses adhere to specific guidelines or rules, such as avoiding content that could harm the company's reputation. They also provide a way to [moderate content](https://python.useinstructor.com/examples/moderation/) using OpenAI's moderation endpoint to check content compliance with OpenAI's usage policies.

Here's an example of how to use `llm_validator` for content filtering:

```python
from pydantic import BaseModel, BeforeValidator
from typing_extensions import Annotated
from instructor import llm_validator

class ValidatedReply(BaseModel):
    content: Annotated[
        str,
        BeforeValidator(
            llm_validator(
                statement="Never say things that could hurt the reputation of the company.",
                client=client,
                allow_override=True,
            )
        ),
    ]
```

In this code, we define a `ValidatedReply` model using Pydantic. The `content` field is annotated with `Annotated` and `BeforeValidator` to associate a custom validator with it.

The `llm_validator` function is used as the validator, and it takes several parameters:
- `statement`: A string representing the validation rule that the generated response should follow. In this case, it states that the response should never contain content that could damage the company's reputation.
- `client`: The OpenAI client instance used for making API calls.
- `allow_override`: A boolean flag indicating whether the validation can be overridden if needed.

When making a request to the LLM, we can use the `ValidatedReply` model as the `response_model`:

```python
try:
    reply = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=ValidatedReply,
        max_retries=1,
        messages=[
            {
                "role": "system",
                "content": "You're a helpful customer care assistant that can classify incoming messages and create a response.",
            },
            {"role": "user", "content": query},
        ],
    )
except Exception as e:
    print(e)
```

If the generated response contains content that violates the specified validation rule, the `llm_validator` will raise a `ValidationError` with a helpful error message. This error message can be caught and used to prompt the LLM to self-correct and generate a response that adheres to the validation rule.

By incorporating content filtering using `llm_validator`, you can ensure that the generated responses meet specific content guidelines and avoid potential issues that could harm the company's reputation.

### Understanding the Syntax

To use `llm_validator` for content filtering, it's important to understand the syntax and components involved:

1. `Annotated`: It is a type hint from the `typing_extensions` module that allows attaching metadata or additional information to a type. In this code, it is used to associate the `BeforeValidator` with the `content` field of the `ValidatedReply` model.

2. `BeforeValidator`: It is a Pydantic validator that is applied before the field value is validated against the field's type and other constraints. It allows performing custom validation logic on the field value before the standard Pydantic validation takes place. In this code, it is used to wrap the `llm_validator` function.

3. `llm_validator`: It is a custom validation function provided by the `instructor` library. It takes the validation statement, OpenAI client instance, and an `allow_override` flag as parameters. It internally uses the OpenAI API to validate the generated response against the provided validation statement. If the validation fails, it raises a `ValidationError` with a helpful error message.

By combining these components, you can effectively filter the content of the generated responses and ensure they meet specific guidelines or rules.

## Conclusion

Instructor simplifies the process of validating and filtering LLM outputs by leveraging Pydantic models, validation rules, and the `llm_validator` function. By defining the desired output structure, specifying validation constraints, and incorporating content filtering, you can ensure that the generated responses meet your requirements and adhere to specific guidelines.

This powerful combination of features improves the reliability, accuracy, and appropriateness of the responses generated by your LLM-powered applications, ultimately enhancing the user experience and protecting your company's reputation.