from openrouter import OpenRouter
from dotenv import load_dotenv
import requests
import json
import os

# Load environment
load_dotenv()
API_KEY = os.getenv("REPLICATE_API_TOKEN")

client = OpenRouter(
    api_key=API_KEY,
    server_url="https://ai.hackclub.com/proxy/v1",
)

# Functions
def llm_request(user_prompt: str) -> str:
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'model': '~google/gemini-flash-latest',
        'messages': [
            {
                'role': 'user',
                'content': user_prompt,
            },
        ],
    }

    response = requests.post('https://ai.hackclub.com/proxy/v1/chat/completions', headers=headers, json=json_data)
    return json.loads(response.text)["choices"][0]["message"]["content"]

def tts_request(prompt: str) -> str:
    headers = {
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Type': 'application/json',
        'Prefer': 'wait',
    }

    json_data = {
        'input': {
            'text': prompt,
            'voice_id': 'English_ImposingManner',
            'language_boost': 'English',
            'english_normalization': True,
        }
    }

    response = requests.post(
        'https://ai.hackclub.com/proxy/v1/replicate/models/minimax/speech-2.8-turbo/predictions',
        headers=headers,
        json=json_data
    )

    return json.loads(response.text)["output"]