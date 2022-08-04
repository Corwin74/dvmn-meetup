from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from meetup.models import Event


def show_program(update: Update, context: CallbackContext):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    events = Event.objects.all()
    keyboard = [
        [InlineKeyboardButton(f"{event.name} - {event.start_time.strftime('%H:%M')}",
         callback_data = str(event.id))]
         for event in events
    ] + [[InlineKeyboardButton('В начало', callback_data='to_start')]]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Программа мероприятий:',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'SHOW_EVENT'
