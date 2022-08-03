from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext


def show_program(update: Update, context: CallbackContext):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")
    context.bot.send_message(
            chat_id=update.callback_query.from_user.id,
            text='Программа мероприятий:\n1. Спикер: Вася Пупкин "Телеграмм-боты"\n2. Нетворкинг'
        )
    return 'START'
