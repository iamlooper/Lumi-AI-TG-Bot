import asyncio
import traceback
from functools import wraps

from app import bot


def try_(func):
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def run_func(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except BaseException:
                text = (
                    f"<b>FUNC</b>: {func.__name__}"
                    f"\n</b>TRACEBACK</b>:\n<pre language=python>{traceback.format_exc()}</pre>"
                )
                await bot.log_text(text=text, name="traceback.txt", type="error")

    else:

        @wraps(func)
        def run_func(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except BaseException:
                text = (
                    f"<b>FUNC</b>: {func.__name__}"
                    f"\n</b>TRACEBACK</b>:\n<pre language=python>{traceback.format_exc()}</pre>"
                )
                bot.log_text(text=text, name="traceback.txt", type="error")

    return run_func
