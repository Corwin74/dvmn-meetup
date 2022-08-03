import os
from dotenv import load_dotenv

from telegram import Update, LabeledPrice
from telegram.ext import CallbackContext
from telegram import LabeledPrice, Update


def make_donation(update: Update, context: CallbackContext):
    print(update)
    load_dotenv()
    PAYMENT_PROVIDER_TOKEN = os.getenv('PAYMENT_PROVIDER_TOKEN')

    query = update.callback_query
    chat_id = query.message.chat.id
    title = "Совершение платежа"
    description = "Для продолжения, нажмите кнопку Заплатить"
    payload = "Custom-Payload"
    currency = "USD"
    price = 5
    prices = [LabeledPrice("Test", price * 100)]

    context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        PAYMENT_PROVIDER_TOKEN,
        currency,
        prices
    )

    return 'GET_DONATION'


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


def successful_payment_callback(update: Update, context: CallbackContext) -> None:
    """Confirms the successful payment."""
    update.message.reply_text("Thank you for your payment!")
