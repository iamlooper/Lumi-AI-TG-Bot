import asyncio
import os
from logging import (
    ERROR,
    INFO,
    WARNING,
    Handler,
    StreamHandler,
    basicConfig,
    getLogger,
    handlers,
)

from app import Config, bot

os.makedirs(name="logs", exist_ok=True)

LOGGER = getLogger(Config.BOT_NAME)


class TgErrorHandler(Handler):
    def emit(self, log_record):
        if not bot.is_connected:
            return
        self.format(log_record)
        chat = ""
        if hasattr(log_record, "tg_message"):
            chat = (
                log_record.tg_message.chat.title
                or log_record.tg_message.chat.first_name
            )
        text = (
            f"#{log_record.levelname} #TRACEBACK"
            f"<b>\nChat</b>: {chat}"
            f"\n<b>Line No</b>: <code>{log_record.lineno}</code>"
            f"\n<b>Func</b>: <code>{log_record.funcName}</code>"
            f"\n<b>Module</b>: <code>{log_record.module}</code>"
            f"\n<b>Time</b>: <code>{log_record.asctime}</code>"
            f"\n<b>Error Message</b>:\n<pre language=python>{log_record.exc_text or log_record.message}</pre>"
        )
        asyncio.run_coroutine_threadsafe(
            coro=bot.log_text(text=text, name="traceback.txt"), loop=bot.loop
        )


custom_handler = TgErrorHandler()
custom_handler.setLevel(ERROR)

basicConfig(
    level=INFO,
    format="[%(levelname)s] [%(asctime)s] [%(name)s] [%(module)s]: %(message)s",
    datefmt="%d-%m-%y %I:%M:%S %p",
    handlers={
        handlers.RotatingFileHandler(
            filename="logs/app_logs.txt",
            mode="a",
            maxBytes=5 * 1024 * 1024,
            backupCount=2,
            encoding=None,
            delay=False,
        ),
        StreamHandler(),
        custom_handler,
    },
)

getLogger("pyrogram").setLevel(WARNING)
getLogger("httpx").setLevel(WARNING)
getLogger("aiohttp.access").setLevel(WARNING)
