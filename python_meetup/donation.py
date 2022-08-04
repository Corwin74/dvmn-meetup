import os

from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from meetup.models import User, Donate


def make_donation(update: Update, context: CallbackContext):
    query = update.callback_query
    provider_token = os.getenv('PAYMENT_PROVIDER_TOKEN')
    chat_id = query.message.chat.id
    description = "Для продолжения, нажмите кнопку Заплатить"
    payload = "Custom-Payload"
    currency = "USD"
    price = 5
    prices = [LabeledPrice("Донат", price * 100)]
    title = "Совершаем платеж доната"

    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices
    )

    return 'GET_DONATION'


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    tg_nick = update.message.chat.username
    receipt = update.message.successful_payment
    donated_user = User.objects.get(tg_nick=tg_nick)
    donate = Donate(
        user=donated_user,
        amount=receipt.total_amount
    )
    donate.save()
    update.message.reply_text("Спасибо за ваш платеж!")
