import time

from pyrogram.types import Message, User

from app.utils.media_helper import bytes_to_mb

PROGRESS_DICT = {}


def get_name(user: User) -> str:
    first = user.first_name or ""
    last = user.last_name or ""
    return f"{first} {last}".strip()


def extract_user_data(user: User) -> dict:
    return dict(name=get_name(user), username=user.username, mention=user.mention)


async def progress(
    current: int,
    total: int,
    response: Message | None = None,
    action: str = "",
    file_name: str = "",
    file_path: str = "",
):
    if not response:
        return
    if current == total:
        PROGRESS_DICT.pop(file_path, "")
        return
    current_time = time.time()
    if file_path not in PROGRESS_DICT or (current_time - PROGRESS_DICT[file_path]) > 5:
        PROGRESS_DICT[file_path] = current_time
        if total:
            percentage = round((current * 100 / total), 1)
        else:
            percentage = 0
        await response.edit(
            f"<b>{action}</b>"
            f"\n<pre language=bash>"
            f"\nfile={file_name}"
            f"\npath={file_path}"
            f"\nsize={bytes_to_mb(total)}mb"
            f"\ncompleted={bytes_to_mb(current)}mb | {percentage}%</pre>"
        )
