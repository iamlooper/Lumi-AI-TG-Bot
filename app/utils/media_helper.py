import re
from enum import Enum, auto
from os.path import basename, splitext
from urllib.parse import unquote_plus, urlparse

from pyrogram.enums import MessageMediaType
from pyrogram.types import Message


class MediaType(Enum):
    AUDIO = auto()
    DOCUMENT = auto()
    GIF = auto()
    GROUP = auto()
    MESSAGE = auto()
    PHOTO = auto()
    STICKER = auto()
    VIDEO = auto()


class MediaExts:
    PHOTO = {".png", ".jpg", ".jpeg"}
    VIDEO = {".mp4", ".mkv", ".webm"}
    GIF = {".gif"}
    AUDIO = {".aac", ".mp3", ".opus", ".m4a", ".ogg", ".flac"}
    TEXT = {
        ".txt",
        ".json",
        ".xml",
        ".html",
        ".css",
        ".md",
        ".log",
        ".ini",
        ".conf",
        ".sh",
        ".py",
        ".js",
        ".java",
        ".kt",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
    }
    DOCUMENT = {".pdf", ".docx", ".xlsx"}


def bytes_to_mb(size: int):
    return round(size / 1048576, 1)


def get_filename_from_url(url: str, tg_safe: bool = False) -> str:
    parsed_url = urlparse(unquote_plus(url))
    name = basename(parsed_url.path.rstrip("/"))
    if tg_safe:
        return make_file_name_tg_safe(file_name=name)
    return name


def get_filename_from_headers(headers: dict, tg_safe: bool = False) -> str | None:
    content_disposition = headers.get("Content-Disposition", "")
    match = re.search(r"filename=(.+)", content_disposition)
    if not match:
        return
    if tg_safe:
        return make_file_name_tg_safe(file_name=match.group(1))
    return match.group(1)


def make_file_name_tg_safe(file_name: str) -> str:
    if file_name.lower().endswith((".webp", ".heic")):
        file_name = file_name + ".jpg"
    elif file_name.lower().endswith(".webm"):
        file_name = file_name + ".mp4"
    return file_name


def get_type(url: str | None = "", path: str | None = "") -> MediaType | None:
    if url:
        media = get_filename_from_url(url)
    else:
        media = path
    name, ext = splitext(media)
    if ext in MediaExts.PHOTO:
        return MediaType.PHOTO
    if ext in MediaExts.VIDEO:
        return MediaType.VIDEO
    if ext in MediaExts.GIF:
        return MediaType.GIF
    if ext in MediaExts.AUDIO:
        return MediaType.AUDIO
    return MediaType.DOCUMENT


def get_tg_media_details(message: Message):
    match message.media:
        case MessageMediaType.PHOTO:
            file = message.photo
            file.file_name = "photo.jpg"
            return file
        case MessageMediaType.AUDIO:
            return message.audio
        case MessageMediaType.ANIMATION:
            return message.animation
        case MessageMediaType.DOCUMENT:
            return message.document
        case MessageMediaType.STICKER:
            return message.sticker
        case MessageMediaType.VIDEO:
            return message.video
        case MessageMediaType.VOICE:
            return message.voice
        case _:
            return
