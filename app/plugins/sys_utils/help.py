from collections import defaultdict

from app import BOT, Config, Message, bot


@bot.add_cmd(cmd="help")
async def cmd_list(bot: BOT, message: Message) -> None:
    """
    CMD: HELP
    INFO: Check info/about available cmds.
    USAGE:
        .help help | .help
    """
    cmd = message.input.strip()
    if not cmd:
        await message.reply(text=get_cmds(), del_in=30, block=True)
    elif cmd not in Config.CMD_DICT.keys():
        await message.reply(
            text=f"Invalid <b>{cmd}</b>, check {message.trigger}help", del_in=5
        )
    else:
        raw_help_str = Config.CMD_DICT[cmd].doc
        parsed_str = "\n".join(
            [x.replace("    ", "", 1) for x in raw_help_str.splitlines()]
        )
        await message.reply(text=f"<pre language=java>{parsed_str}</pre>", del_in=30)


def get_cmds() -> str:
    dir_dict = defaultdict(list)
    for cmd in Config.CMD_DICT.values():
        dir_dict[cmd.dirname].append(cmd.cmd)
    sorted_keys = sorted(dir_dict.keys())
    help_str = ""
    for key in sorted_keys:
        help_str += f"\n\n\n<b>{key.capitalize()}:</b>\n"
        help_str += "  ".join([f"<code>{cmd}</code>" for cmd in dir_dict[key]])
    return help_str
