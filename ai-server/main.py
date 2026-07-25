import asyncio
import os
import sys
import urllib.request

from core import llm_request, tts_request
from db import Database

OUTPUT_PATH = "audio/output.mp3"


async def main():
    # Load system prompt
    with open("system.md", "r") as file:
        system_prompt = file.read()
    with open("memory.md", "r") as file:
        memory_prompt = file.read()

    if len(sys.argv) < 2:
        print(
            "Usage: python main.py <user_prompt> [<phone_number>] [--is-new-conversation]"
        )
        sys.exit(1)

    phone_number = None
    is_new_conversation = False

    if len(sys.argv) >= 3:
        phone_number = sys.argv[2]
    is_new_conversation = "--is-new-conversation" in sys.argv

    async with Database() as db:
        user_id = await db.get_user_id_from_phone_number(
            phone_number if phone_number is not None else "anonymous",
            create_if_not_exists=True,
        )
        if is_new_conversation:
            current_conversation_id = await db.create_conversation(user_id=user_id)
        else:
            current_conversation_id = await db.get_latest_conversation_id(
                user_id=user_id
            )
        past_messages = await db.get_past_conversation_messages(
            conversation_id=current_conversation_id
        )
        memory = await db.get_user_memory(user_id=user_id)

    print(f"PROMPT: {sys.argv[1]}")
    messages = (
        [
            {
                "role": "system",
                "content": system_prompt.format(
                    memory=memory or "No memory available."
                ),
            }
        ]
        + past_messages
        + [{"role": "user", "content": sys.argv[1]}]
    )

    # LLM
    try:
        llm_response = llm_request(messages)
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

    # Update memory
    memory_messages = [
        {
            "role": "system",
            "content": system_prompt.format(memory=memory or "No memory available."),
        },
        {
            "role": "user",
            "content": sys.argv[1],
        },
        {
            "role": "assistant",
            "content": llm_response,
        },
    ]

    # LLM
    try:
        llm_response = llm_request(memory_messages)
        print(f"LLM RESPONSE FOR MEMORY UPDATE: {llm_response}")
    except Exception as e:
        print(f"LLM Request failed:\n{e}")
        sys.exit(1)

    async with Database() as db:
        await db.save_message(
            conversation_id=current_conversation_id, role="user", content=sys.argv[1]
        )
        await db.save_message(
            conversation_id=current_conversation_id,
            role="assistant",
            content=llm_response,
        )
        await db.update_user_memory(user_id=user_id, new_memory=llm_response)

    urllib.request.urlretrieve(url, OUTPUT_PATH)
    print(f"TTS saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
