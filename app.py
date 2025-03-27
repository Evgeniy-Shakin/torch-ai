from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
import asyncio
import os
from aiogram.fsm.storage.memory import MemoryStorage


from handlers.user_privat import user_private_router
from handlers.admin_group import admin_group_router

ALLOWED_UPDATES = ["message", "edited_message"]

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()
storage = MemoryStorage()

dp.include_router(user_private_router)
dp.include_router(admin_group_router)


async def on_startup(bot):
    print('Bot online')

async def on_shutdown(bot):
    print('Bot ofline...')

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)



if __name__ == "__main__":
    asyncio.run(main())