from async_lru import alru_cache
from pyrogram.raw.functions.messages import SetTyping
from pyrogram.raw.types import SendMessageCancelAction, SendMessageTypingAction
from pyrogram.enums import ParseMode

from app import Config, Message, bot
from app.utils import aiohttp_tools as aio


def extend_or_add(message: Message, data: list):
    if message.unique_chat_user_id in Config.CONVO_DICT:
        Config.CONVO_DICT[message.unique_chat_user_id].extend(data)
    else:
        Config.CONVO_DICT[message.unique_chat_user_id] = data


def check_overflow(message: Message):
    if message.unique_chat_user_id not in Config.CONVO_DICT:
        return False
    return Config.CONVO_DICT[message.unique_chat_user_id][-1]["role"] == "user"


@alru_cache()
async def get_peer(chat_id: int):
    peer = await bot.resolve_peer(chat_id)
    return peer


async def send_response(message: Message, url: str, data: str | None = None):
    peer = await get_peer(message.chat.id)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
    async with aio.SESSION.post(
        url=url,
        headers={"Content-Type": "application/json"},
        data=data,
    ) as ses:
        await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
        response_json_list = await ses.json()
    extend_or_add(message=message, data=response_json_list["chat"])
    ai_response_text = response_json_list["chat"][-1]["content"]
    await message.reply(ai_response_text, parse_mode=ParseMode.MARKDOWN)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageCancelAction()))
