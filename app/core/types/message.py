import asyncio
from functools import cached_property
from typing import Self

from pyrogram.enums import MessageEntityType
from pyrogram.errors import MessageDeleteForbidden
from pyrogram.filters import Filter
from pyrogram.types import Message as Msg
from pyrogram.types import User

from app import Config
from app.core.conversation import Conversation


class Message(Msg):
    def __init__(self, message: Msg | Self) -> None:
        kwargs = self.sanitize_message(message)
        super().__init__(**kwargs)

    @cached_property
    def cmd(self) -> str | None:
        if not self.text_list:
            return
        raw_cmd = self.text_list[0]
        cmd = raw_cmd.replace(self.trigger, "", 1)
        return cmd if cmd in Config.CMD_DICT.keys() else None

    @cached_property
    def flags(self) -> list:
        return [i for i in self.text_list if i.startswith("-")]

    @cached_property
    def flt_input(self) -> str:
        split_lines = self.input.split(sep="\n", maxsplit=1)
        split_lines[0] = " ".join(
            [word for word in split_lines[0].split(" ") if word not in self.flags]
        )
        return "\n".join(split_lines)

    @cached_property
    def input(self) -> str:
        if len(self.text_list) > 1:
            return self.text.split(maxsplit=1)[-1]
        return ""

    @cached_property
    def replied(self) -> "Message":
        if self.reply_to_message:
            return Message.parse(self.reply_to_message)

    @cached_property
    def reply_id(self) -> int | None:
        return self.replied.id if self.replied else None

    @cached_property
    def replied_task_id(self) -> str | None:
        return self.replied.task_id if self.replied else None

    @cached_property
    def reply_text_list(self) -> list:
        return self.replied.text_list if self.replied else []

    @cached_property
    def task_id(self) -> str:
        return f"{self.chat.id}-{self.id}"

    @cached_property
    def text_list(self) -> list:
        return self.text.split() if self.text else []

    @cached_property
    def trigger(self):
        return Config.TRIGGER

    @cached_property
    def unique_chat_user_id(self):
        return f"{self.chat.id}-{self.from_user.id}"

    async def async_deleter(self, del_in, task, block) -> None:
        if block:
            x = await task
            await asyncio.sleep(del_in)
            await x.delete()
            return x
        else:
            asyncio.create_task(
                self.async_deleter(del_in=del_in, task=task, block=True)
            )

    async def delete(self, reply: bool = False) -> None:
        try:
            await super().delete()
            if reply and self.replied:
                await self.replied.delete()
        except MessageDeleteForbidden:
            pass

    async def edit(
        self, text, del_in: int = 0, block=True, name: str = "output.txt", **kwargs
    ) -> "Message":
        if len(str(text)) < 4096:
            task = super().edit_text(text=text, **kwargs)
            if del_in:
                reply = await self.async_deleter(task=task, del_in=del_in, block=block)
            else:
                reply = Message.parse((await task))  # fmt:skip
            self.text = reply.text
        else:
            _, reply = await asyncio.gather(
                super().delete(), self.reply(text, name=name, **kwargs)
            )
        return reply

    async def extract_user_n_reason(self) -> tuple[User | str | Exception, str | None]:
        if self.replied:
            return self.replied.from_user, self.flt_input
        input_text_list = self.flt_input.split(maxsplit=1)
        if not input_text_list:
            return (
                "Unable to Extract User info.\nReply to a user or input @ | id.",
                None,
            )
        user = input_text_list[0]
        reason = None
        if len(input_text_list) >= 2:
            reason = input_text_list[1]
        if self.entities:
            for entity in self.entities:
                if entity == MessageEntityType.MENTION:
                    return entity.user, reason
        if user.isdigit():
            user = int(user)
        elif user.startswith("@"):
            user = user.strip("@")
        try:
            return (await self._client.get_users(user_ids=user)), reason
        except Exception:
            return user, reason

    async def get_response(self, filters: Filter = None, timeout: int = 8):
        response: Message | None = await Conversation.get_resp(
            client=self._client, chat_id=self.chat.id, filters=filters, timeout=timeout
        )
        return response

    async def log(self):
        return (await self.copy(Config.LOG_CHAT))  # fmt:skip

    async def reply(
        self, text, del_in: int = 0, block: bool = True, **kwargs
    ) -> "Message":
        task = self._client.send_message(
            chat_id=self.chat.id, text=text, reply_to_message_id=self.id, **kwargs
        )
        if del_in:
            await self.async_deleter(task=task, del_in=del_in, block=block)
        else:
            return Message.parse((await task))  # fmt:skip

    @staticmethod
    def sanitize_message(message):
        kwargs = vars(message).copy()
        kwargs["client"] = kwargs.pop("_client", message._client)
        [
            kwargs.pop(arg, 0)
            for arg in dir(Message)
            if (
                isinstance(getattr(Message, arg, 0), (cached_property, property))
                and not hasattr(Msg, arg)
            )
        ]
        return kwargs

    @classmethod
    def parse(cls, message: Msg) -> "Message":
        return cls(message)
