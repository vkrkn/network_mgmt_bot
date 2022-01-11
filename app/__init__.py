import os
import logging

from telebot import TeleBot, apihelper
from telebot.types import Message, Update

from dotenv import load_dotenv
from pathlib import Path

from app.helpers.enums import AppState

load_dotenv()
APP_DIR = Path(__file__).resolve().parent

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(int(os.getenv('LOG_LEVEL')))
file_handler = logging.FileHandler(APP_DIR / 'log.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# инициализация pytelegrambotapi
apihelper.ENABLE_MIDDLEWARE = True
bot = TeleBot(os.getenv("TOKEN"), parse_mode="HTML")


def application():
    from app.models.base_model import Role
    from app.models.base_model import User
    from app.helpers.filers import IsReadOnly

    @bot.middleware_handler()
    def auth(bot_instance, update: Update):
        if update.__dict__.get('message') is not None:
            message = update.message
        else:
            message = update.edited_message

        telegram_id = message.from_user.id
        fullname = f"{message.from_user.first_name} {message.from_user.last_name}"
        bot_instance.app_user = User.get_or_create(telegram_id=telegram_id, name=fullname)[0]
        logger.info(f"Получение модели пользователя {bot_instance.app_user}")

    from app.handlers.start import start_handler
    from app.handlers.text import text_handler

    bot.add_custom_filter(IsReadOnly())
    bot.infinity_polling()
