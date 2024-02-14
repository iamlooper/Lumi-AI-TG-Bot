import os
import sys
import tracemalloc

if os.path.isfile("app_error.txt"):
    print("aborting boot process, remove 'app_error.txt' to start bot.")
    sys.exit(0)

from dotenv import load_dotenv

load_dotenv("config.env")

tracemalloc.start()

if "com.termux" not in os.environ.get("PATH", ""):
    import uvloop

    uvloop.install()


from app.config import Config  # NOQA
from app.core import Message, Convo  # NOQA
from app.core.client import BOT, bot  # NOQA
from app.core.logger import LOGGER  # NOQA
