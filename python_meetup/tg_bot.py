import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_meetup.settings')
django.setup()

from django.conf import settings

from dotenv import load_dotenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, PreCheckoutQueryHandler

from meetup.models import User, Question, Donut, Event


def start(update: Update, context: CallbackContext):
    user, created = User.objects.get_or_create(chat_id=update.message.chat_id)
    context.bot_data['user'] = user
    if created:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Привет'
        )
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Снова привет'
        )
    return 'START'


def user_input_handler(update: Update, context: CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query.data:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = context.bot_data.get('user').status

    states_function = {
        'START': start,
    }

    state_handler = states_function[user_state]
    next_state = state_handler(update, context)
    context.bot_data['user'].status = next_state


def main():
    load_dotenv()
    tg_token = os.getenv('TG_TOKEN')
    updater = Updater(tg_token)

    bot_commands = [
        ('start', 'Начать диалог')
    ]
    updater.bot.set_my_commands(bot_commands)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(user_input_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, user_input_handler))
    dispatcher.add_handler(CommandHandler('start', user_input_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
