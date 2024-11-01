import asyncio
import random
import config
from datetime import datetime, timedelta
from telethon import TelegramClient, events, functions
from characterai import aiocai
from colorama import Fore
from fanblock import fans_ids

client = TelegramClient('session_name', config.api_id, config.api_hash)
characterai_client = aiocai.Client(config.charai_token)
characterai_client_unk = aiocai.Client(config.charai_token_unk)
previous_chat_id = config.previous_chat_id
last_post_date = config.last_post_date
last_post_text = config.last_post_text

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
        return response.text

async def get_character_ai_response_unk(message_text):
    me = await characterai_client_unk.get_me()
    async with await characterai_client_unk.connect() as chat:
        new_chat, answer = await chat.new_chat(config.char_id, me.id)
        response = await chat.send_message(config.char_id, new_chat.chat_id, message_text)
        return response.text

def update_config_file(key, value):
    with open('config.py', 'r') as file:
        lines = file.readlines()
    with open('config.py', 'w') as file:
        for line in lines:
            if line.startswith(key):
                file.write(f'{key} = "{value}"\n')
            else:
                file.write(line)

def update_fans_ids_file(fans_ids):
    with open('fanblock.py', 'w') as file:
        file.write('fans_ids = [\n')
        for fan_id in fans_ids:
            file.write(f'    {fan_id},\n')
        file.write(']\n')
        

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    if event.sender_id == config.tg_id:
        await asyncio.sleep(random.randint(1, 5))
        message = event.message.text
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
            response_text = await get_character_ai_response_unk(message)
            async with client.action(event.chat_id, 'typing'):
                await asyncio.sleep(len(response_text) * 0.1 + 1)
            await event.reply(response_text)
            print(f"{Fore.RED}[WRN] Akane: {response_text}{Fore.RESET}")
            await asyncio.sleep(random.randint(1, 5))
            await client(functions.account.UpdateStatusRequest(offline=True))

async def post_daily_message():
    global last_post_date, last_post_text
    now = datetime.now()

    if last_post_date != now.date().isoformat():
        message_for_post = f"Hi Akane, imagine that you have a telegram channel, it's time for a new post for it. Your last post was: '{last_post_text}'"
        
        post_text = await get_character_ai_response_unk(message_for_post)
        await client.send_message(config.tg_channel_id, post_text)
        print(f"{Fore.GREEN}[POST] Повідомлення відправлено в канал: {post_text}{Fore.RESET}")
        
        last_post_date = now.date().isoformat()
        last_post_text = post_text
        update_config_file('last_post_date', last_post_date)
        update_config_file('last_post_text', last_post_text)
    
    while True:
        now = datetime.now()
        next_post_time = now.replace(hour=random.randint(10, 20), minute=random.randint(0, 59), second=0, microsecond=0)
        
        if next_post_time < now:
            next_post_time += timedelta(days=1)
        
        wait_seconds = (next_post_time - now).total_seconds()
        print(f"{Fore.YELLOW}[LOG] Наступний пост буде о {next_post_time.strftime('%H:%M')} (через {wait_seconds / 3600:.2f} годин){Fore.RESET}")
        
        await asyncio.sleep(wait_seconds)
        
        message_for_post = f"Hi Akane, imagine that you have a telegram channel, it's time for a new post for it. Your last post was: '{last_post_text}'"
        
        post_text = await get_character_ai_response_unk(message_for_post)
        
        await client.send_message(config.tg_channel_id, post_text)
        print(f"{Fore.GREEN}[POST] Повідомлення відправлено в канал: {post_text}{Fore.RESET}")
        
        last_post_date = now.date().isoformat()
        last_post_text = post_text
        update_config_file('last_post_date', last_post_date)
        update_config_file('last_post_text', last_post_text)


async def main():
    await client.start(config.phone_number)
    print(f"{Fore.YELLOW}[LOG] Клієнт запущений!{Fore.RESET}")
    await asyncio.gather(client.run_until_disconnected(), post_daily_message())

if __name__ == '__main__':
    asyncio.run(main())
