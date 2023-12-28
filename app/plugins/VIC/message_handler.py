from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message as Msg

from app import BOT, Message, bot
from app.plugins.VIC import chats


def chat_convo_check(filters, client: BOT, message: Msg, media: bool = False) -> bool:
    if (
        (not message.text if not media else not message.media)
        or message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}
        or not message.reply_to_message
        or not message.reply_to_message.from_user
        or message.reply_to_message.from_user.id != client.me.id
        or f"{message.chat.id}-{message.from_user.id}" not in chats.CONVO_DICT
    ):
        return False
    return True


def private_convo_check(
    filters, client: BOT, message: Msg, media: bool = False
) -> bool:
    if (
        (not message.text if not media else not message.media)
        or not message.chat.type == ChatType.PRIVATE
        or f"{message.chat.id}-{message.from_user.id}" not in chats.CONVO_DICT
    ):
        return False
    return True


async def media_check(filters, client: BOT, message: Msg) -> bool:
    media = chat_convo_check(
        filters, client, message, media=True
    ) or private_convo_check(filters, client, message, media=True)
    if not media:
        return False
    if message.media_group_id:
        group: list[Message] = await chats.get_media_group(message=message)
        return group[0].id == message.id
    return True


@bot.on_message(filters.command(commands="ask", prefixes="/"), group=2)
async def start_query(bot: BOT, message: Msg):
    message = Message.parse_message(message)
    input = message.input
    if not input:
        await message.reply("Usage: `/ask Hello`")
        return

    history = chats.CONVO_DICT.pop(message.unique_chat_user_id, None)
    if history:
        await message.reply("Starting a new chat...")
    await chats.text_query(bot=bot, message=message)
    message.stop_propagation()


@bot.on_message(filters.command(commands="clear", prefixes="/"), group=2)
async def clear_history(bot: BOT, message: Message):
    message = Message.parse_message(message)
    history = chats.CONVO_DICT.pop(message.unique_chat_user_id, None)
    if history:
        await message.reply("History Cleared!")


bot.add_handler(
    MessageHandler(
        callback=chats.text_query,
        filters=filters.create(chat_convo_check) | filters.create(private_convo_check),
    ),
    group=2,
)
bot.add_handler(
    MessageHandler(
        callback=chats.media_query,
        filters=filters.create(media_check),
    ),
    group=2,
)
