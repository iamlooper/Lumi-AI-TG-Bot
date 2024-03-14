from pyrogram import filters
from pyrogram.handlers import MessageHandler, EditedMessageHandler
from pyrogram.types import Message
from ub_core.core.handlers.handler import cmd_dispatcher

from vic import Config, extra_config, bot


def cmd_check(message: Message, trigger: str) -> bool:
    start_str = message.text.split(maxsplit=1)[0]
    cmd = start_str.replace(trigger, "", 1)
    return bool(cmd in Config.CMD_DICT.keys())


def basic_check(message: Message):
    if message.reactions or not message.text or not message.from_user:
        return True


def users_check(_, __, message: Message) -> bool:
    if (
        basic_check(message)
        or not message.text.startswith(extra_config.TRIGGER)
        or message.from_user.id not in extra_config.USERS
    ):
        return False
    cmd = cmd_check(message, extra_config.TRIGGER)
    return cmd


users_filter = filters.create(users_check)


# Invalid Message Filter
@bot.on_message(filters.create(lambda _, __, m: not m.chat), group=0)
async def _(_, m):
    m.stop_propagation()


# SUDO Commands Handler
bot.add_handler(MessageHandler(callback=cmd_dispatcher, filters=users_filter), group=1)
bot.add_handler(
    EditedMessageHandler(callback=cmd_dispatcher, filters=users_filter), group=1
)
