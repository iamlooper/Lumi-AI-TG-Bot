import asyncio

from pyrogram import filters
from pyrogram.types import Message as Msg

from app import BOT, Config, Message, bot
from app.plugins.lumi_ai.text_query import text_query

HELP_TEXT = """Hello. I am Lumi, a friendly AI sidekick with a human-like personality.

**Usage**:
- /ask Hello! (starts new chat, clears previous if exists)
- /web_ask Hello! How many subscribers does MrBeast have on YouTube? (starts web search chat, clears previous if exists)
- /clear (clears chat history)

**Continued Conversation**:
- Public chat: Reply to Lumi to continue.
- Private chat: No need to reply to Lumi."""


@bot.on_message(filters.command(commands="start", prefixes="/"), group=1)
async def start_bot(bot: BOT, message: Msg):
    await message.reply(text=HELP_TEXT)
    message.stop_propagation()


async def valid_user(message: Msg) -> bool:
    if not message.from_user:
        await message.reply(text="Anonymous Admins | Channels cannot use this command.")
        return False
    return True


@bot.on_message(filters.command(commands="ask", prefixes="/"), group=1)
async def ask_query(bot: BOT, message: Msg):
    if not (await valid_user(message)):
        return
    message = Message.parse(message)
    query = message.input
    if not query:
        await message.reply("Usage: `/ask Hello`")
        return

    history = Config.CONVO_DICT.pop(message.unique_chat_user_id, None)
    if history:
        await message.reply("Starting a new chat...")
    Config.WEB_SEARCH[message.unique_chat_user_id] = False
    await text_query(bot=bot, message=message)
    message.stop_propagation()
    
@bot.on_message(filters.command(commands="web_ask", prefixes="/"), group=1)
async def web_ask_query(bot: BOT, message: Msg):
    if not (await valid_user(message)):
        return
    message = Message.parse(message)
    query = message.input
    if not query:
        await message.reply("Usage: `/web_ask Hello. How many subscribers does MrBeast have on YouTube?`")
        return

    history = Config.CONVO_DICT.pop(message.unique_chat_user_id, None)
    if history:
        await message.reply("Starting a new chat...")
    Config.WEB_SEARCH[message.unique_chat_user_id] = True
    await text_query(bot=bot, message=message)
    message.stop_propagation()

@bot.on_message(filters.command(commands="clear", prefixes="/"), group=1)
async def clear_history(bot: BOT, message: Msg):
    if not (await valid_user(message)):
        return
    message = Message.parse(message)
    history = Config.CONVO_DICT.pop(message.unique_chat_user_id, None)
    if history:
        await message.reply("Chat history cleared!")
    message.stop_propagation()


@bot.add_cmd(cmd="total")
async def total_chats(bot: BOT, message: Message):
    users = len(Config.CHATS["PRIVATE"])
    groups = len(Config.CHATS["GROUPS"])
    await message.reply(
        f"<u>BOT STATS</u>\n<b>Users</b>: {users}\n<b>Chats</b>: {groups}"
    )


@bot.add_cmd(cmd="broadcast")
async def broadcast_text(bot: BOT, message: Message):
    if not message.input:
        await message.reply("Broadcast text not provided!!!")
        return
    chats = Config.CHATS["GROUPS"]
    total = len(chats)
    total_failed = 0
    failed_str = ""
    for chat in chats:
        try:
            await bot.send_message(chat_id=chat, text=message.input)
            await asyncio.sleep(1)
        except Exception as e:
            total_failed += 1
            failed_str += (
                f"<b>Chat</b>:<code>{chat}</code>\n<b>Error</b>:<code>{e}</code>\n\n"
            )
    final_str = (
        f"\n\nBroadcasted in <b>{total-total_failed}</b> chats."
        f"\n\nFailed to broadcast in <b>{total_failed}</b> chats:\n{failed_str}"
    )
    await message.reply(message.input + final_str)
