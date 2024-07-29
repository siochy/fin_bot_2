#!/usr/bin/env python3.11

import asyncio
import logging
import sys
import os
import dotenv

from aiogram import Bot, Dispatcher

import commands
import takers
import getters


async def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    dotenv.load_dotenv()
    token = os.getenv('TOKEN')
    bot = Bot(token=token)
    dp = Dispatcher()

    dp.include_routers(commands.rt, takers.rt, getters.rt)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
