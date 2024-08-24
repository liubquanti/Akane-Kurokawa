from telethon import TelegramClient, events
import asyncio
from config import api_id, api_hash, phone_number

# Ініціалізуємо клієнта
client = TelegramClient('session_name', api_id, api_hash)

# Обробник подій для нового повідомлення
@client.on(events.NewMessage(incoming=True))
async def handler(event):
    message = event.message.text.lower()
    
    # Перевіряємо, чи є повідомлення привітанням
    if "привіт" in message or "здравствуйте" in message or "добрий день" in message:
        # Відправляємо відповідь
        await event.reply("Привіт! Як я можу допомогти?")

# Запускаємо клієнта
async def main():
    await client.start(phone_number)
    print("Бот запущений!")
    await client.run_until_disconnected()

# Запускаємо асинхронний основний метод
if __name__ == '__main__':
    asyncio.run(main())
