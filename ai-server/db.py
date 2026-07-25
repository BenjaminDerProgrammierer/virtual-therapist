import asyncio
from typing import Any, cast

from prisma import Prisma


class Database:
    def __init__(self):
        self.db = Prisma()
        self._schema_initialized = False

    async def connect(self):
        await self.db.connect()
        await self.ensure_tables()

    async def disconnect(self):
        await self.db.disconnect()

    async def ensure_tables(self):
        if self._schema_initialized:
            return

        await self.db.execute_raw("""
            CREATE TABLE IF NOT EXISTS "Users" (
                id SERIAL PRIMARY KEY,
                "phoneNumber" TEXT NOT NULL UNIQUE
            )
            """)
        await self.db.execute_raw("""
            CREATE TABLE IF NOT EXISTS "Conversations" (
                id SERIAL PRIMARY KEY,
                "userId" INTEGER NOT NULL,
                "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """)
        await self.db.execute_raw("""
            CREATE TABLE IF NOT EXISTS "Messages" (
                id SERIAL PRIMARY KEY,
                "conversationId" INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """)

        self._schema_initialized = True

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    async def get_past_conversation_messages(self, conversation_id: int) -> str:
        conversation_messages = await self.db.messages.find_many(
            where={"conversationId": conversation_id}, order={"createdAt": "asc"}
        )
        return "\n".join([msg.content for msg in conversation_messages])

    async def save_message(self, conversation_id: int, role: str, content: str) -> None:
        await self.db.messages.create(
            data={
                "conversationId": conversation_id,
                "role": role,
                "content": content,
            }
        )

    async def create_conversation(self, user_id: int) -> int:
        conversation = await self.db.conversations.create(data={"userId": user_id})
        return conversation.id

    async def get_latest_conversation_id(self, user_id: int) -> int:
        conversation = await self.db.conversations.find_first(
            where={"userId": user_id},
            order=cast(Any, {"createdAt": "desc"}),
        )
        if conversation:
            return conversation.id
        else:
            return await self.create_conversation(user_id)

    async def get_user_id_from_phone_number(
        self, phone_number: str, create_if_not_exists: bool = True
    ) -> int:
        user = await self.db.users.find_first(where={"phoneNumber": phone_number})
        if user:
            return user.id
        if create_if_not_exists:
            new_user = await self.db.users.create(data={"phoneNumber": phone_number})
            return new_user.id
        raise ValueError(f"User with phone number {phone_number} not found.")


async def test():
    async with Database() as db:
        user_id = await db.get_user_id_from_phone_number("+1234567890")
        print(f"User ID: {user_id}")


if __name__ == "__main__":
    asyncio.run(test())
