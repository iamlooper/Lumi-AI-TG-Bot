import json
import os

from git import Repo


class _Config:
    class CMD:
        def __init__(self, func, path, doc):
            self.func = func
            self.path = path
            self.doc = doc or "Not Documented."

    def __init__(self):
        self.API: str = os.environ.get("VIC_API")

        self.API_TOKEN = os.environ.get("VIC_API_TOKEN")

        self.BOT_NAME: str = os.environ.get("BOT_NAME")

        self.CMD_DICT: dict[str, _Config.CMD] = {}

        self.DEV_MODE: int = int(os.environ.get("DEV_MODE", 0))

        self.INIT_TASKS: list = []

        self.LOG_CHAT: int = int(os.environ.get("LOG_CHAT"))

        self.TRIGGER: str = os.environ.get("TRIGGER", "/")

        self.REPO = Repo(".")

        self.USERS: list[int] = json.loads(os.environ.get("USERS", "[]"))

        self.UPSTREAM_REPO: str = os.environ.get(
            "UPSTREAM_REPO", "https://github.com/iamlooper/VIC-TG-Bot"
        )

    def __str__(self):
        config_dict = self.__dict__.copy()
        return json.dumps(config_dict, indent=4, ensure_ascii=False, default=str)


Config = _Config()
