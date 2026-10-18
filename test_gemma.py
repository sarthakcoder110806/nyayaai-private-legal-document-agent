from core.llm import generate_response


prompt = """
Explain in simple language:

The tenant must pay monthly rent of INR 12,000
on or before the 5th day of each month.

Use only the supplied statement.
"""


response = generate_response(
    prompt
)

print(response)