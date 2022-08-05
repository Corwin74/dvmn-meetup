import os

from dotenv import load_dotenv
from django.conf import settings
from django.core.management.base import BaseCommand

from telegram import Update
from telegram.ext import Filters, Updater, CallbackContext, PreCheckoutQueryHandler
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from meetup.models import User, Question, Donate, Event
from meet_schedule import event_details
from donation import precheckout_callback, successful_payment_callback

from core_bot_functions import (
    start,
    choose_action,
    check_data,
    get_company,
    get_email,
    get_name,
    get_networking,
    make_networking,
    get_position,
    get_info,
    show_event,
    handle_event,
    get_answer,
    answer_questions,
)
from speakers import (
    get_speaker,
    handle_speaker,
    get_question,
    send_question,
)
from networking import network_communicate, confirm_networking


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
        'GET_INFO': get_info,
        'CHECK_DATA': check_data,
        'GET_NETWORKING': get_networking,
        'CHOOSE_ACTION': choose_action,
        'SHOW_EVENT': show_event,
        'HANDLE_EVENT': handle_event,
        'GET_ANSWER': get_answer,
        'ANSWER_QUESTIONS': answer_questions,
        'EVENT_DETAILS': event_details,
        'GET_SPEAKER': get_speaker,
        'HANDLE_SPEAKER': handle_speaker,
        'GET_QUESTION': get_question,
        'SEND_QUESTION': send_question,
        'MAKE_NETWORKING': make_networking,
        'NETWORK_COMMUNICATE': network_communicate,
        'CONFIRM_NETWORKING': confirm_networking
    }

    state_handler = states_function[user_state]
    next_state = state_handler(update, context)
    context.bot_data['user'].tg_state = next_state
    context.bot_data['user'].save()


def main():
    load_dotenv()
    tg_token = settings.TG_TOKEN
    updater = Updater(tg_token)

    bot_commands = [
        ('start', 'Начать диалог')
    ]
    updater.bot.set_my_commands(bot_commands)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(user_input_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, user_input_handler))
    dispatcher.add_handler(CommandHandler('start', user_input_handler))
    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(MessageHandler(
        Filters.successful_payment, successful_payment_callback))

    updater.start_polling()
    updater.idle()
