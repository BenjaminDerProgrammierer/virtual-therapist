from core import llm_request, tts_request
import urllib.request
import sys
import os

INPUT_PATH = "audio/input.mp3"
OUTPUT_PATH = "audio/output.mp3"

# Load system prompt
with open("system.md", 'r') as file:
    system_prompt = file.read()    

if len(sys.argv) < 2:
    print("Usage: python main.py <user_prompt>")
    sys.exit(1)

user_prompt = system_prompt + sys.argv[1]
print(f"PROMPT: {sys.argv[1]}")

# LLM
try:
    llm_response = llm_request(user_prompt)
    print(f"LLM RESPONSE: {llm_response}")
except Exception as e:
    print(f"LLM Request failed:\n{e}")
    sys.exit(1)

# TTS
try:
    url = tts_request(llm_response)
    print(f"TTS RESPONSE: {url}")
except Exception as e:
    print(f"TTS Request failed:\n{e}")
    sys.exit(1)

# Save output
try:
    os.unlink(OUTPUT_PATH)
except:
    pass

urllib.request.urlretrieve(url, OUTPUT_PATH)
print(f"TTS saved: {OUTPUT_PATH}")