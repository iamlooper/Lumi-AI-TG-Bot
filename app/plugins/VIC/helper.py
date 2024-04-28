from async_lru import alru_cache
from pyrogram.enums import ParseMode
from pyrogram.raw.functions.messages import SetTyping
from pyrogram.raw.types import SendMessageCancelAction, SendMessageTypingAction

from app import Config, Message, bot
from app.utils.aiohttp_tools import aio

def add_response_json_to_convo(message: Message, query: str, response_json: dict | None = None):
    if response_json is not None:
        if "web_search_results" in response_json:
            Config.CONVO_DICT[message.unique_chat_user_id].extend(
                [
                    {
                        "role": "user",
                        "content": "."
                    },
                    {
                        "role": "ai",
                        "content": response_json["web_search_results"]
                    }
                ]
            )

        if "files_contents" in response_json:
            Config.CONVO_DICT[message.unique_chat_user_id].extend(
                [
                    {
                        "role": "user",
                        "content": "."
                    },
                    {
                        "role": "ai",
                        "content": response_json["files_contents"]
                    }
                ]
            )

        Config.CONVO_DICT[message.unique_chat_user_id].extend(
            [
                {
                    "role": "user",
                    "content": query
                },
                {
                    "role": "ai",
                    "content": response_json["response"]
                }
            ]
        )


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
    async with aio.session.post(
        url=url,
        headers={"Content-Type": "application/json"},
        data=data
    ) as ses:
        await bot.invoke(SetTyping(peer=peer, action=SendMessageTypingAction()))
        response_json = await ses.json()
    add_response_json_to_convo(message, query, response_json)
    ai_response_text = response_json["response"]
    await message.reply(ai_response_text, parse_mode=ParseMode.MARKDOWN)
    await bot.invoke(SetTyping(peer=peer, action=SendMessageCancelAction()))
