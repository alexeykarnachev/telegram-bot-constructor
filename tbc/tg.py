import asyncio
import logging
from typing import cast

import telegram as tg
import telegram.ext as te
from beanie import init_beanie

from tbc.chat_engine import ChatEngine
from tbc.settings import settings
from tbc.types import Chat, Message, User


class App:
    def __init__(self) -> None:
        self._tg_app = (
            te.ApplicationBuilder()
            .token(settings.tg_token.get_secret_value())  # type: ignore
            .concurrent_updates(True)
            .connect_timeout(60.0)
            .build()
        )

        self._tg_app.add_handler(
            te.MessageHandler(
                te.filters.USER & te.filters.UpdateType.MESSAGE, self._before_update
            ),
            group=-1,
        )
        self._tg_app.add_handler(
            te.MessageHandler(
                te.filters.USER & te.filters.UpdateType.MESSAGE,
                self._handle_user_message,
            )
        )
        self._tg_app.add_error_handler(self._handle_error)

        self._logger = logging.getLogger(__name__)

    def run(self):
        self._logger.debug("Trying to connect to MongoDB")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            init_beanie(
                connection_string=settings.mongodb_uri.get_secret_value(),  # type: ignore
                document_models=[User, Chat],
            )
        )
        asyncio.set_event_loop(loop)
        self._logger.info("Successfully connected to MongoDB")

        self._logger.info("Polling messages")
        self._tg_app.run_polling()

    async def _before_update(
        self,
        tg_update: tg.Update,
        tg_context: te.ContextTypes.DEFAULT_TYPE,
    ):
        self._logger.debug("_before_update")

        tg_chat_id = tg_update.effective_chat.id  # type: ignore
        tg_chat_data = tg_update.effective_chat.to_dict()  # type: ignore
        chat: Chat | None = await Chat.find_one({"tg_id": tg_chat_id})

        if chat is None:
            tg_user_id = tg_update.effective_user.id  # type: ignore
            tg_user_data = tg_update.effective_user.to_dict()  # type: ignore
            user = await User.find_one({"tg_id": tg_user_id})
            if user is None:
                user = User(tg_id=tg_user_id, tg_data=tg_user_data)
                user = await user.insert()

            chat = Chat(
                tg_id=tg_chat_id,
                tg_data=tg_chat_data,
                engine_config=settings.chat_engine_config,  # type: ignore
            )

            await chat.insert()

        if "engine" not in tg_context.chat_data:  # type: ignore
            tg_context.chat_data["engine"] = ChatEngine(chat, settings.chat_engine_config)  # type: ignore

    async def _handle_user_message(
        self,
        tg_update: tg.Update,
        tg_context: te.ContextTypes.DEFAULT_TYPE,
    ):
        self._logger.debug("_handle_user_message")

        engine: ChatEngine = tg_context.chat_data["engine"]  # type: ignore
        message = await self._get_message_from_tg_update(tg_update)
        await engine.notice_new_message(message)

    async def _handle_error(self, _: object, tg_context: te.ContextTypes.DEFAULT_TYPE):
        self._logger.error(
            "Exception while handling an update:", exc_info=tg_context.error
        )

    async def _get_message_from_tg_update(self, tg_update: tg.Update) -> Message:
        tg_message = cast(tg.Message, tg_update.message)

        async def _try_download_tg_file(tg_file):
            if tg_file is None:
                return None

            try:
                tg_bot = tg_update.get_bot()
                file = await tg_bot.get_file(tg_file.file_id)
                self._logger.info(f"Downloading file from telegram: {file}")
                data = bytes(await file.download_as_bytearray())
                return data
            except:
                self._logger.exception(f"Failed to download file from telegram:")

        async def _download_tg_photo(tg_photo):
            tg_file = tg_photo[-1] if tg_photo else None
            return await _try_download_tg_file(tg_file)

        message = Message(
            tg_id=tg_message.id,
            tg_data=tg_message.to_dict(),
            text=tg_message.text,
        )

        message._caption = tg_message.caption
        message._image = await _download_tg_photo(tg_message.photo)
        message._sticker = await _try_download_tg_file(tg_message.sticker)
        message._audio = await _try_download_tg_file(tg_message.audio)
        message._voice = await _try_download_tg_file(tg_message.voice)
        message._document = await _try_download_tg_file(tg_message.document)

        self._logger.info(
            "Message constructed from telegram update",
            extra={"message_dump": message.model_dump()},
        )

        return message
