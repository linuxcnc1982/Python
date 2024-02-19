from aiogram import Bot, Dispatcher
from typing import Final

import asyncio
#TOKEN :Final='6889510436:AAFdV8cnLmxl8R67Rr2iihlXy4VwcHtcz-E'#gazpromcert_bot
bot = Bot(token='6889510436:AAFdV8cnLmxl8R67Rr2iihlXy4VwcHtcz-E')
dp = Dispatcher(bot=bot)

async def main():
    from handlers import dp
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
