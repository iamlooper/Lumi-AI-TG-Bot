import os
from app import LOGGER
import traceback

if __name__ == "__main__":
    from app import bot

    try:
        bot.run(bot.boot())
    except BaseException:
        LOGGER.error(traceback.format_exc())
        os.system("touch app_error.txt")
