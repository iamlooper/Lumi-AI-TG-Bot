from async_lru import alru_cache
from pyrogram.enums import ParseMode
from pyrogram.raw.functions.messages import SetTyping
from pyrogram.raw.types import SendMessageCancelAction, SendMessageTypingAction

from app import Config, Message, bot
from app.utils.aiohttp_tools import aio


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
    async with aio.session.post(
        url=url,
        headers={"Content-Type": "application/json"},
        data=data,
    ) as ses:
        await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
        response_json_list = await ses.json()
    Config.CONVO_DICT[message.unique_chat_user_id].extend(data)
    ai_response_text = response_json_list["chat"][-1]["content"]
    await message.reply(ai_response_text, parse_mode=ParseMode.MARKDOWN)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageCancelAction()))
