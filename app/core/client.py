import asyncio
import glob
import importlib
import logging
import os
import sys

from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from app import Config
from app.core.conversation import Conversation
from app.core.decorators.add_cmd import AddCmd
from app.core.methods import ChannelLogger, SendMessage
from app.utils.aiohttp_tools import aio

LOGGER = logging.getLogger(Config.BOT_NAME)


def import_modules():
    for py_module in glob.glob(pathname="app/**/[!^_]*.py", recursive=True):
        name = os.path.splitext(py_module)[0]
        py_name = name.replace("/", ".")
        try:
            mod = importlib.import_module(py_name)
            if hasattr(mod, "init_task"):
                Config.INIT_TASKS.append(mod.init_task())
        except Exception as ie:
            LOGGER.error(ie, exc_info=True)


class BOT(AddCmd, SendMessage, ChannelLogger, Client):
    def __init__(self):
        super().__init__(
            name="bot",
            api_id=int(os.environ.get("API_ID")),
            api_hash=os.environ.get("API_HASH"),
            bot_token=os.environ.get("BOT_TOKEN"),
            parse_mode=ParseMode.DEFAULT,
            sleep_threshold=30,
            max_concurrent_transmissions=2,
        )
        self.log = LOGGER
        self.Convo = Conversation

    async def boot(self) -> None:
        await super().start()
        LOGGER.info("Connected to TG.")
        import_modules()
        LOGGER.info("Plugins Imported.")
        await asyncio.gather(*Config.INIT_TASKS)
        Config.INIT_TASKS.clear()
        LOGGER.info("Init Tasks Completed.")
        await self.log_text(text="<i>Started</i>")
        LOGGER.info("Idling...")
        await idle()
        await self.shut_down()

    @staticmethod
    async def shut_down():
        await aio.close()

    async def restart(self, hard=False) -> None:
        await self.shut_down()
        await super().stop(block=False)
        if hard:
            os.execl("/bin/bash", "/bin/bash", "run")
        LOGGER.info("Restarting...")
        os.execl(sys.executable, sys.executable, "-m", "app")


bot: BOT = BOT()
