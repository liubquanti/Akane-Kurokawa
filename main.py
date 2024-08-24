import asyncio
import random
from telethon import TelegramClient, events, functions
from config import api_id, api_hash, phone_number, char_id, charai_token
from characterai import aiocai

client = TelegramClient('session_name', api_id, api_hash)

characterai_client = aiocai.Client(charai_token)

async def get_character_ai_response(message_text):
    me = await characterai_client.get_me()

    async with await characterai_client.connect() as chat:
        new_chat, answer = await chat.new_chat(char_id, me.id)
        response = await chat.send_message(char_id, new_chat.chat_id, message_text)
        return response.text

@client.on(events.NewMessage(incoming=True))
async def handler(event):

    await asyncio.sleep(random.randint(1, 5))

    message = event.message.text

    await event.message.mark_read()

    await asyncio.sleep(len(message) * 0.03 + 1)

    response_text = await get_character_ai_response(message)

    async with client.action(event.chat_id, 'typing'):
        await asyncio.sleep(len(response_text) * 0.1 + 1)

    await event.reply(response_text)

    await asyncio.sleep(random.randint(1, 5))

    await client(functions.account.UpdateStatusRequest(offline=True))

async def main():
    await client.start(phone_number)
    print("Бот запущений!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
