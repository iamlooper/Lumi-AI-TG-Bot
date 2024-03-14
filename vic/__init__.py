import os
import sys


if os.path.isfile("app_error.txt"):
    print("aborting boot process, remove 'app_error.txt' to start bot.")
    sys.exit(0)


from ub_core import Config, Message, Convo, BOT, bot, LOGGER  # NOQA
