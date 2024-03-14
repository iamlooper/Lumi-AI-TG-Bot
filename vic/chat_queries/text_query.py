import json
import os

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message as Msg

from vic import BOT, Message, bot
from vic import extra_config
from vic.helper import check_overflow, send_response


def chat_convo_check(_, client, message: Message, media: bool = False) -> bool:
    contains_media = message.photo or message.document
    if (
        (not message.text if not media else not contains_media)
        or message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}
        or not message.reply_to_message
        or not message.reply_to_message.from_user
        or message.reply_to_message.from_user.id != client.me.id
        or f"{message.chat.id}-{message.from_user.id}" not in extra_config.CONVO_DICT
    ):
        return False
    return True


def private_convo_check(_, __, message: Message, media: bool = False) -> bool:
    contains_media = message.photo or message.document
    if (
        (not message.text if not media else not contains_media)
        or not message.chat.type == ChatType.PRIVATE
        or f"{message.chat.id}-{message.from_user.id}" not in extra_config.CONVO_DICT
    ):
        return False
    return True


vic_text_chat_filter = filters.create(chat_convo_check) | filters.create(
    private_convo_check
)


@bot.on_message(vic_text_chat_filter, group=2)
async def text_query(bot: BOT, message: Message | Msg):
    message = Message.parse(message)
    if message.text.startswith("/ask"):
        input = message.input
    else:
        input = message.text

    overflow = check_overflow(message=message)
    if overflow:
        return

    url = os.path.join(extra_config.API, "chat")
    history = extra_config.CONVO_DICT[message.unique_chat_user_id]
    data = json.dumps({"query": input, "history": history})
    await send_response(message=message, url=url, data=data)
