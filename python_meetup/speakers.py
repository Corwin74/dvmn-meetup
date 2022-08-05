from textwrap import dedent

from django.utils import timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Filters, Updater, CallbackContext

from core_bot_functions import start, show_speakers
from meetup.models import User, Question, Donate, Event


def get_speaker(update: Update, context: CallbackContext):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    speaker_id = int(update.callback_query.data)
    context.bot_data['speaker'] = User.objects.get(id=speaker_id)
    events = context.bot_data['speaker'].events.all()
    text = dedent(f"""
    <b>{context.bot_data['speaker']}</b>
    {context.bot_data['speaker'].position} в {context.bot_data['speaker'].company}
    {context.bot_data['speaker'].info}
    <u>Выступает</u>
    """) + "\n".join([f"{event.start_time.strftime('%d %B %H:%M')} - {event.name}" for event in events])
    keyboard = [
        [InlineKeyboardButton('Задать вопрос', callback_data=str(context.bot_data['speaker'].id))],
        [InlineKeyboardButton('Назад', callback_data='back'), InlineKeyboardButton('Главное меню', callback_data='to_start')],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'HANDLE_SPEAKER'


def handle_speaker(update: Update, context: CallbackContext, speaker=None, event_id=None):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    elif update.callback_query.data == 'back':
        return show_speakers(update, context)
    keyboard = [
        [InlineKeyboardButton('Назад', callback_data=event_id or 'back')],
        [InlineKeyboardButton('Главное меню', callback_data='to_start')],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent(f"""
        Напишите свой вопрос ниже.
        {context.bot_data['speaker']} сможет ответить вам через этот чат"""),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'GET_QUESTION'


def get_question(update: Update, context: CallbackContext):
    if update.callback_query:
        if update.callback_query.data == 'to_start':
            return start(update, context)
        elif update.callback_query.data == 'back':
            return show_speakers(update, context)            
    question = update.message.text
    keyboard = [
        [InlineKeyboardButton('Верно, отправляйте', callback_data=question), InlineKeyboardButton('Изменить', callback_data='correct')],
        [InlineKeyboardButton('Главное меню', callback_data='to_start')],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent(f"""
        Ваш вопрос {context.bot_data['speaker']}:
        {question}
        Все верно?
        """),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'SEND_QUESTION'


def send_question(update: Update, context: CallbackContext):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    elif update.callback_query.data == 'correct':
        return handle_speaker(update, context)
    Question.objects.create(
        text=update.callback_query.data,
        asker=context.bot_data['user'],
        answerer=context.bot_data['speaker']
    )
    update.callback_query.answer(text="Вопрос отправлен")
    return start(update, context)
