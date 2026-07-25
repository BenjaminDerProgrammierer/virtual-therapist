from dotenv import load_dotenv
import requests
import os

# Load environment
load_dotenv()
API_KEY = os.getenv("REPLICATE_API_TOKEN")
SPEED = 1.2

def _api_key() -> str:
    key = API_KEY or os.getenv("REPLICATE_API_TOKEN")
    if not key:
        raise RuntimeError("REPLICATE_API_TOKEN is not configured")
    return key


def _response_json(response: requests.Response) -> dict:
    response.raise_for_status()
    try:
        return response.json()
    except ValueError as error:
        raise RuntimeError("AI service returned invalid JSON") from error


# Functions
def llm_request(messages: list[dict[str, str]]) -> str:
    headers = {
        'Authorization': f'Bearer {_api_key()}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'model': '~google/gemini-flash-latest',
        'messages': messages,
    }

    response = requests.post(
        'https://ai.hackclub.com/proxy/v1/chat/completions',
        headers=headers,
        json=json_data,
        timeout=(5, 45),
    )
    data = _response_json(response)
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError("AI service response did not contain a message") from error
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("AI service returned an empty message")
    return content.strip()

def tts_request(prompt: str) -> str:
    headers = {
        'Authorization': 'Bearer ' + _api_key(),
        'Content-Type': 'application/json',
        'Prefer': 'wait',
    }

    json_data = {
        'input': {
            'text': prompt,
            'voice_id': 'English_ImposingManner',
            'language_boost': 'English',
            'english_normalization': True,
            'speed': SPEED,
        }
    }

    response = requests.post(
        'https://ai.hackclub.com/proxy/v1/replicate/models/minimax/speech-2.8-turbo/predictions',
        headers=headers,
        json=json_data,
        timeout=(5, 90),
    )
    data = _response_json(response)
    output = data.get("output")
    if not isinstance(output, str) or not output.startswith(("http://", "https://")):
        raise RuntimeError("TTS service response did not contain an audio URL")
    return output