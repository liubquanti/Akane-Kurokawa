import asyncio
import random
import config
import time
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError
from colorama import Fore
from fanblock import fans_ids
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetShortName, InputDocument

client = TelegramClient('session_name', config.api_id, config.api_hash)
characterai_client = None
previous_chat_id = None
last_message_time = datetime.now()
CHECK_INTERVAL = 3600
MIN_INACTIVE_TIME = timedelta(hours=28)
MAX_INACTIVE_TIME = timedelta(hours=40)

async def initialize_characterai_client():
    global characterai_client, previous_chat_id
    characterai_client = await get_client(token=config.charai_token)
    previous_chat_id = config.previous_chat_id

async def get_character_ai_response(message_text, message_time):
    global previous_chat_id

    try:
        formatted_message = f"{message_text}\n*Message time: {message_time}*\n*You can send a sticker to the person you are chatting with, if appropriate. To do this, add one of the following emojis at the end of your message 😊, 😂, ❤️*"
        if previous_chat_id:
            answer = await characterai_client.chat.send_message(config.char_id, previous_chat_id, formatted_message)
        else:
            chat, greeting_message = await characterai_client.chat.create_chat(config.char_id)
            previous_chat_id = chat.chat_id
            update_config_file('previous_chat_id', previous_chat_id)
            answer = await characterai_client.chat.send_message(config.char_id, previous_chat_id, formatted_message)
        return answer.get_primary_candidate().text
    except SessionClosedError:
        print("[ERROR] CharacterAI session closed. Reinitializing...")
        await initialize_characterai_client()
        return await get_character_ai_response(message_text, message_time)

def update_config_file(key, value):
    with open('config.py', 'r') as file:
        lines = file.readlines()
    with open('config.py', 'w') as file:
        for line in lines:
            if line.startswith(key):
                file.write(f"{key} = '{value}'\n")
            else:
                file.write(line)

def update_fans_ids_file(fans_ids):
    with open('fanblock.py', 'w') as file:
        file.write('fans_ids = [\n')
        for fan_id in fans_ids:
            file.write(f'    {fan_id},\n')
        file.write(']\n')

async def check_inactivity():
    global last_message_time
    while True:
        await asyncio.sleep(CHECK_INTERVAL)
        current_time = datetime.now()
        inactive_duration = current_time - last_message_time

        if MIN_INACTIVE_TIME <= inactive_duration <= MAX_INACTIVE_TIME:
            message = "*The user hasn't written to you for a while. You miss them and want to start a conversation. Write a casual message to initiate chat. Write just the message, nothing else.*"

            response_text = await get_character_ai_response(message)

            async with client.action(config.tg_id, 'typing'):
                ttime = len(response_text) * 0.1
                await asyncio.sleep(ttime)

            await client.send_message(config.tg_id, response_text)
            print(f"{Fore.BLUE}[MSG] Akane (Initiative): {response_text}{Fore.RESET}")
            last_message_time = current_time

