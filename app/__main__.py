import os
import traceback

from app import LOGGER

if __name__ == "__main__":
    from app import bot

    try:
        bot.run(bot.boot())
    except BaseException:
        LOGGER.error(traceback.format_exc())
        os.system("touch app_error.txt")
