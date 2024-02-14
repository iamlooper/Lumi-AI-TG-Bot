import asyncio
import json
import os
from collections import defaultdict
from typing import Callable, Coroutine

from git import Repo
from pyrogram.types import Message

from app.utils import Str


class Cmd(Str):
    def __init__(self, cmd: str, func: Callable, path: str, sudo: bool):
        self.cmd: str = cmd
        self.func: Callable = func
        self.path: str = path
        self.dirname: str = os.path.basename(os.path.dirname(path))
        self.doc: str = func.__doc__ or "Not Documented."
        self.sudo: bool = sudo


class Config:
    CMD = Cmd

    API: str = os.environ.get("VIC_API")

    API_TOKEN = os.environ.get("VIC_API_TOKEN")

    BOT_NAME: str = os.environ.get("BOT_NAME", "VIC-BOT")

    CHATS: dict[str, list[int]] = {"PRIVATE": [], "GROUPS": []}

    CMD_DICT: dict[str, Cmd] = {}

    CONVO_DICT: dict[str, list[dict[str, str]]] = defaultdict(list)

    CACHED_MEDIA_GROUPS: dict[str, list[Message]] = {}

    DEV_MODE: int = int(os.environ.get("DEV_MODE", 0))

    DB_ID: int = int(os.environ.get("DB_ID", 0))

    INIT_TASKS: list[Coroutine] = []

    LOG_CHAT: int = int(os.environ.get("LOG_CHAT"))

    DB_CHANNEL: int = int(os.environ.get("DB_CHANNEL", LOG_CHAT))

    DB_UPDATE_INTERVAL: int = int(os.environ.get("DB_UPDATE_INTERVAL", 600))

    TRIGGER: str = os.environ.get("TRIGGER", "/")

    REPO: Repo = Repo(".")

    SLEEPER_TASK: asyncio.Task | None = None

    USERS: list[int] = json.loads(os.environ.get("USERS", "[]"))

    UPSTREAM_REPO: str = os.environ.get(
        "UPSTREAM_REPO", "https://github.com/iamlooper/VIC-TG-Bot"
    )
