import inspect
from functools import wraps

from app import Config


class AddCmd:
    @staticmethod
    def add_cmd(cmd: str | list):
        def the_decorator(func):
            path = inspect.stack()[1][1]

            @wraps(func)
            def wrapper():
                if isinstance(cmd, list):
                    for _cmd in cmd:
                        Config.CMD_DICT[_cmd] = Config.CMD(
                            func=func, path=path, doc=func.__doc__
                        )
                else:
                    Config.CMD_DICT[cmd] = Config.CMD(
                        func=func, path=path, doc=func.__doc__
                    )

            wrapper()
            return func

        return the_decorator
