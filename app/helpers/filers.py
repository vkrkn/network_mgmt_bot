from telebot import custom_filters
from app import bot


class IsReadOnly(custom_filters.SimpleCustomFilter):
    key = 'is_role'

    @staticmethod
    def check(message):
        print(message)
        return str(bot.app_user.role)
