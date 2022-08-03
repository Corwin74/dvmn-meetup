import os
import re

from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.utils import timezone

from telegram import Update
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from meetup.models import User, Question, Donut, Event
from meet_schedule import show_program
from donation import make_donation

from core_bot_functions import (
    start,
    choose_action,
    check_data,
    get_company,
    get_email,
    get_name,
    get_networking,
    get_position,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()


def user_input_handler(update: Update, context: CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        username = update.message.from_user.username
    elif update.callback_query.data:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
        username = update.callback_query.from_user.username
    else:
        return
    print(username)
    user, created = User.objects.get_or_create(
        tg_nick=username,
        defaults={
            'chat_id': chat_id,
        }
    )
    context.bot_data['user'] = user
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = user.tg_state

    states_function = {
        'START': start,
        'GET_NAME': get_name,
        'GET_EMAIL': get_email,
        'GET_COMPANY': get_company,
        'GET_POSITION': get_position,
        'CHECK_DATA': check_data,
        'GET_NETWORKING': get_networking,
        'CHOOSE_ACTION': choose_action,
    }

    state_handler = states_function[user_state]
    next_state = state_handler(update, context)
    context.bot_data['user'].tg_state = next_state
    context.bot_data['user'].save()


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
