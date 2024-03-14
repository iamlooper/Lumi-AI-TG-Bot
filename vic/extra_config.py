import json
import os
from collections import defaultdict
from pyrogram.types import Message


API: str = os.environ.get("VIC_API")

API_TOKEN = os.environ.get("VIC_API_TOKEN")

BOT_NAME: str = os.environ.get("BOT_NAME", "vic-BOT")

CHATS: dict[str, list[int]] = {"PRIVATE": [], "GROUPS": []}

CACHED_MEDIA_GROUPS: dict[str, list[Message]] = {}

CONVO_DICT: dict[str, list[dict[str, str]]] = defaultdict(list)

DB_ID: int = int(os.environ.get("DB_ID", 0))

LOG_CHAT: int = int(os.environ.get("LOG_CHAT"))

DB_CHANNEL: int = int(os.environ.get("DB_CHANNEL", LOG_CHAT))

DB_UPDATE_INTERVAL: int = int(os.environ.get("DB_UPDATE_INTERVAL", 600))

TRIGGER: str = os.environ.get("TRIGGER", "/")

USERS: list[int] = json.loads(os.environ.get("USERS", "[]"))

UPSTREAM_REPO: str = os.environ.get(
    "UPSTREAM_REPO", "https://github.com/iamlooper/VIC-TG-Bot"
)
