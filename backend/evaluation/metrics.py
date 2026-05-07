"""
LLM-as-Judge evaluation metrics.
Uses GPT to score each metric — domain agnostic, semantically accurate.
Cost: ~$0.003 per full eval run (7 questions).
"""

from __future__ import annotations
import json
import re
from typing import List, Dict
from openai import OpenAI
from core.config import config


def _get_client() -> OpenAI:
    return OpenAI(api_key=config.OPENAI_API_KEY)


def _ask_judge(prompt: str, client: OpenAI) -> float:
    """Send a scoring prompt to the LLM, return a 0.0–1.0 float."""
    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict evaluation judge. "
                    "You ONLY respond with a JSON object like: {\"score\": 0.8} "
                    "Score is always between 0.0 and 1.0. No explanation, no extra text."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    try:
        return float(json.loads(raw)["score"])
    except Exception:
        # fallback: extract first float found in response
        match = re.search(r"0?\.\d+|[01]\.0*", raw)
        return float(match.group()) if match else 0.0


# ── 1. Context Precision ───────────────────────────────────────────────────

def context_precision(
    question: str,
    retrieved_chunks: List[Dict],
    client: OpenAI = None,
) -> float:
    """
    Are the retrieved chunks actually relevant to the question?
    Scores each chunk and averages.
    """
    client = client or _get_client()
    if not retrieved_chunks:
        return 0.0

    scores = []
    for chunk in retrieved_chunks:
        prompt = f"""Question: {question}

Retrieved chunk:
\"\"\"{chunk.get('text', '')[:400]}\"\"\"

Is this chunk relevant to answering the question?
Score 1.0 = highly relevant, 0.5 = somewhat relevant, 0.0 = not relevant."""
        scores.append(_ask_judge(prompt, client))

    return round(sum(scores) / len(scores), 4)


# ── 2. Context Recall ──────────────────────────────────────────────────────

def context_recall(
    question: str,
    retrieved_chunks: List[Dict],
    ground_truth_answer: str,
    client: OpenAI = None,
) -> float:
    """
    Does the retrieved context contain enough information
    to produce the ground truth answer?
    """
    client = client or _get_client()
    context = "\n\n".join(
        c.get("text", "")[:300] for c in retrieved_chunks
    )
    prompt = f"""Question: {question}

Retrieved context:
\"\"\"{context}\"\"\"

Expected answer:
\"\"\"{ground_truth_answer}\"\"\"

Does the retrieved context contain enough information to produce the expected answer?
Score 1.0 = all information present, 0.5 = partial, 0.0 = missing key information."""

    return round(_ask_judge(prompt, client), 4)


# ── 3. Answer Correctness ─────────────────────────────────────────────────

def answer_correctness(
    question: str,
    generated_answer: str,
    ground_truth_answer: str,
    client: OpenAI = None,
) -> float:
    """
    Is the generated answer correct compared to the ground truth?
    """
    client = client or _get_client()
    prompt = f"""Question: {question}

Generated answer:
\"\"\"{generated_answer[:400]}\"\"\"

Expected answer:
\"\"\"{ground_truth_answer[:400]}\"\"\"

How correct and complete is the generated answer compared to the expected answer?
Score 1.0 = fully correct, 0.5 = partially correct, 0.0 = wrong or missing."""

    return round(_ask_judge(prompt, client), 4)


# ── 4. Faithfulness ───────────────────────────────────────────────────────

def faithfulness(
    generated_answer: str,
    retrieved_chunks: List[Dict],
    client: OpenAI = None,
) -> float:
    """
    Is the generated answer grounded in the retrieved context,
    or is the model hallucinating?
    """
    client = client or _get_client()
    context = "\n\n".join(
        c.get("text", "")[:300] for c in retrieved_chunks
    )
    prompt = f"""Retrieved context:
\"\"\"{context}\"\"\"

Generated answer:
\"\"\"{generated_answer[:400]}\"\"\"

Is the generated answer fully supported by the retrieved context?
Score 1.0 = fully grounded, 0.5 = partially grounded, 0.0 = hallucinated."""

    return round(_ask_judge(prompt, client), 4)


# ── Aggregate scorer ──────────────────────────────────────────────────────

def score_sample(
    question: str,
    generated_answer: str,
    retrieved_chunks: List[Dict],
    ground_truth_answer: str,
    ground_truth_contexts: List[str],   # kept for interface compatibility
    client: OpenAI = None,
    dry_run: bool = False,
) -> Dict:
    """
    Score one Q&A sample using LLM-as-judge.
    Pass dry_run=True to skip LLM calls and return retrieval-only scores.
    """
    client = client or _get_client()

    if dry_run:
        # Free mode: only score faithfulness (no generation needed)
        return {
            "question":           question,
            "context_precision":  context_precision(question, retrieved_chunks, client),
            "context_recall":     context_recall(question, retrieved_chunks, ground_truth_answer, client),
            "answer_correctness": None,   # skipped in dry-run
            "faithfulness":       faithfulness(generated_answer, retrieved_chunks, client),
        }

    return {
        "question":           question,
        "context_precision":  context_precision(question, retrieved_chunks, client),
        "context_recall":     context_recall(question, retrieved_chunks, ground_truth_answer, client),
        "answer_correctness": answer_correctness(question, generated_answer, ground_truth_answer, client),
        "faithfulness":       faithfulness(generated_answer, retrieved_chunks, client),
    }