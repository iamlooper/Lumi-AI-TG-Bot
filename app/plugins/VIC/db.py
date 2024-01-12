import asyncio
import json
import os
from io import BytesIO

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InputMediaDocument
from pyrogram.types import Message as Msg

from app import BOT, Config, bot, try_


# Setup DB CHATS on boot.
async def init_task():
    if not Config.DB_ID:
        return
    db_file: str | BytesIO = await (
        await bot.get_messages(chat_id=Config.DB_CHANNEL, message_ids=Config.DB_ID)
    ).download(in_memory=True)
    db_str = (db_file.getvalue()).decode("utf-8")
    Config.CHATS = json.loads(db_str)


def new_chat_filter(filters, client, message: Msg) -> bool:
    text = message.text and message.text.startswith("/")
    exists = (
        message.chat.id in Config.CHATS["GROUPS"]
        or message.chat.id in Config.CHATS["PRIVATE"]
    )
    return text and not exists


# Listen for a new Message and add chat to DB
@try_
@bot.on_message(
    filters=(filters.create(new_chat_filter) & ~filters.channel),
    group=0,
)
async def new_chat(bot: BOT, message: Msg):
    chat_id = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        Config.CHATS["PRIVATE"].append(chat_id)
    else:
        Config.CHATS["GROUPS"].append(chat_id)
    message.continue_propagation()


@try_
async def sleeper():
    while True:
        try:
            await asyncio.sleep(Config.DB_UPDATE_INTERVAL)
            await update_db()
        except asyncio.exceptions.CancelledError:
            bot.log.info("Sleeper Task Cancelled")
            return


@try_
async def update_db():
    latest_data = json.dumps(Config.CHATS)
    with open("db.json", 'a'):
        os.utime("db.json", None)    
    with open("db.json", "r") as f:
        if f.read() == latest_data:
            bot.log.info("Duplicate DB Update Skipped.")
            return
    with open("db.json", "w+") as f:
        f.write(latest_data)
    await bot.edit_message_media(
        chat_id=Config.DB_CHANNEL,
        message_id=Config.DB_ID,
        media=InputMediaDocument(media="db.json"),
        file_name="db.json",
    )


Config.SLEEPER_TASK = asyncio.create_task(sleeper())
