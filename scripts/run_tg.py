from logging import getLogger

from tbc.logs import configure_logging
from tbc.tg import App

configure_logging(app="tbc")

logger = getLogger(__name__)


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
