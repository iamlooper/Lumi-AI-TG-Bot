from async_lru import alru_cache
from pyrogram.enums import ParseMode
from pyrogram.errors import ChatWriteForbidden
from pyrogram.raw.functions.messages import SetTyping
from pyrogram.raw.types import SendMessageCancelAction, SendMessageTypingAction
from ub_core.utils import aio, get_name

from vic import Message, bot
from vic import extra_config


def check_overflow(message: Message):
    if not extra_config.CONVO_DICT[message.unique_chat_user_id]:
        return False
    return extra_config.CONVO_DICT[message.unique_chat_user_id][-1]["role"] == "user"


@alru_cache()
async def get_peer(chat_id: int):
    peer = await bot.resolve_peer(chat_id)
    return peer


async def send_response(message: Message, url: str, data: str | None = None):
    peer = await get_peer(message.chat.id)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))

    async with aio.session.post(
        url=url, headers={"Content-Type": "application/json"}, data=data
    ) as ses:
        await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
        response_json_list = await ses.json()

    ai_response_text = response_json_list["chat"][-1]["content"]
    if not ai_response_text:
        return

    extra_config.CONVO_DICT[message.unique_chat_user_id].extend(
        response_json_list["chat"]
    )

    try:
        await message.reply(ai_response_text, parse_mode=ParseMode.MARKDOWN)
        await bot.invoke(SetTyping(peer=peer, action=SendMessageCancelAction()))
    except ChatWriteForbidden:
        text = (
            f"Auto-Left Chat: {get_name(message.chat)} [{message.chat.id}]"
            f"\nNot Enough Rights to send message."
        )
        await bot.log_text(text=text, type="info")
        await message.chat.leave()
        return
