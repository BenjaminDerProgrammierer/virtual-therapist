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

    if len(sys.argv) < 2:
        print(
            "Usage: python main.py <user_prompt> [<phone_number>] [is_new_conversation]"
        )
        sys.exit(1)

    phone_number = None
    is_new_conversation = False

    if len(sys.argv) >= 3:
        phone_number = sys.argv[2]
    if len(sys.argv) >= 4:
        is_new_conversation = sys.argv[3].lower() == "is_new_conversation"

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

    print(f"PROMPT: {sys.argv[1]}")
    messages = (
        [{"role": "system", "content": system_prompt}]
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

    async with Database() as db:
        await db.save_message(
            conversation_id=current_conversation_id, role="user", content=sys.argv[1]
        )
        await db.save_message(
            conversation_id=current_conversation_id,
            role="assistant",
            content=llm_response,
        )

    urllib.request.urlretrieve(url, OUTPUT_PATH)
    print(f"TTS saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
