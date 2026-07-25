from core import llm_request, tts_request
import urllib.request
import sys

# Load system prompt
with open("system.md", 'r') as file:
    system_prompt = file.read()    

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
    os.unlink("output.mp3")
except:
    pass

urllib.request.urlretrieve(url, "output.mp3")
print("TTS saved: output.mp3")