import os

from telegram import Update, LabeledPrice
from telegram.ext import CallbackContext
from meetup.models import User, Donate


def ask_donation_amount(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите, пожалуйста, сумму доната:'
    )
    return 'MAKE_DONATION'


def make_donation(update: Update, context: CallbackContext):
    user_reply = update.message.text
    chat_id = update.effective_chat.id
    try:
        user_reply = int(user_reply)
    except ValueError:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Повторите ввод. {user_reply} не является числом.'
        )
        return 'MAKE_DONATION'

    provider_token = os.getenv('PAYMENT_PROVIDER_TOKEN')
    description = "Для продолжения, нажмите кнопку Заплатить"
    payload = "Custom-Payload"
    currency = "USD"
    price = user_reply
    prices = [LabeledPrice("Донат", price * 100)]
    title = "Совершаем платеж доната🤑"

    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices
    )

    return 'MAKE_DONATION'


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
