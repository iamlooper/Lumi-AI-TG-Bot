import asyncio
import traceback

from pyrogram import filters
from pyrogram.types import Message as Msg

from app import BOT, Config, Message, bot
from app.core.client import filters


@bot.on_message(filters.convo_filter, group=0)
@bot.on_edited_message(filters.convo_filter, group=0)
async def convo_handler(bot: BOT, message: Msg):
    conv_obj: bot.Convo = bot.Convo.CONVO_DICT[message.chat.id]
    if conv_obj.filters and not (await conv_obj.filters(bot, message)):
        message.continue_propagation()
    conv_obj.responses.append(message)
    conv_obj.response.set_result(message)
    message.continue_propagation()


@bot.on_message(filters.users_filter, group=0)
@bot.on_edited_message(filters.users_filter, group=0)
async def cmd_dispatcher(bot: BOT, message: Message) -> None:
    message = Message.parse_message(message)
    func = Config.CMD_DICT[message.cmd].func
    coro = func(bot, message)
    await run_coro(coro, message)
    message.stop_propagation()


async def run_coro(coro, message) -> None | int:
    try:
        task = asyncio.Task(coro, name=message.task_id)
        await task
    except asyncio.exceptions.CancelledError:
        await bot.log(text=f"<b>#Cancelled</b>:\n<code>{message.text}</code>")
    except BaseException:
        await bot.log(
            traceback=f"<pre language=python>{traceback.format_exc()}</pre>",
            chat=message.chat.title or message.chat.first_name,
            func=coro.__name__,
            name="traceback.txt",
        )
        return 1
