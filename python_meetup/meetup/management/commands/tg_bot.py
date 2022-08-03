import os
import re

from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.utils import timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Filters, Updater, CallbackContext
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from meetup.models import User, Question, Donut, Event
from .meet_schedule import show_program


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()

def start(update: Update, context: CallbackContext):
    if context.bot_data['user'].status == 'PARTICIPANT':
        keyboard = [
            [InlineKeyboardButton('Программа', callback_data='show_program')],
            [InlineKeyboardButton('Спикеры', callback_data='show_speakers')],
            [InlineKeyboardButton('Нетворкинг', callback_data='networking')],
            [InlineKeyboardButton('Задонатить', callback_data='make_donation')],
        ]
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='''Приветствуем на нашем митапе.
            Хотите посмотреть программу, задать вопросы спикерам, поучаствовать в нетворкинге или задонатить?
            ''',
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'CHOOSE_ACTION'

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


def choose_action(update: Update, context: CallbackContext):
    response = update.callback_query.data
    if response == 'show_program':
        return show_program(update, context)
    elif response == 'show_speakers':
        return show_speakers(update, context)
    elif response == 'networking':
        return get_networking(update, context)
    elif response == 'make_donation':
        return make_donation(update, context)


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
    elif update.callback_query.data == 'confirmed':
        context.bot_data['user'].firstname = context.bot_data['firstname']
        context.bot_data['user'].lastname = context.bot_data['lastname']
        context.bot_data['user'].save()
        keyboard = [
            [InlineKeyboardButton('Да', callback_data='yes'), InlineKeyboardButton('Нет', callback_data='no')]
        ]
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text='Хотите ли вы участвовать в нетворкинге и общаться с другими участниками?',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return 'GET_NETWORKING'


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
    context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Укажите, пожалуйста, название компании, которую вы представляете'
        )
    return 'GET_COMPANY'


def get_company(update: Update, context: CallbackContext):
    user_reply = update.message.text
    context.bot_data['user'].company = user_reply
    context.bot_data['user'].save()
    context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Укажите, пожалуйста, вашу должность в компании'
        )
    return 'GET_POSITION'


def get_position(update: Update, context: CallbackContext):
    user_reply = update.message.text
    context.bot_data['user'].position = user_reply
    context.bot_data['user'].save()
    keyboard = [
        [InlineKeyboardButton('Да. Начнем общаться', callback_data='yes'), InlineKeyboardButton('Нет, хочу поправить', callback_data='no')]
    ]
    context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"""Вы работаете в компании {context.bot_data['user'].company} на должности {context.bot_data['user'].position}
            Ваш email - {context.bot_data['user'].email}
            Все верно?""",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    return 'CHECK_DATA'


def check_data(update: Update, context: CallbackContext):
    if update.callback_query.data == 'no':
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Введите свой email"
        )
        return 'GET_EMAIL'
    context.bot_data['user'].networking = True
    context.bot_data['user'].save()
    if User.objects.filter(networking=True).count() > 1:
        keyboard = [
            [InlineKeyboardButton('Программа', callback_data='show_program')],
            [InlineKeyboardButton('Спикеры', callback_data='show_speakers')],
            [InlineKeyboardButton('Нетворкинг', callback_data='networking')],
            [InlineKeyboardButton('Задонатить', callback_data='make_donation')],
        ]
        text = 'Отлично. Приглашаем к нам на митап'
    else:
        keyboard = [
            [InlineKeyboardButton('Программа', callback_data='show_program')],
            [InlineKeyboardButton('Спикеры', callback_data='show_speakers')],
            [InlineKeyboardButton('Задонатить', callback_data='make_donation')]
        ]
        text = '''В нетворкинге вы пока первый, но скоро появятся новые собеседники.
        Пока же можете посмотреть программу, задать вопросы спикерам или задонатить организаторам
        '''
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return 'CHOOSE_ACTION'


def get_networking(update: Update, context: CallbackContext):
    if update.callback_query.data == 'no':
        keyboard = [
            [InlineKeyboardButton('Программа', callback_data='show_program')],
            [InlineKeyboardButton('Спикеры', callback_data='show_speakers')],
            [InlineKeyboardButton('Задонатить', callback_data='make_donation')]
        ]
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text='В таком случае предлагаем ознакомиться с программой, написать спикеру или задонатить организаторам',
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return 'CHOOSE_ACTION'
    context.bot.send_message(
        chat_id=update.callback_query.message.chat_id,
        text="""Чтобы участвовать в нетворкинге, оставьте, пожалуйста, дополнительную информацию о себе
        Введите свой email"""
    )
    return 'GET_EMAIL'


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
