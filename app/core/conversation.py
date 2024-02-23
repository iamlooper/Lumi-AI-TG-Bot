import asyncio
from collections import defaultdict
from typing import Self

from pyrogram import Client
from pyrogram.filters import Filter
from pyrogram.types import Message

from app.utils import Str


class Conversation(Str):
    CONVO_DICT: dict[int, list["Conversation"]] = defaultdict(list)

    class DuplicateConvo(Exception):
        def __init__(self, chat: str | int):
            super().__init__(f"Conversation already started with {chat} ")

    def __init__(
        self,
        client: Client,
        chat_id: int | str,
        check_for_duplicates: bool = True,
        filters: Filter | None = None,
        timeout: int = 10,
    ):
        self.chat_id: int | str = chat_id
        self._client: Client = client
        self.check_for_duplicates: bool = check_for_duplicates
        self.filters: Filter = filters
        self.response_future: asyncio.Future | None = None
        self.responses: list[Message] = []
        self.timeout: int = timeout
        self.set_future()

    async def __aenter__(self) -> Self:
        """
        Convert Username to ID if chat_id is username.
        Check Convo Dict for duplicate Convo with same ID.
        Initialize Context Manager and return the Object.
        """
        if isinstance(self.chat_id, str):
            self.chat_id = (await self._client.get_chat(self.chat_id)).id
        if self.check_for_duplicates and self.chat_id in Conversation.CONVO_DICT.keys():
            raise self.DuplicateConvo(self.chat_id)
        Conversation.CONVO_DICT[self.chat_id].append(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit Context Manager and remove Chat ID from Dict."""
        Conversation.CONVO_DICT[self.chat_id].remove(self)
        if not self.response_future.done():
            self.response_future.cancel()
        if not Conversation.CONVO_DICT[self.chat_id]:
            Conversation.CONVO_DICT.pop(self.chat_id)

    @classmethod
    async def get_resp(cls, client, *args, **kwargs) -> Message | None:
        """
        Bound Method to Gracefully handle Timeout.
        but only returns first Message.
        """
        try:
            async with cls(*args, client=client, **kwargs) as convo:
                response: Message | None = await convo.get_response()
                return response
        except TimeoutError:
            return

    def set_future(self, *args, **kwargs):
        future = asyncio.Future()
        future.add_done_callback(self.set_future)
        self.response_future = future

    """Methods"""

    async def get_response(self, timeout: int = 0) -> Message | None:
        """Returns Latest Message for Specified Filters."""
        try:
            response: asyncio.Future.result = await asyncio.wait_for(
                fut=self.response_future, timeout=timeout or self.timeout
            )
            return response
        except asyncio.TimeoutError:
            raise TimeoutError("Conversation Timeout")

    async def send_message(
        self,
        text: str,
        timeout: int = 0,
        get_response: bool = False,
        **kwargs,
    ) -> Message | tuple[Message, Message]:
        """
        Bound Method to Send Texts in Convo Chat.
        Returns Sent Message and Response if get_response is True.
        """
        message = await self._client.send_message(
            chat_id=self.chat_id, text=text, **kwargs
        )
        if get_response:
            response = await self.get_response(timeout=timeout)
            return message, response
        return message

    async def send_document(
        self,
        document,
        caption: str = "",
        timeout: int = 0,
        get_response: bool = False,
        force_document: bool = True,
        **kwargs,
    ) -> Message | tuple[Message, Message]:
        """
        Bound Method to Send Documents in Convo Chat.
        Returns Sent Message and Response if get_response is True.
        """
        message = await self._client.send_document(
            chat_id=self.chat_id,
            document=document,
            caption=caption,
            force_document=force_document,
            **kwargs,
        )
        if get_response:
            response = await self.get_response(timeout=timeout)
            return message, response
        return message
