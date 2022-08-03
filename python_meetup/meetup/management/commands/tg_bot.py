import os
import re

from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.utils import timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Update
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, PreCheckoutQueryHandler

from meetup.models import User, Question, Donut, Event


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()

def start(update: Update, context: CallbackContext):
    if not context.bot_data['user'].firstname:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='''Приветствуем в нашем чат-боте.
            Давайте познакомимся.
            Как вас зовут?
            (введите, пожалуйста, имя и фамилию через пробел)
            '''
        )
        return 'GET_NAME'
    elif context.bot_data['user'].status == 'SPEAKER':
        events = context.bot_data['user'].events.filter(finish_time__gte=timezone.now())
        print(events)
        keyboard = [
            [InlineKeyboardButton(f"{event.name} - {event.start_time.strftime('%H:%M')}", callback_data = str(event.id))]
            for event in events
        ]
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"""{context.bot_data['user']}, здравствуйте.
            Ваши предстоящие мероприятия:
            """,
            reply_markup = InlineKeyboardMarkup(keyboard)
        )
        return 'NEXT'


def get_name(update: Update, context: CallbackContext):
    keyboard = [
       [InlineKeyboardButton('Все верно', callback_data='confirmed')]
    ]
    if update.message:
        try:
            context.bot_data['firstname'], context.bot_data['lastname'] = update.message.text.split(' ', 1)
        except ValueError:
            context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите, пожалуйста, имя и фамилию через пробел'
            )
            return 'GET_NAME'
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f'''Ваше имя: {context.bot_data['firstname']}
            Ваша фамилия: {context.bot_data['lastname']}
            Нажмите кнопку, если все верно, или введите имя-фамилию заново''',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return 'GET_NAME'
    elif update.callback_query.data  == 'confirmed':
        context.bot_data['user'].firstname = context.bot_data['firstname']
        context.bot_data['user'].lastname = context.bot_data['lastname']
        context.bot_data['user'].save()
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text='Введите, пожалуйста, свой email'
        )
        return 'GET_EMAIL'

def get_email(update: Update, context: CallbackContext):
    user_reply = update.message.text
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", user_reply):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Введите, пожалуйста, корректный email'
        )
        return 'GET_EMAIL'
    context.bot_data['user'].email = user_reply
    context.bot_data['user'].save()
    return 'NEXT'



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
