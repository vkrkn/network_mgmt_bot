from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from app import bot, Message
import re

from app.models.base_model import Switch


class Text:
    start_message = '''
<b>Приветствую!</b>

Ваши данные:  
Telegram id: {telegram_id}
Роль: {role}

Для назначения роли пишите: @vkrkn
    '''
    help_for_readonly_users = '''
Для выбора коммутатора, введите его название либо ip-адрес. 
Пример: <b>10.102.170.97</b> либо <b>6-39</b>
    '''


@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    if bot.app_user.has_access_readonly():
        bot.send_message(
            bot.app_user.telegram_id,
            Text.start_message.format(telegram_id=bot.app_user.telegram_id, role=bot.app_user.role),
            reply_markup=ReplyKeyboardRemove()
        )
        bot.send_message(
            bot.app_user.telegram_id,
            Text.help_for_readonly_users
        )


