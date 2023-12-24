from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message as Msg

from app import BOT, Message, bot
from app.plugins.VIC import chats


def chat_convo_check(filters, client: BOT, message: Msg) -> bool:
    if (
        not message.text
        or message.chat.type not in {ChatType.GROUP, ChatType.SUPERGROUP}
        or not message.reply_to_message
        or not message.reply_to_message.from_user
        or message.reply_to_message.from_user.id != client.me.id
        or f"{message.chat.id}-{message.from_user.id}" not in chats.CONVO_DICT
    ):
        return False
    return True


def private_convo_check(filters, client: BOT, message: Msg) -> bool:
    if (
        not message.text
        or not message.chat.type == ChatType.PRIVATE
        or f"{message.chat.id}-{message.from_user.id}" not in chats.CONVO_DICT
    ):
        return False
    return True


@bot.on_message(filters.command(commands="ask", prefixes="/"), group=1)
async def start_query(bot: BOT, message: Msg):
    message = Message.parse_message(message)
    input = message.input
    if not input:
        await message.reply("Usage: '/ask Who are you?'")
        return

    history = chats.CONVO_DICT.pop(message.unique_chat_user_id, None)
    if history:
        await message.reply("Clearing History and Starting new Thread.")
    await chats.handle_query(bot=bot, message=message)
    message.stop_propagation()


bot.add_handler(
    MessageHandler(
        callback=chats.handle_query,
        filters=filters.create(chat_convo_check) | filters.create(private_convo_check),
    ),
    group=1,
)
