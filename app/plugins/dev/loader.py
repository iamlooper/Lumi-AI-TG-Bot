import importlib
import inspect
import os
import sys
import traceback

from app import BOT, Config, Message


async def loader(bot: BOT, message: Message) -> Message | None:
    if (
        not message.replied
        or not message.replied.document
        or not message.replied.document.file_name.endswith(".py")
    ) and "-r" not in message.flags:
        await message.reply("Reply to a Plugin.")
        return
    if "-r" in message.flags:
        plugin = message.flt_input
        cmd_module = Config.CMD_DICT.get(plugin)
        if not cmd_module:
            await message.reply(text="Invalid cmd.")
            return
        module = str(cmd_module.func.__module__)
    else:
        file_name: str = os.path.splitext(message.replied.document.file_name)[0]
        module = f"app.temp.{file_name}"
        await message.replied.download("app/temp/")
    reply: Message = await message.reply("Loading....")
    reload = sys.modules.pop(module, None)
    status: str = "Reloaded" if reload else "Loaded"
    try:
        importlib.import_module(module)
    except Exception:
        await reply.edit(str(traceback.format_exc()))
        return
    await reply.edit(f"{status} {module}")


if Config.DEV_MODE:
    Config.CMD_DICT["load"] = Config.CMD(
        cmd="load",
        func=loader,
        path=inspect.stack()[0][1],
        sudo=False,
    )
