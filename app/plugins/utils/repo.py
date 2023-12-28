from app import BOT, Config, Message, bot


@bot.add_cmd(cmd="repo")
async def sauce(bot: BOT, message: Message) -> None:
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"<a href='{Config.UPSTREAM_REPO}'>{Config.BOT_NAME}</a>",
        reply_to_message_id=message.reply_id or message.id,
        disable_web_page_preview=True,
    )
