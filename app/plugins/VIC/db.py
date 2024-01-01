import json

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message as Msg

from app import BOT, Config, bot


# Setup DB CHATS on boot.
async def init_task():
    if not Config.DB_ID:
        return
    db_str: str = (
        await bot.get_messages(chat_id=Config.LOG_CHAT, message_ids=Config.DB_ID)
    ).text
    db_dict = json.loads(db_str)
    if db_dict:
        Config.CHATS = db_dict


# Listen for a new Message and add chat to DB


@bot.on_message(
    filters=(
        filters.create(lambda _, __, m: m.text and m.text.startswith("/"))
        & ~filters.channel
    ),
    group=0,
)
async def new_chat(bot: BOT, message: Msg):
    chat_id = message.chat.id
    if chat_id in Config.CHATS["PRIVATE"] or chat_id in Config.CHATS["GROUPS"]:
        message.continue_propagation()
    if message.chat.type == ChatType.PRIVATE:
        Config.CHATS["PRIVATE"].append(chat_id)
    else:
        Config.CHATS["GROUPS"].append(chat_id)
    await bot.edit_message_text(
        chat_id=Config.LOG_CHAT, message_id=Config.DB_ID, text=json.dumps(Config.CHATS)
    )
    message.continue_propagation()
