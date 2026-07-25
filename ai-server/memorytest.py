import asyncio
import os
import sys
import urllib.request

from core import llm_request, tts_request
from db import Database

async def main():
    # Get transcript
    transcript = "User: why am i shorter than all my friends\nDr. Snickers: Someone had to be the group armrest, and you're lowkey built for the job." # TODO get the actual transcript

    with open("memory.md", "r") as file:
        memory_prompt = file.read()

    # Update memory
    memory_messages = [
        {
            "role": "system",
            "content": memory_prompt.format(
                memory="No memory yet. Either add your first entries now or output this exact line not to add anything.",
                transcript=transcript
            ),
        }
    ]

    # LLM
    try:
        llm_response = llm_request(memory_messages)
        print(f"MEMORY UPDATE: {llm_response}")
    except Exception as e:
        print(f"LLM Request failed:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
