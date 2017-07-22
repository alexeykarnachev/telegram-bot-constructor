# Telegram Bot Constructor

## What is this?
This is the Python package for an easy-way declarative development
of a Telegram bots. Telegram Bot Constructor (tbc) remembers users' states
within SQL database. In this way, each user's request (pressed button,
message or other input) processed individually. The tbc provides to
developer some kind of the
[MVC](https://ru.wikipedia.org/wiki/Model-View-Controller) instrumentation.
* **Model** (M) component is implemented using the great Python package
[transitions](https://github.com/pytransitions/transitions) (for the
states switching) and
[SQLAlchemy](https://www.sqlalchemy.org/) (for the data manipulations)
* **View** (V) component as a matter of fact is a Telegram-python
interface:
[python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot),
which provides bot's buttons visualization, bot's replies sending and so on
* **Controller** (C) component is also partially the python-telegram-bot
instrumentation (for the receiving user's inputs) and custom handlers
(for the interaction with model)

## Installation
Clone the repo from GitHub and then:<br>
`python setup.py install`

#### Preparation
Telegram api token could be obtained within the [@BotFather](https://telegram.me/botfather).
So, you should go to Telegram and start chat with bot father. Then just follow extremely easy
instruction, provided by @BotFather.<br>
Since we have the idea of the bot structure and token obtained from bot father, we can start to code the
blockchain explorer bot.