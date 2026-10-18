import json
import os
import re

import ollama

# Must match exactly what `ollama list` shows on your machine.
# You can override it without editing code:
#   set NYAYAAI_MODEL=gemma3:4b      (Windows cmd)
MODEL_NAME = os.environ.get("NYAYAAI_MODEL", "gemma4:e2b")


def generate_response(prompt: str, json_mode: bool = False) -> str:
    """Send a prompt to Gemma through Ollama and return the raw text.

    With json_mode=True, Ollama constrains the output to valid JSON.
    """
    kwargs = {"format": "json"} if json_mode else {}

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
        **kwargs,
    )

    return response["message"]["content"]


def parse_json(raw: str):
    """Parse JSON from a model response.

    Strips code fences and stray text around the JSON object.
    Raises json.JSONDecodeError if nothing parseable is found.
    """
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise