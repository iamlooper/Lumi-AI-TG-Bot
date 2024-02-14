import asyncio
from typing import Callable

from pyrogram import StopPropagation
from pyrogram.types import Message as Msg

from app import BOT, Config, Convo, Message, bot
from app.core.handlers import filters


@bot.on_message(filters.convo_filter, group=0)
@bot.on_edited_message(filters.convo_filter, group=0)
async def convo_handler(bot: BOT, message: Msg):
    conv_objects: list[Convo] = Convo.CONVO_DICT[message.chat.id]
    for conv_object in conv_objects:
        if conv_object.filters and not (await conv_object.filters(bot, message)):
            message.continue_propagation()
        conv_object.responses.append(message)
        conv_object.response_future.set_result(message)
    message.continue_propagation()


@bot.on_message(filters.users_filter, group=0)
@bot.on_edited_message(filters.users_filter, group=0)
async def cmd_dispatcher(bot: BOT, message: Message, func: Callable = None) -> None:
    message = Message.parse(message)
    func = func or Config.CMD_DICT[message.cmd].func
    task = asyncio.create_task(func(bot, message), name=message.task_id)
    try:
        await task
    except asyncio.exceptions.CancelledError:
        await bot.log_text(text=f"<b>#Cancelled</b>:\n<code>{message.text}</code>")
    except StopPropagation:
        raise StopPropagation
    except Exception as e:
        bot.log.error(e, exc_info=True, extra={"tg_message": message})
    message.stop_propagation()
