"""
Utility functions for the ReWriteMe backend.

This module wraps calls to the OpenAI API for text rewriting and
emotion analysis.  It provides asynchronous helpers that return
structured results.  To keep the example self‑contained, if the
OpenAI API key is not present or a request fails, simple fallback
implementations are used instead.
"""

import os
import asyncio
import logging
from typing import List

try:
    import openai  # type: ignore
except ImportError:
    openai = None  # Allows the rest of the code to import


logger = logging.getLogger(__name__)

# Configure OpenAI API key from environment if available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


async def generate_rewrites(text: str) -> List[str]:
    """
    Generate three rewrite suggestions for the given text using the
    OpenAI ChatCompletion API.  If the API is unavailable, produce
    simple deterministic variants as a fallback.
    """
    # Only attempt API if openai module and key are configured
    if openai and OPENAI_API_KEY:
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that rewrites the user's text while preserving the original meaning."},
                {"role": "user", "content": f"Rewrite the following text in three different ways:\n{text}"},
            ]
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=256,
                n=1,
                temperature=0.7,
            )
            # Extract three rewrites separated by newlines
            content = response.choices[0].message["content"]
            # The model returns rewrites separated by newlines or enumerated.  Split accordingly.
            lines = [line.strip(" -\t\n") for line in content.split("\n") if line.strip()]
            # Return the first three non‑empty lines as rewrites
            rewrites = lines[:3] if len(lines) >= 3 else lines + [text] * (3 - len(lines))
            return rewrites
        except Exception as exc:
            logger.warning("OpenAI API call failed: %s", exc)

    # Fallback: trivial transformations (append markers)
    return [f"{text} (rewrite {i})" for i in range(1, 4)]


async def emotion_analysis(rewrites: List[str]) -> List[str]:
    """
    Perform a simple sentiment classification on each rewrite.
    If the OpenAI API is available, ask the API to classify each
    sentence as one of joy, sad, neutral or anger.  Otherwise return
    'neutral' for all.
    """
    sentiments: List[str] = []
    if openai and OPENAI_API_KEY:
        try:
            # Build a prompt that lists all rewrites and asks for classification
            prompt = "Classify the emotional tone of each sentence in the following list as one of joy, sad, neutral or anger. Return a comma separated list of the labels in the same order.\n\n" + "\n".join(rewrites)
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=64,
                n=1,
                temperature=0.0,
            )
            content = response.choices[0].message["content"]
            # Split by comma and strip whitespace
            sentiments = [lab.strip().lower() for lab in content.split(",")]
            # If fewer labels than rewrites, pad with 'neutral'
            if len(sentiments) < len(rewrites):
                sentiments.extend(["neutral"] * (len(rewrites) - len(sentiments)))
            return sentiments[: len(rewrites)]
        except Exception as exc:
            logger.warning("OpenAI sentiment analysis failed: %s", exc)
    # Fallback: neutral for all
    return ["neutral" for _ in rewrites]


async def analyse_single_emotion(text: str) -> str:
    """
    Analyse the emotional tone of a single text input.  Uses the same
    classification categories as `emotion_analysis`.
    """
    result = await emotion_analysis([text])
    return result[0] if result else "neutral"