from collections import deque
from logging import getLogger
from typing import Deque, Dict, Literal
from zoneinfo import ZoneInfo

from beanie import Document, after_event, before_event
from beanie.odm.actions import EventTypes
from pydantic import BaseModel, Field, PrivateAttr, field_validator, validator
from pymongo import ASCENDING, IndexModel
from pytz import all_timezones

logger = getLogger(__name__)


class BaseDocument(Document):
    tg_id: int
    tg_data: Dict

    @before_event(EventTypes.SAVE, EventTypes.SAVE_CHANGES)
    def before_save(self):
        logger.info(
            f"Saving {self.__class__.__name__}",
            extra={"tg_id": self.tg_id, "changes": self.get_previous_changes()},
        )

    @after_event(EventTypes.INSERT)
    def after_insert(self):
        logger.info(
            f"Created {self.__class__.__name__}",
            extra={"tg_id": self.tg_id, "model_dump": self.model_dump_json(indent=4)},
        )


class Message(BaseModel):
    tg_id: int
    tg_data: Dict

    text: str | None = None
    _caption: str | None = PrivateAttr(default=None)
    _image: bytes | None = PrivateAttr(default=None)
    _sticker: bytes | None = PrivateAttr(default=None)
    _audio: bytes | None = PrivateAttr(default=None)
    _voice: bytes | None = PrivateAttr(default=None)
    _document: bytes | None = PrivateAttr(default=None)

    is_new: bool | None = None


class User(BaseDocument):
    class Settings:
        name = "users"
        use_state_management = True
        state_management_save_previous = True
        indexes = [
            IndexModel(
                [("tg_id", ASCENDING)],
                unique=True,
                name="users.tg_id",
            ),
        ]


ChatEngineName = Literal["example_01"]


class ChatEngineConfig(BaseModel):
    new_message_processing_delay: float | None = None
    timezone: str | None = None


class Chat(BaseDocument):
    engine_config: ChatEngineConfig

    history: Deque[Message] = Field(default_factory=deque)

    class Settings:
        name = "chats"
        use_state_management = True
        state_management_save_previous = True
        indexes = [
            IndexModel(
                [("tg_id", ASCENDING)],
                unique=True,
                name="chats.tg_id",
            )
        ]
