from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from meetup.models import Event
from core_bot_functions import start


def event_details(update: Update, context: CallbackContext):
    query = update.callback_query

    # CallbackQueries need to be answered,
    # even if no notification to the user is needed
    # Some clients may have trouble otherwise.
    # See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    if update.callback_query.data == 'to_start':
        return start(update, context)

    keyboard = [[InlineKeyboardButton('Назад', callback_data='show_program')]]
    event_id = int(update.callback_query.data)
    event = Event.objects.get(id=event_id)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text= f'{event.name}\n'
              f'{event.start_time.strftime("%d %B   %H:%M")} - '
              f'{event.finish_time.strftime("%H:%M")}\n'
              f'Спикер: {event.speaker}\n'
              f'{event.description}',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'CHOOSE_ACTION'
