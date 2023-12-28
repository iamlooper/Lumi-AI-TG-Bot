import os

from pyrogram.enums import ChatType

from app import BOT, Message, bot


async def init_task() -> None:
    restart_msg = int(os.environ.get("RESTART_MSG", 0))
    restart_chat = int(os.environ.get("RESTART_CHAT", 0))
    if restart_msg and restart_chat:
        await bot.get_chat(restart_chat)
        await bot.edit_message_text(
            chat_id=restart_chat, message_id=restart_msg, text="__Started__"
        )
        os.environ.pop("RESTART_MSG", "")
        os.environ.pop("RESTART_CHAT", "")


@bot.add_cmd(cmd="restart")
async def restart(bot: BOT, message: Message, u_resp: Message | None = None) -> None:
    """
    CMD: RESTART
    INFO: Restart the Bot.
    FLAGS: -h for hard restart and clearing logs
    Usage:
        .restart | .restart -h
    """
    reply: Message = u_resp or await message.reply("Restarting....")
    if reply.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        os.environ["RESTART_MSG"] = str(reply.id)
        os.environ["RESTART_CHAT"] = str(reply.chat.id)
    await bot.restart(hard="-h" in message.flags)
