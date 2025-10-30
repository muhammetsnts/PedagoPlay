from cgitb import html
import json
import os
import sys
import time
from typing import Iterable, List, Dict, Optional
import requests
import markdown


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Prefer a free model to avoid credit errors by default. You can change this.
DEFAULT_MODEL = "meta-llama/llama-3.3-8b-instruct:free"

class OpenRouterError(Exception):
    pass

def build_messages(
    num_children: int,
    ages: List[int],
    weather: str, 
    location: str, 
    special_cases: str, 
) -> List[dict]:
    
    messages: List[dict] = []
    system_prompt = """You are an expert in pedagogy, child development, and educational activity design. 

**Your role:** Generate safe, fun, and age-appropriate activities for children, considering their ages, the number of children, location, weather, and any special cases.

# Guidelines:
- Adapt to the age group(s) of the children.
- Suggest  3 **indoor** and 3 **outdoor** activities.
- Outdoor activities must be realistic and possible near the provided location, given the weather.
- Check the provided location and sugggest outdoor activities according to the natural specifics of it. 
- Respect special cases (e.g., allergy, disability, space limitation).
- Provide 3–4 activity ideas. There must be indoor and outdoor activities depending on weather and location.
- For each activity, include:
  - **Title with an icon/emoji**
  - **Description (2-3 sentences)**
  - **Why it’s good for the children** (developmental or educational value).
- Keep the tone practical, friendly, and parent-oriented.
- If the special cases are not related to children's activities, you should say "I'm sorry, I can only help with children's activities."
- If the special cases are not related to the children's ages, the weather or the location, you should say "I'm sorry, I can only help with children's activities."
- DO NOT write anything sexual, violent, or inappropriate for children.
"""
    user_prompt = f"""
Number of children: {num_children}
Ages of children: {ages}
Location: {location}
Weather: {weather}
Special case: {special_cases}

Please suggest suitable activities based on these inputs.
"""

    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    return messages

def get_inputs():
    try:
        num_children = int(input("Enter the number of children: "))
    except ValueError:
        num_children = 1
    try:
        ages_input = input("Enter the ages of the children separated by ',' (ex.: 4,5,6): ")
        ages = [int(i.strip()) for i in ages_input.split(",") if i.strip()]
    except Exception:
        ages = [4]
    weather = input("How is the weather? (sunny, rainy, snowy): ") or "sunny"
    location = input("Enter your location: ") or "Yverdon-les-Bains"
    special_cases = input("Mention any special cases if you have any: ") or "No special case."
    
    prompts = build_messages(
        num_children=num_children,
        ages=ages,
        weather=weather,
        location=location,
        special_cases=special_cases if special_cases else None
    )
    return prompts

def chat_completion(
    prompts: dict,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    request_timeout: int = 120,
    metadata_app_name: Optional[str] = None,
    retries: int = 2,
    ) -> str:
    """
    Call OpenRouter chat completions and return the full response text
    (non-stream) or print streamed chunks and return the accumulated text.
    """

    api_key = None
    try:
        with open(".env", "r") as env_file:
            for line in env_file:
                if line.strip().startswith("OPENROUTER_API_KEY="):
                    api_key = line.strip().split("=", 1)[1]
                    break
    except FileNotFoundError:
        api_key = None
        
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
        "messages": prompts,
        "temperature": temperature,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if top_p is not None:
        payload["top_p"] = top_p

    # Basic retry with exponential backoff
    last_error: Optional[Exception] = None
    for attempt in range(retries + 1):
        try:
            return send_request(headers, payload, request_timeout)
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            last_error = e
            if attempt < retries:
                sleep_s = 2 ** attempt
                time.sleep(sleep_s)
                continue
            break

    raise OpenRouterError(f"Request failed after {retries + 1} attempts: {last_error}")


def send_request(headers: dict, payload: dict, request_timeout: int) -> str:
    response = requests.post(
        OPENROUTER_API_URL, headers=headers, data=json.dumps(payload), timeout=request_timeout
    )
    _raise_for_bad_status(response)
    data = response.json()
    try:
        result = data["choices"][0]["message"]["content"]
        return _convert_html(result)
        #return data["choices"][0]["message"]["content"]

    except (KeyError, IndexError) as e:
        
        # REMOVE THIS
        print(data)
        raise OpenRouterError(f"Unexpected response format: {data}") from e

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

def _convert_html(result: str) -> html:

    try:
        file_html = markdown.markdown(result)
        file_html = file_html.replace("<li>", "")
        file_html = file_html.replace("</li>", "")
        file_html = file_html.replace("<ol>", "")
        file_html = file_html.replace("</ol>", "")
        return file_html
    except Exception as e:
        raise OpenRouterError(f"AI response convert error... {e}")