async def send_sticker_by_emoji(chat_id, emoji):
    try:
        # Отримуємо стікерпак
        sticker_set = await client(GetStickerSetRequest(
            stickerset=InputStickerSetShortName('akane_by_pinterest_to_stickerbot'),
            hash=0
        ))

        # Шукаємо стікер за емодзі
        for document in sticker_set.documents:
            for attribute in document.attributes:
                if hasattr(attribute, 'alt') and emoji in attribute.alt:  # Перевіряємо емодзі
                    # Відправляємо стікер
                    await client.send_file(chat_id, InputDocument(
                        id=document.id,
                        access_hash=document.access_hash,
                        file_reference=document.file_reference
                    ))
                    print(f"{Fore.GREEN}[LOG] Стікер з емодзі '{emoji}' відправлено.{Fore.RESET}")
                    return True

        print(f"{Fore.RED}[WRN] Стікера з емодзі '{emoji}' не знайдено в паку.{Fore.RESET}")
        return False
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Помилка при відправці стікера: {e}{Fore.RESET}")
        return False

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    global previous_chat_id, last_message_time

    if event.sender_id == config.tg_id:
        last_message_time = datetime.now()
        message = event.message.text
        message_time = event.message.date.strftime("%Y-%m-%d %H:%M:%S")

        if message.startswith("/change "):
            new_char_id = message.split(" ")[1]
            print(f"{Fore.YELLOW}[LOG] Зміна персонажу на {new_char_id}...{Fore.RESET}")

            update_config_file('char_id', new_char_id)
            config.char_id = new_char_id

            async for msg in client.iter_messages(event.chat_id):
                if msg.id != event.message.id:
                    await msg.delete()

            chat, greeting_message = await characterai_client.chat.create_chat(new_char_id)
            previous_chat_id = chat.chat_id
            update_config_file('previous_chat_id', previous_chat_id)

            await event.message.delete()

            async with client.action(event.chat_id, 'typing'):
                await asyncio.sleep(len(greeting_message.get_primary_candidate().text) * 0.1)
            await event.respond(greeting_message.get_primary_candidate().text)
            print(f"{Fore.YELLOW}[LOG] Персонажа змінено! Новий чат: {previous_chat_id}{Fore.RESET}")
            print(f"{Fore.BLUE}[MSG] Character: {greeting_message.get_primary_candidate().text}{Fore.RESET}")
            return

        if message == "/stop":
            print(f"{Fore.YELLOW}[LOG] Видалення повідомлень та створення нового чату...{Fore.RESET}")

            async for msg in client.iter_messages(event.chat_id):
                if msg.id != event.message.id:
                    await msg.delete()

            chat, greeting_message = await characterai_client.chat.create_chat(config.char_id)
            previous_chat_id = chat.chat_id
            update_config_file('previous_chat_id', previous_chat_id)

            await event.message.delete()

            async with client.action(event.chat_id, 'typing'):
                await asyncio.sleep(len(greeting_message.get_primary_candidate().text) * 0.1)
            await event.respond(greeting_message.get_primary_candidate().text)
            print(f"{Fore.YELLOW}[LOG] Створено новий чат з ID: {previous_chat_id}{Fore.RESET}")
            print(f"{Fore.BLUE}[MSG] Akane: {greeting_message.get_primary_candidate().text}{Fore.RESET}")
            return

        # Перевіряємо, чи є емодзі в кінці повідомлення
        if len(message) > 0 and message[-1] in ["😊", "😂", "❤️"]:  # Додайте потрібні емодзі
            emoji = message[-1]
            print(f"[DEBUG] Знайдено емодзі: {emoji}. Виклик send_sticker_by_emoji...")
            if await send_sticker_by_emoji(event.chat_id, emoji):
                print(f"[DEBUG] Стікер успішно відправлено для емодзі: {emoji}")
                return
            else:
                print(f"[DEBUG] Не вдалося відправити стікер для емодзі: {emoji}")

        await asyncio.sleep(random.randint(1, 5))
        await event.message.mark_read()
        print(f"{Fore.BLUE}[MSG] Oleh: {message}{Fore.RESET}")
        rtime = len(message) * 0.03
        await asyncio.sleep(rtime)
        print(f"{Fore.YELLOW}[LOG] Час читання: {rtime:.2f}{Fore.RESET}")
        response_text = await get_character_ai_response(message, message_time)

        # Перевіряємо, чи є емодзі в повідомленні нейромережі
        for emoji in ["😊", "😂", "❤️"]:  # Додайте потрібні емодзі
            if emoji in response_text:
                async with client.action(event.chat_id, 'typing'):
                    ttime = len(response_text) * 0.1
                    await asyncio.sleep(ttime)
                print(f"{Fore.YELLOW}[LOG] Час написання: {ttime:.2f}{Fore.RESET}")
                await client.send_message(event.chat_id, response_text)
                print(f"{Fore.BLUE}[MSG] Akane: {response_text}{Fore.RESET}")
                if await send_sticker_by_emoji(event.chat_id, emoji):
                    return
                else:
                    print(f"{Fore.RED}[WRN] Не вдалося відправити стікер для емодзі: {emoji}{Fore.RESET}")
                return

        async with client.action(event.chat_id, 'typing'):
            ttime = len(response_text) * 0.1
            await asyncio.sleep(ttime)
        print(f"{Fore.YELLOW}[LOG] Час написання: {ttime:.2f}{Fore.RESET}")
        if random.random() < 0.25:
            await event.reply(response_text)
        else:
            await client.send_message(event.chat_id, response_text)
        print(f"{Fore.BLUE}[MSG] Akane: {response_text}{Fore.RESET}")
        await asyncio.sleep(random.randint(1, 5))
        await client(functions.account.UpdateStatusRequest(offline=True))
    else:
        if event.sender_id in fans_ids:
            await asyncio.sleep(random.randint(1, 5))
            await client(functions.account.UpdateStatusRequest(offline=False))
            await asyncio.sleep(random.randint(1, 5))
            await event.message.mark_read()
            print(f"{Fore.RED}[WRN] Було проігноровано користувача {event.sender_id}.{Fore.RESET}")
            await asyncio.sleep(random.randint(1, 5))
            await client(functions.account.UpdateStatusRequest(offline=True))
        else:
            await asyncio.sleep(random.randint(1, 5))
            await client(functions.account.UpdateStatusRequest(offline=False))
            await asyncio.sleep(random.randint(1, 3))
            await event.message.mark_read()
            fans_ids.append(event.sender_id)
            update_fans_ids_file(fans_ids)
            print(f"{Fore.RED}[WRN] Користувач {event.sender_id} намагався написати!{Fore.RESET}")
            message = event.message.text
            print(f"{Fore.RED}[WRN] {event.sender_id}: {message}{Fore.RESET}")
            message = 'Imagine that a fan has written to you a message: "%s", but you don\'t want to communicate with them, write a text for reply send me just a text of reply, nothing else' % message
            await event.message.mark_read()
            await asyncio.sleep(len(message) * 0.03 + 1)
            response_text = await get_character_ai_response(message)
            async with client.action(event.chat_id, 'typing'):
                await asyncio.sleep(len(response_text) * 0.1 + 1)
            await event.reply(response_text)
            print(f"{Fore.RED}[WRN] Akane: {response_text}{Fore.RESET}")
            await asyncio.sleep(random.randint(1, 5))
            await client(functions.account.UpdateStatusRequest(offline=True))

async def main():
    await initialize_characterai_client()
    await client.start(config.phone_number)
    print(f"{Fore.YELLOW}[LOG] Модель Akane Kurokawa запущено!{Fore.RESET}")

    asyncio.create_task(check_inactivity())

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
