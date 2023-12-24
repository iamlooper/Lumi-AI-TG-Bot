import json

from pyrogram.raw.functions.messages import SetTyping
from pyrogram.raw.types import SendMessageCancelAction, SendMessageTypingAction
from pyrogram.types import Message as Msg

from app import BOT, Config, Message
from app.utils import aiohttp_tools as aio

CONVO_DICT: dict[str, list[dict[str, str]]] = {}


def update_or_add(message: Message, data: dict):
    if message.unique_chat_user_id in CONVO_DICT:
        CONVO_DICT[message.unique_chat_user_id].append(data)
    else:
        CONVO_DICT[message.unique_chat_user_id] = [data]


def check_overflow(message: Message):
    if message.unique_chat_user_id not in CONVO_DICT:
        return False
    return CONVO_DICT[message.unique_chat_user_id][-1]["role"] == "user"


async def handle_query(bot: BOT, message: Message | Msg):
    if not isinstance(message, Message):
        message = Message.parse_message(message)
        input = message.text
    else:
        input = message.input
    overflow = check_overflow(message=message)
    if overflow:
        return
    peer = await bot.resolve_peer(message.chat.id)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
    update_or_add(message=message, data={"role": "user", "content": input})
    data = json.dumps({"messages": CONVO_DICT[message.unique_chat_user_id]})
    async with aio.SESSION.post(
        url=Config.API,
        headers={"Content-Type": "application/json"},
        data=data,
    ) as ses:
        response_text = await ses.text()
    update_or_add(message=message, data={"role": "ai", "content": response_text})
    await message.reply(response_text)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageCancelAction()))
