"""
OpenRouter Qwen 3-8B Instruct client (Python, no external deps).

Usage examples:

1) Simple call
   python openrouter_qwen3_8b.py --prompt "Explain quantum computing for kids"

2) With a system prompt and parameters
   python openrouter_qwen3_8b.py \
       --system "You are a concise assistant." \
       --prompt "Summarize the benefits of exercise." \
       --temperature 0.3 --max-tokens 300

Environment:
  - Set OPENROUTER_API_KEY to your OpenRouter key

Model:
  - Default: qwen/qwen-3-8b-instruct
    Adjust with --model if needed (see https://openrouter.ai/models)
"""

import argparse
import json
import os
import sys
import time
from typing import Iterable, List, Optional

import requests


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "meta-llama/llama-3.3-8b-instruct:free"


class OpenRouterError(Exception):
    pass


def build_messages(user_prompt: str, system_prompt: Optional[str] = None) -> List[dict]:
    messages: List[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return messages


def chat_completion(
    prompt: str,
    system: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    stream: bool = False,
    request_timeout: int = 120,
    metadata_app_name: Optional[str] = None,
    retries: int = 2,
) -> str:
    """
    Call OpenRouter chat completions and return the full response text
    (non-stream) or print streamed chunks and return the accumulated text.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise OpenRouterError(
            "Missing OPENROUTER_API_KEY environment variable. Get a key from https://openrouter.ai"
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Optional routing metadata helps with analytics in OpenRouter dashboard
    if metadata_app_name:
        headers["HTTP-Referer"] = metadata_app_name
        headers["X-Title"] = metadata_app_name

    payload: dict = {
        "model": model,
        "messages": build_messages(prompt, system),
        "temperature": temperature,
        "stream": stream,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if top_p is not None:
        payload["top_p"] = top_p

    # Basic retry with exponential backoff
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            if stream:
                return _streaming_request(headers, payload, request_timeout)
            return _non_streaming_request(headers, payload, request_timeout)
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            last_error = e
            if attempt < retries:
                sleep_s = 2 ** attempt
                time.sleep(sleep_s)
                continue
            break

    raise OpenRouterError(f"Request failed after {retries + 1} attempts: {last_error}")


def _non_streaming_request(headers: dict, payload: dict, request_timeout: int) -> str:
    response = requests.post(
        OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=request_timeout
    )
    _raise_for_bad_status(response)
    data = response.json()
    # REMOVE THIS
    #print(data)
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise OpenRouterError(f"Unexpected response format: {data}") from e


def _streaming_request(headers: dict, payload: dict, request_timeout: int) -> str:
    full_text_parts: List[str] = []
    with requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=request_timeout,
        stream=True,
    ) as resp:
        _raise_for_bad_status(resp)
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("data: "):
                chunk = line[len("data: ") :].strip()
                if chunk == "[DONE]":
                    break
                try:
                    obj = json.loads(chunk)
                    delta = obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        sys.stdout.write(delta)
                        sys.stdout.flush()
                        full_text_parts.append(delta)
                except json.JSONDecodeError:
                    # Ignore malformed chunk; continue streaming
                    continue
    # Ensure newline after streaming output
    if full_text_parts:
        sys.stdout.write("\n")
        sys.stdout.flush()
    return "".join(full_text_parts)


def _raise_for_bad_status(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        # Try to include json error details if present
        try:
            details = response.json()
        except Exception:
            details = response.text
        raise OpenRouterError(f"HTTP {response.status_code}: {details}") from e


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenRouter Qwen 3-8B Instruct client")
    parser.add_argument(
        "--prompt",
        required=True,
        help="User prompt/message to send to the model",
    )
    parser.add_argument(
        "--system",
        default=None,
        help="Optional system instruction (assistant behavior)",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model name (see https://openrouter.ai/models)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature",
    )
    
    parser.add_argument(
        "--top-p",
        type=float,
        default=None,
        help="Nucleus sampling probability",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Max tokens to generate",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream tokens as they are generated",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Request timeout in seconds",
    )
    parser.add_argument(
        "--app-name",
        type=str,
        default=None,
        help="Optional app name for OpenRouter routing metadata",
    )
    
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        text = chat_completion(
            prompt=args.prompt,
            system=args.system,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            top_p=args.top_p,
            stream=args.stream,
            request_timeout=args.timeout,
            metadata_app_name=args.app_name,
        )
        if not args.stream:
            print(text)
        return 0
    except OpenRouterError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


