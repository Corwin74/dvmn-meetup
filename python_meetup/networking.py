import random

from textwrap import dedent

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from core_bot_functions import start, get_user_info, get_networking
from meetup.models import User


def confirm_networking(update: Update, context: CallbackContext):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    elif update.callback_query.data == 'confirm':
        context.bot_data['user'].networking = True
        context.bot_data['user'].save()
        return get_networking(update, context)


def network_communicate(update: Update, context: CallbackContext):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    if update.callback_query.data == 'change_info':
        return get_user_info(update, context)
    if update.callback_query.data == 'cancel_networking':
        context.bot_data['user'].networking = False
        context.bot_data['user'].save()
        return start(update, context)
    context.bot_data['networking_connection'] = context.bot_data['user']
    while context.bot_data['networking_connection'] == context.bot_data['user']:
        context.bot_data['networking_connection'] = random.choice(
            User.objects.filter(networking=True)
        )
        print(context.bot_data['networking_connection'])
    keyboard = [
        [InlineKeyboardButton('Следующий контакт', callback_data='next_contact')],
        [InlineKeyboardButton('Главное меню', callback_data='to_start')]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent(f"""
        <strong>{context.bot_data['networking_connection']}</strong>
        {context.bot_data['networking_connection'].position} в {context.bot_data['networking_connection'].company}
        {context.bot_data['networking_connection'].info}
        Связаться в Telegram:
        <tg-spoiler>@{context.bot_data['networking_connection'].tg_nick}</tg-spoiler>
        """),
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'NETWORK_COMMUNICATE'
