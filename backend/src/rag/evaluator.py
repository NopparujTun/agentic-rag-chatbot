"""Evaluation module for RAG answer quality assessment.

Provides two evaluation strategies:
- Faithfulness: checks if an answer is grounded in the provided context documents.
- Accuracy: checks if an answer matches expected ground truth (for baseline comparisons).

Both evaluators use the Typhoon API as an LLM judge with structured JSON output.
"""

import json
import logging
import os
import re
import time
from typing import List

import requests
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TYPHOON_API_URL = "https://api.opentyphoon.ai/v1/chat/completions"
TYPHOON_MODEL = "typhoon-v2.5-30b-a3b-instruct"
TYPHOON_TEMPERATURE = 0.0
TYPHOON_MAX_TOKENS = 4000
TYPHOON_TIMEOUT_SECONDS = 90

MAX_PROMPT_LENGTH = 6000
MAX_ANSWER_LENGTH = 500
MAX_CONTEXT_LENGTH = 3000

MAX_RETRIES = 3
RATE_LIMIT_WAIT_SECONDS = 20


# ---------------------------------------------------------------------------
# Typhoon API client
# ---------------------------------------------------------------------------

def _call_typhoon_api(prompt_text: str) -> str:
    """Send a prompt to the Typhoon chat completions API and return the response text.

    Handles prompt truncation, rate-limit retries, and HTTP error codes.

    Args:
        prompt_text: The full prompt string to send.

    Returns:
        The assistant's response content, or an `ERROR_*` prefixed string on failure.
    """
    api_key = os.environ.get("TYPHOON_API_KEY")
    if not api_key:
        return "ERROR_CONFIG: TYPHOON_API_KEY environment variable is not set"

    if len(prompt_text) > MAX_PROMPT_LENGTH:
        half_length = MAX_PROMPT_LENGTH // 2
        prompt_text = prompt_text[:half_length] + "\n...[truncated]...\n" + prompt_text[-half_length:]

    request_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    request_payload = {
        "model": TYPHOON_MODEL,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": TYPHOON_TEMPERATURE,
        "max_tokens": TYPHOON_MAX_TOKENS,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            api_response = requests.post(
                TYPHOON_API_URL,
                headers=request_headers,
                json=request_payload,
                timeout=TYPHOON_TIMEOUT_SECONDS,
            )

            if api_response.status_code == 200:
                return api_response.json()["choices"][0]["message"]["content"]

            if api_response.status_code == 429:
                logger.warning(
                    "Rate-limited by Typhoon API (attempt %d/%d). Waiting %ds...",
                    attempt, MAX_RETRIES, RATE_LIMIT_WAIT_SECONDS,
                )
                time.sleep(RATE_LIMIT_WAIT_SECONDS)
                continue

            return f"ERROR_API: {api_response.status_code} - {api_response.text}"

        except requests.RequestException as exception:
            logger.error("Typhoon API request failed: %s", exception)
            return f"ERROR_REQ: {exception}"

    return "ERROR: Max retries exceeded"


# ---------------------------------------------------------------------------
# Verdict parsing
# ---------------------------------------------------------------------------

def _parse_verdict(raw_content: str) -> str:
    """Extract a PASS / FAIL verdict from an LLM response.

    Attempts JSON parsing first, then falls back to keyword matching.

    Args:
        raw_content: Raw LLM response text.

    Returns:
        `PASS`, `FAIL`, or the original `ERROR_*` string.
    """
    print(f"\n[DEBUG LLM]: {raw_content}\n")
    if raw_content.startswith("ERROR"):
        return raw_content

    cleaned_json_string = re.sub(r"```json|```", "", raw_content).strip()

    try:
        parsed_json = json.loads(cleaned_json_string)
        return parsed_json.get("verdict", "FAIL").upper()
    except (json.JSONDecodeError, AttributeError):
        pass

    if "PASS" in raw_content.upper():
        return "PASS"
    return "FAIL"


# ---------------------------------------------------------------------------
# Public evaluation functions
# ---------------------------------------------------------------------------

def evaluate_accuracy(question: str, ground_truth: str, generated_answer: str) -> str:
    """Judge whether the answer is factually consistent with the ground truth.

    Intended for baseline evaluation where there is no retrieval context.
    We simply compare the model's answer against a known-correct answer.

    Args:
        question: The original question.
        ground_truth: The expected correct answer.
        generated_answer: The model-generated answer to evaluate.

    Returns:
        `PASS` if the answer is substantively correct, `FAIL` otherwise.
    """
    truncated_answer = generated_answer[:MAX_ANSWER_LENGTH]

    evaluation_prompt = (
        "คุณคือระบบตรวจคำตอบระดับผู้เชี่ยวชาญ\n"
        "ตัดสินว่า 'คำตอบจากระบบ' มีเนื้อหาถูกต้องตาม 'เฉลย' หรือไม่ "
        "(เน้นสาระสำคัญ ไม่ต้องตรงทุกคำ)\n\n"
        f"โจทย์: {question}\n"
        f"เฉลย: {ground_truth}\n"
        f"คำตอบ: {truncated_answer}\n\n"
        'ตอบเป็น JSON เท่านั้น: {"verdict": "PASS"} หรือ {"verdict": "FAIL"}'
    )
    return _parse_verdict(_call_typhoon_api(evaluation_prompt))


def evaluate_faithfulness(
    context_documents: List[Document],
    generated_answer: str,
) -> str:
    """Judge whether the generated answer is fully grounded in the context documents.

    Used during RAG evaluation to detect hallucination.

    Args:
        context_documents: List of LangChain Document objects used as context.
        generated_answer: The RAG-generated answer to evaluate.

    Returns:
        `PASS` if faithful, `FAIL` if hallucination detected.
    """
    if not context_documents:
        return "FAIL"

    context_text = "\n\n".join(
        doc.page_content for doc in context_documents
    )[:MAX_CONTEXT_LENGTH]

    truncated_answer = generated_answer[:MAX_ANSWER_LENGTH]

    evaluation_prompt = (
        "คุณคือระบบตรวจสอบความถูกต้อง "
        "ตรวจสอบว่า 'คำตอบ' สอดคล้องและมาจาก 'ข้อมูลอ้างอิง' หรือไม่\n"
        "**เงื่อนไขสำคัญ**: หาก 'คำตอบ' ระบุความหมายในทำนองว่า 'ขออภัย ไม่พบข้อมูล', "
        "'ไม่มีข้อมูลในเอกสาร', หรือปฏิเสธการตอบเนื่องจากข้อมูลไม่พอ ให้คุณตัดสินว่าสอดคล้องและตอบ PASS ทันที\n\n"
        f"อ้างอิง: {context_text}\n"
        f"คำตอบ: {truncated_answer}\n\n"
        'ตอบเป็น JSON เท่านั้น: {"verdict": "PASS"} หรือ {"verdict": "FAIL"}'
    )
    return _parse_verdict(_call_typhoon_api(evaluation_prompt))