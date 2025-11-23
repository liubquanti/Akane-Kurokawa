from characterai import aiocai
import asyncio
from config import charai_token, char_id

async def main():
    char = char_id
    client = aiocai.Client(charai_token)

    me = await client.get_me()

    async with await client.connect() as chat:
        new, answer = await chat.new_chat(
            char, me.id
        )

        print(f'{answer.name}: {answer.text}')
        
        while True:
            text = input('YOU: ')

            message = await chat.send_message(
                char, new.chat_id, text
            )

            print(f'{message.name}: {message.text}')

asyncio.run(main())