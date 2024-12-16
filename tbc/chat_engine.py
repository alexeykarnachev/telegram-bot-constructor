import logging
from datetime import datetime, timedelta

from apscheduler.job import Iterable
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tbc.calendar import format_timestamp
from tbc.types import Chat, ChatEngineConfig, Message


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

        delay = self._config.new_message_processing_delay or 0.0
        run_date = datetime.now() + timedelta(seconds=delay)

        self._scheduler.add_job(
            self._tick,
            trigger="date",
            run_date=run_date,
            coalesce=True,
        )

        self._logger.info(f"Next chat engine tick is scheduled in {delay} s")

    async def _tick(self):
        prompt = _get_prompt(history=self._chat.history)


def _get_prompt(history: Iterable[Message], timezone: str | None = None):
    old_messages = []
    new_messages = []

    for message in history:
        msg = _format_message(message, timezone=timezone)

        if message.is_new:
            new_messages.append(msg)
        else:
            old_messages.append(msg)

    prompt = f"""
<legend>
You are an AI assistant.
</legend>

<tasks>
</tasks>

<old_messages>
Here are the old messages, which you are already saw.
Don't reply to them, but use them as a historical context if you need to.

{"\n".join(old_messages)}
</old_messages>

<new_messages>
Here are the new messages, you didn't see them yet.
You can reply to them if needed.

{"\n".join(new_messages)}
</new_messages>
""".strip()


def _format_message(message: Message, timezone: str | None = None):
    timestamp = format_timestamp(message.tg_data["date"], timezone=timezone)
    firstname = message.tg_data["from"]["first_name"]
    lastname = message.tg_data["from"].get("last_name", "")
    fullname = f"{firstname} {lastname}".strip()
    text = message.text or ""

    return f"[${timestamp} | ${fullname}] ${text}"
