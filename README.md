# 💙 • Akane-Kurokawa

Персональна розмовна нейронна модель персонажу Акане Курокави на основі Telegram клієнту [Telethon](https://github.com/LonamiWebs/Telethon) та бібліотеки [CharacterAI](https://github.com/kramcat/CharacterAI).

Програма працює, як Telegram клієнт з обліковим записом користувача, який здатен отримувати повідомлення співрозмовника, обробляти їх за допомогою сервісу [Character.AI](https://character.ai/), та надавати відповідь на основі нейронної моделі.

## 📝 • config.py

Для запуску програма вимагає конфігураціний файл `config.py`. 

```python
api_id = ''
api_hash = ''
phone_number = ''
charai_token = ''
char_id = ''
tg_id = 
```
### `api_id` та `api_hash`

API ключі Telegram для роботи клієнту Telethon. Отримати їх можна після створення програми на сайті [my.telegram.org](https://my.telegram.org/).

### `phone_number`

Програма працює, за допомогою облікового запису користувача, тому вам потрібно написати тут номер телефону облікового запису, з яким буде проходити спілкування, у форматі `+XXXXXXXXXXX`.

### `charai_token`

Токен вашого облікового запису Character.AI. Його можна отримати увійшовши до свого облікового запису Character.AI за допомогою запуску спеціального скрипту:
```python
from characterai import aiocai, sendCode, authUser
import asyncio

async def main():
    email = input('YOUR EMAIL: ')

    code = sendCode(email)

    link = input('CODE IN MAIL: ')

    token = authUser(link, email)

    print(f'YOUR TOKEN: {token}')

asyncio.run(main())
```

### `char_id`

Ідентифікатор персонажу, з яким буде проходити спілкування. Його можна отримати з посилання на сайті [Character.AI](https://character.ai/), коли ви відкриєте чат з яким-небуть персонажем. У Акане Курокави це `zQ7Yav1HdV_MzCUsXRaKbeVZuEoLOvlpXn2pSKr-LEU`.

### `tg_id`

Ідентифікатор вашого облікового запису Telegram. Його можна отримати скориставшись Telegram ботом [GetMyIDBot](https://t.me/getmy_idbot).