import os
import sys
import tracemalloc

if os.path.isfile("app_error.txt"):
    print("aborting boot process, remove 'app_error.txt' to start bot.")
    sys.exit(0)

from dotenv import load_dotenv

load_dotenv("config.env")

tracemalloc.start()

from app.config import Config  # NOQA
from app.core import LOGGER  # NOQA
from app.core import Message  # NOQA
from app.core.client.client import BOT  # NOQA


if "com.termux" not in os.environ.get("PATH", ""):
    import uvloop

    uvloop.install()

bot: BOT = BOT()

from app.core.decorators.try_except import try_  # NOQA
