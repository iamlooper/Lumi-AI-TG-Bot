import logging

from pyrogram import Client
from pyrogram.enums import ParseMode

from app import Config
from app.core.types.message import Message

LOGGER = logging.getLogger(Config.BOT_NAME)


class ChannelLogger(Client):
    async def log_text(
        self,
        text,
        name="log.txt",
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML,
        type: str = "",
    ) -> Message:
        if type:
            if hasattr(LOGGER, type):
                getattr(LOGGER, type)(text)
            text = f"#{type.upper()}\n{text}"

        return (await self.send_message(
            chat_id=Config.LOG_CHAT,
            text=text,
            name=name,  # NOQA
            disable_web_page_preview=disable_web_page_preview,
            parse_mode=parse_mode,
        ))  # fmt:skip

    @staticmethod
    async def log_message(message: Message):
        return (await message.copy(chat_id=Config.LOG_CHAT))  # fmt: skip
