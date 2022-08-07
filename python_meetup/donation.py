import os

from telegram import Update, LabeledPrice
from telegram.ext import CallbackContext
from meetup.models import User, Donate
from core_bot_functions import start, ask_donation


def make_donation(update: Update, context: CallbackContext, price=500):
    if update.callback_query:
        if update.callback_query.data == 'start':
            return start(update. context)
        else:
            price = int(update.callback_query.data)
    elif update.message:
        try:
            price = int(update.message.text)
        except ValueError:
            return ask_donation(update, context, text='Введите корректную сумму доната не менее 100 рублей')
    provider_token = os.getenv('PAYMENT_PROVIDER_TOKEN')
    chat_id = update.effective_chat.id
    description = "Для продолжения, нажмите кнопку Заплатить"
    payload = "Custom-Payload"
    currency = "RUB"
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
    return 'START'


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


def successful_payment_callback(update: Update, context: CallbackContext):
    tg_nick = update.message.chat.username
    receipt = update.message.successful_payment
    donated_user = User.objects.get(tg_nick=tg_nick)
    donate = Donate(
        user=donated_user,
        amount=receipt.total_amount/100
    )
    donate.save()
    return start(update, context, text='Спасибо за Ваш платеж!')
