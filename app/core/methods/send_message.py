from io import BytesIO

from pyrogram import Client

from app.core.types.message import Message


class SendMessage(Client):
    async def send_message(
        self,
        chat_id: int | str,
        text,
        name: str = "output.txt",
        disable_web_page_preview: bool = False,
        **kwargs,
    ) -> Message:
        if not isinstance(text, str):
            text = str(text)
        if len(text) < 4096:
            message = await super().send_message(
                chat_id=chat_id,
                text=text,
                disable_web_page_preview=disable_web_page_preview,
                **kwargs,
            )
            return Message.parse(message=message)
        doc = BytesIO(bytes(text, encoding="utf-8"))
        doc.name = name
        return (await super().send_document(
            chat_id=chat_id, document=doc, **kwargs
        ))  # fmt: skip
