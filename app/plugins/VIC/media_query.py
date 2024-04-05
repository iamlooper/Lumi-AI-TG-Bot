import base64
import json
import os
from io import BytesIO

from pyrogram import filters
from pyrogram.types import Message as Msg

from app import BOT, Config, Message, bot
from app.plugins.VIC.helper import check_overflow, send_response
from app.plugins.VIC.text_query import chat_convo_check, private_convo_check
from app.utils.media_helper import MediaExts

ALLOWED_EXTS = {*MediaExts.PHOTO, *MediaExts.TEXT, *MediaExts.DOCUMENT}


async def media_check(filters, client, message: Message) -> bool:
    media = chat_convo_check(
        filters, client, message, media=True
    ) or private_convo_check(filters, client, message, media=True)
    if not media:
        return False
    if message.media_group_id:
        group: list[Message] = await get_media_group(message=message)
        return group[0].id == message.id
    return True


@bot.on_message(filters.create(media_check), group=2)
async def media_query(bot: BOT, message: Message | Msg):
    message = Message.parse(message)
    overflow = check_overflow(message=message)
    if overflow:
        return
    query = message.caption or "Analyze the given file(s) above."
    down_resp = await message.reply("Downloading...")
    media: list | None = await get_media_list(message)
    if not media:
        await down_resp.edit("File size exceeds 2MB or is an unsupported file type.")
        return

    history = Config.CONVO_DICT[message.unique_chat_user_id]
    data = json.dumps({"query": query, "files": media, "history": history})
    await send_response(message=message, query=query, url=Config.API, data=data)


async def get_media_list(message: Message) -> list[dict[str, str]]:
    if message.media_group_id:
        group = Config.CACHED_MEDIA_GROUPS.pop(message.media_group_id)
        group_dict = [await parse_media(msg) for msg in group]
        return [media_dict for media_dict in group_dict if media_dict]
    media_dict = await parse_media(message)
    if media_dict:
        return [media_dict]


async def get_media_group(message: Message) -> list[Message]:
    media_id = message.media_group_id
    cache = Config.CACHED_MEDIA_GROUPS.get(media_id)
    if cache:
        return cache
    group = await message.get_media_group()
    Config.CACHED_MEDIA_GROUPS[media_id] = group
    return group


async def parse_media(message: Message) -> dict[str, str] | None:
    media = message.photo or message.document
    if not hasattr(media, "file_name"):
        media.file_name = f"image_{media.file_unique_id}.png"
    if not check_size(media):
        return
    if os.path.splitext(media.file_name)[-1].lower() not in ALLOWED_EXTS:
        return
    file: BytesIO = (await message.download(in_memory=True)).getvalue()
    return {
        "filename": media.file_name,
        "file_bytes": base64.b64encode(file).decode("utf-8"),
    }


def check_size(media):
    return media.file_size < 2097152