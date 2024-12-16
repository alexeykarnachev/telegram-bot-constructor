import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tbc.state import Chat, ChatEngineConfig, Message


class ChatEngine:
    def __init__(self, chat: Chat, config: ChatEngineConfig):
        self._chat = chat
        self._config = config

        self._scheduler = AsyncIOScheduler()
        self._scheduler.start()

        logger = logging.getLogger(__name__).getChild(self.__class__.__name__)
        self._logger = logger

    async def notice_new_message(self, message: Message):
        if message.is_new is not None:
            raise ValueError("The message has already been noticed")

        message.is_new = True
        self._chat.history.append(message)
        await self._chat.save()

        self._scheduler.add_job(
            self._process_new_messages,
            trigger="date",
            run_date=datetime.now()
            + timedelta(seconds=self._config.new_message_processing_delay),
            coalesce=True,
        )

    async def _process_new_messages(self):
        history = self._chat.history

