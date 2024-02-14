from pyrogram import filters as _filters
from pyrogram.types import Message

from app import Config
from app.core.conversation import Conversation

# Overall BOT filters

convo_filter = _filters.create(
    lambda _, __, message: (message.chat.id in Conversation.CONVO_DICT.keys())
    and (not message.reactions)
)


def cmd_check(message: Message, trigger: str) -> bool:
    start_str = message.text.split(maxsplit=1)[0]
    cmd = start_str.replace(trigger, "", 1)
    return bool(cmd in Config.CMD_DICT.keys())


def basic_check(message: Message):
    if message.reactions or not message.text or not message.from_user:
        return True


def users_check(filters, client, message: Message) -> bool:
    if (
        basic_check(message)
        or not message.text.startswith(Config.TRIGGER)
        or message.from_user.id not in Config.USERS
    ):
        return False
    cmd = cmd_check(message, Config.TRIGGER)
    return cmd


users_filter = _filters.create(users_check)
