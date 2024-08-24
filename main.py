from telethon import TelegramClient, events, functions, types
import asyncio
import random
from config import api_id, api_hash, phone_number

# Ініціалізуємо клієнта
client = TelegramClient('session_name', api_id, api_hash)

# Обробник подій для нового повідомлення
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    await asyncio.sleep(random.randint(1, 10))
    message = event.message.text.lower()

    # Позначаємо повідомлення як прочитане
    await event.message.mark_read()

    await asyncio.sleep(len(message) * 0.1 + 4)
        
        # Перевіряємо, чи є повідомлення привітанням
    if "привіт" in message or "здравствуйте" in message or "добрий день" in message:

        async with client.action(event.chat_id, 'typing'):
            
            await asyncio.sleep(random.randint(1, 5))

        await event.reply("Привіт! Як я можу допомогти?")

        await asyncio.sleep(random.randint(5, 10))

        await client(functions.account.UpdateStatusRequest(
            offline=True
        ))

    else:

        await asyncio.sleep(random.randint(1, 5))
        
        await client(functions.account.UpdateStatusRequest(
            offline=True
        ))

# Запускаємо клієнта
async def main():
    await client.start(phone_number)
    print("Бот запущений!")
    await client.run_until_disconnected()

# Запускаємо асинхронний основний метод
if __name__ == '__main__':
    asyncio.run(main())
