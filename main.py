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

client = TelegramClient('session_name', config.api_id, config.api_hash)
characterai_client = None
previous_chat_id = None
last_message_time = datetime.now()
CHECK_INTERVAL = 3600
MIN_INACTIVE_TIME = timedelta(hours=46)
MAX_INACTIVE_TIME = timedelta(hours=80)

async def get_character_ai_response(message_text):
    global previous_chat_id
    
    me = await characterai_client.get_me()
    async with await characterai_client.connect() as chat:
        if previous_chat_id:
            response = await chat.send_message(config.char_id, previous_chat_id, message_text)
        else:
            new_chat, answer = await chat.new_chat(config.char_id, me.id)
            previous_chat_id = new_chat.chat_id
            update_config_file('previous_chat_id', previous_chat_id)
            response = await chat.send_message(config.char_id, previous_chat_id, message_text)
        
        translated_response = translator.translate(response.text, dest='ru').text
        print(f"{Fore.YELLOW}[LOG] Translated response: {translated_response}{Fore.RESET}")
        return translated_response

async def get_character_ai_response_unk(message_text):
    me = await characterai_client_unk.get_me()
    async with await characterai_client_unk.connect() as chat:
        new_chat, answer = await chat.new_chat(config.char_id, me.id)
        response = await chat.send_message(config.char_id, new_chat.chat_id, message_text)
        
        translated_response = translator.translate(response.text, dest='ru').text
        print(f"{Fore.YELLOW}[LOG] Translated response: {translated_response}{Fore.RESET}")
        return translated_response

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
            message = "The user hasn't written to you for a while. You miss them and want to start a conversation. Write a casual message to initiate chat. Write just the message, nothing else."

            response_text = await get_character_ai_response(message)

            async with client.action(config.tg_id, 'typing'):
                ttime = len(response_text) * 0.1
                await asyncio.sleep(ttime)

            await client.send_message(config.tg_id, response_text)
            print(f"{Fore.BLUE}[MSG] Akane (Initiative): {response_text}{Fore.RESET}")
            last_message_time = current_time

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    global previous_chat_id, last_message_time

    if event.sender_id == config.tg_id:
        last_message_time = datetime.now()
        message = event.message.text

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

            translated_answer = translator.translate(answer.text, dest='ru').text
            
            async with client.action(event.chat_id, 'typing'):
                await asyncio.sleep(len(translated_answer) * 0.1)
            await event.respond(translated_answer)
            print(f"{Fore.YELLOW}[LOG] Персонажа змінено! Новий чат: {previous_chat_id}{Fore.RESET}")
            print(f"{Fore.BLUE}[MSG] Character: {translated_answer}{Fore.RESET}")
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
            
            translated_answer = translator.translate(answer.text, dest='ru').text
            
            async with client.action(event.chat_id, 'typing'):
                await asyncio.sleep(len(translated_answer) * 0.1)
            await event.respond(translated_answer)
            print(f"{Fore.YELLOW}[LOG] Створено новий чат з ID: {previous_chat_id}{Fore.RESET}")
            print(f"{Fore.BLUE}[MSG] Akane: {translated_answer}{Fore.RESET}")
            return

        await asyncio.sleep(random.randint(1, 5))
        await event.message.mark_read()
        print (f"{Fore.BLUE}[MSG] Oleh: {message}{Fore.RESET}")
        rtime = len(message) * 0.03
        await asyncio.sleep(rtime)
        print (f"{Fore.YELLOW}[LOG] Час читання: {rtime:.2f}{Fore.RESET}")
        response_text = await get_character_ai_response(message)
        async with client.action(event.chat_id, 'typing'):
            ttime = len(response_text) * 0.1
            await asyncio.sleep(ttime)
        print (f"{Fore.YELLOW}[LOG] Час написання: {ttime:.2f}{Fore.RESET}")
        if random.random() < 0.25:
            await event.reply(response_text)
        else:
            await client.send_message(event.chat_id, response_text)
        print (f"{Fore.BLUE}[MSG] Akane: {response_text}{Fore.RESET}")
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
