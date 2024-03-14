if __name__ == "__main__":
    import os
    from vic import bot, LOGGER

    try:
        bot.run(bot.boot())
    except Exception as e:
        LOGGER.error(e, exc_info=True)
        os.system("touch app_error.txt")
