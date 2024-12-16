import logging
from typing import Any


def configure_logging(**tags: Any) -> None:
    def get_console_handler() -> logging.StreamHandler:
        tag_str = " ".join(f"{k}={v}" for k, v in tags.items())
        format = (
            f"%(asctime)s - %(name)s - %(levelname)s - %(message)s - tags: [{tag_str}]"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format))
        return handler

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(get_console_handler())

    for module in [
        "httpx",
        "httpcore",
        "telegram",
        "together",
        "apscheduler",
        "anthropic",
        "pymongo",
        "requests",
        "urllib3",
        "PIL",
        "asyncio",
    ]:
        logging.getLogger(module).setLevel(logging.ERROR)
