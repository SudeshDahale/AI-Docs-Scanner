from typing import Literal
from openai import OpenAI
from core.config import config

QueryType = Literal["summary", "factual", "comparison"]


def classify_query(query: str, client: OpenAI = None) -> QueryType:
    """
    Classify the user query into one of three types:
      - summary    : broad overview, "what is this document about"
      - factual    : specific fact lookup, "what is the value of X"
      - comparison : comparing two or more things

    Uses a cheap single-token LLM call. Falls back to 'factual' on error.
    """
    client = client or OpenAI(api_key=config.OPENAI_API_KEY)

    prompt = (
        "Classify this question into exactly one word: summary, factual, or comparison.\n"
        "Rules:\n"
        "  summary    = asks for overview, summary, or general description\n"
        "  factual    = asks for a specific fact, value, date, or definition\n"
        "  comparison = asks to compare, contrast, or differentiate things\n\n"
        f"Question: {query}\n"
        "Answer (one word only):"
    )

    try:
        response = client.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0,
        )
        label = response.choices[0].message.content.strip().lower()
        if label in ("summary", "factual", "comparison"):
            return label  # type: ignore
        return "factual"
    except Exception:
        return "factual"