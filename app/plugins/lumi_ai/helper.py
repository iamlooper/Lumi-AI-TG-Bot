import ssl
from async_lru import alru_cache
from pyrogram.enums import ParseMode
from pyrogram.raw.functions.messages import SetTyping
from pyrogram.raw.types import SendMessageCancelAction, SendMessageTypingAction

from app import Config, Message, bot
from app.utils.aiohttp_tools import aio

def add_response_json_to_convo(message: Message, query: str, response_json: dict | None = None):
    if response_json is not None:
        convo_entry = [
            {
                "role": "user",
                "content": query
            },
            {
                "role": "ai",
                "content": response_json["response"]
            }
        ]

        if "files" in response_json:
            convo_entry[0]["files"] = response_json["files"]

        Config.CONVO_DICT[message.unique_chat_user_id].extend(convo_entry)


def check_overflow(message: Message):
    if message.unique_chat_user_id not in Config.CONVO_DICT:
        return False
    return Config.CONVO_DICT[message.unique_chat_user_id][-1]["role"] == "user"


@alru_cache()
async def get_peer(chat_id: int):
    peer = await bot.resolve_peer(chat_id)
    return peer


async def send_response(message: Message, query: str, url: str, data: str | None = None):
    peer = await get_peer(message.chat.id)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aio.session.post(
        url=url,
        headers={"Content-Type": "application/json"},
        data=data,
        ssl=ssl_context
    ) as ses:
        await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
        response_json = await ses.json()
    add_response_json_to_convo(message, query, response_json)
    ai_response_text = response_json["response"]
    await message.reply(ai_response_text, parse_mode=ParseMode.MARKDOWN)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageCancelAction()))
