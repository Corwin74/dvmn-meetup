import random
import re

from textwrap import dedent

from django.utils import timezone

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from meetup.models import User, Event


def start(update: Update, context: CallbackContext, text='''Приветствуем на нашем митапе!'''):
    keyboard = [
        [InlineKeyboardButton('Мои мероприятия', callback_data='personal_program')] if context.bot_data['user'].status == 'SPEAKER' else [],
        [InlineKeyboardButton('Вопросы ко мне', callback_data='my_questions')] if context.bot_data['user'].status == 'SPEAKER' else [],
        [InlineKeyboardButton('Программа', callback_data='show_program'), InlineKeyboardButton('Спикеры', callback_data='show_speakers')],
        [InlineKeyboardButton('Нетворкинг', callback_data='networking'), InlineKeyboardButton('Задонатить', callback_data='make_donation')],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    message = update.effective_message
    if message:
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
    return 'CHOOSE_ACTION'


def choose_action(update: Update, context: CallbackContext):
    response = update.callback_query.data
    if response == 'show_program':
        return show_program(update, context)
    elif response == 'show_speakers':
        return show_speakers(update, context)
    elif response == 'networking':
        return get_networking(update, context)
    elif response == 'make_donation':
        return ask_donation(update, context)
    elif response == 'personal_program':
        return get_personal_events(update, context)
    elif response == 'my_questions':
        return get_questions(update, context)


def get_personal_events(update: Update, context: CallbackContext):
    events = context.bot_data['user'].events.filter(finish_time__gte=timezone.now())
    keyboard = [
        [InlineKeyboardButton(f"{event.name} - {event.start_time.strftime('%H:%M')}", callback_data=str(event.id))]
        for event in events
    ] + [[InlineKeyboardButton('Главное меню', callback_data='to_start')]]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Ваши мероприятия',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'SHOW_EVENT'


def show_event(update: Update, context: CallbackContext):
    if update.callback_query.data == 'to_start':
        return start(update, context)
    event_id = int(update.callback_query.data)
    event = Event.objects.get(id=event_id)
    text = dedent(f"""
    <b>{event.name}</b>
    Начало - {event.start_time.strftime('%d %B %H:%M')}
    """)
    keyboard = [[InlineKeyboardButton('Назад', callback_data='back')]]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'HANDLE_EVENT'


def handle_event(update: Update, context: CallbackContext):
    if update.callback_query.data == 'back':
        return get_personal_events(update, context)
    return 'HANDLE_EVENT'


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
            chat_id=update.effective_chat.id,
            text=dedent(f'''
            Ваше имя: <b>{context.bot_data['firstname']}</b>
            Ваша фамилия: <b>{context.bot_data['lastname']}</b>
            Нажмите кнопку, если все верно, или введите имя-фамилию заново'''),
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        message = update.effective_message
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
        return 'GET_NAME'
    elif update.callback_query.data == 'confirmed':
        context.bot_data['user'].firstname = context.bot_data['firstname']
        context.bot_data['user'].lastname = context.bot_data['lastname']
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Введите свой email',
        )
        message = update.effective_message
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
        return 'GET_EMAIL'


def get_email(update: Update, context: CallbackContext):
    user_reply = update.message.text
    if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", user_reply):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Введите, пожалуйста, корректный email'
        )
        message = update.effective_message
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
        return 'GET_EMAIL'
    context.bot_data['user'].email = user_reply
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Укажите, пожалуйста, название компании, которую вы представляете'
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'GET_COMPANY'


def get_company(update: Update, context: CallbackContext):
    user_reply = update.message.text
    context.bot_data['user'].company = user_reply
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Укажите, пожалуйста, вашу должность в компании'
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'GET_POSITION'


def get_position(update: Update, context: CallbackContext):
    user_reply = update.message.text
    context.bot_data['user'].position = user_reply
    keyboard = [[InlineKeyboardButton('Продолжить', callback_data='continue')]]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent("""
        Если хотите добавить дополнительную информацию о себе, то напишите ее в ответном сообщении.
        Либо нажмите 'Продолжить'"""),
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'GET_INFO'


def get_info(update: Update, context: CallbackContext):
    if update.message:
        context.bot_data['user'].info = update.message.text
    else:
        context.bot_data['user'].info = ''
    keyboard = [
        [InlineKeyboardButton('Да. Начнем общаться', callback_data='yes'), InlineKeyboardButton('Нет, хочу поправить', callback_data='no')]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent(f"""
        Вы работаете в компании {context.bot_data['user'].company} на должности {context.bot_data['user'].position}
        Ваш email - {context.bot_data['user'].email}
        Ваша дополнительная информация о себе {context.bot_data['user'].info}
        Все верно?"""),
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'CHECK_DATA'


def check_data(update: Update, context: CallbackContext):
    if update.callback_query.data == 'no':
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите свой email"
        )
        message = update.effective_message
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
        return 'GET_EMAIL'
    context.bot_data['user'].networking = True
    context.bot_data['user'].save()
    return get_networking(update, context)


def get_user_info(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent("""
        Чтобы участвовать в нетворкинге, оставьте, пожалуйста, дополнительную информацию о себе
        Введите, пожалуйста, имя и фамилию через пробел""")
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'GET_NAME'


def get_networking(update: Update, context: CallbackContext):
    if not context.bot_data['user'].firstname:
        return get_user_info(update, context)
    elif context.bot_data['user'].networking == False:
        keyboard = [
            [InlineKeyboardButton('Подтвердить участие в нетворкинге', callback_data='confirm')],
            [InlineKeyboardButton('Главное меню', callback_data='to_start')]
        ]
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Для участия в нетворкинге нужжно ваше согласие",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        message = update.effective_message
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
        return 'CONFIRM_NETWORKING'
    return make_networking(update, context)


def make_networking(update: Update, context: CallbackContext):
    networking_connections_count = User.objects.filter(networking=True).count()
    keyboard = [
        [InlineKeyboardButton('Познакомиться', callback_data='find_contact')] if networking_connections_count > 1 else [],
        [InlineKeyboardButton('Изменить \nинформацию о себе', callback_data='change_info'), InlineKeyboardButton('Отказаться \nот участия в нетворкинге', callback_data='cancel_networking')],
        [InlineKeyboardButton('Главное меню', callback_data='to_start')]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent(f"""
        {context.bot_data['user'].firstname}, рады видеть вас в нетворкинге.
        Сейчас нас {networking_connections_count} человек"""),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'NETWORK_COMMUNICATE'


def get_questions(update: Update, context: CallbackContext):
    questions_count = context.bot_data['user'].questions_to.filter(answered=False).count()
    if questions_count == 0:
        keyboard = [
            [InlineKeyboardButton('Главное меню', callback_data='to_start')],
        ]
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='У вас нет неотвеченных вопросов',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        message = update.effective_message
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=message.message_id
        )
        return 'ANSWER_QUESTIONS'
    keyboard = [
        [InlineKeyboardButton('Ответить на вопрос', callback_data='answer')],
        [InlineKeyboardButton('Главное меню', callback_data='to_start')],
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=dedent(f'''
        У вас {questions_count} неотвеченных вопросов
        Хотите ответить?'''),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'ANSWER_QUESTIONS'


def answer_questions(update: Update, context: CallbackContext):
    if update.callback_query and update.callback_query.data == 'to_start':
        return start(update, context)
    question = random.choice(context.bot_data['user'].questions_to.filter(answered=False).select_related())
    keyboard = [
        [InlineKeyboardButton('Следующий вопрос', callback_data='next_question')],
        [InlineKeyboardButton('Не отвечать', callback_data='mark_answered')],
        [InlineKeyboardButton('Главное меню', callback_data='to_start')],
    ]
    context.bot_data['question'] = question
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question.text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'GET_ANSWER'


def get_answer(update: Update, context: CallbackContext):
    if update.callback_query:
        if update.callback_query.data == 'to_start':
            return start(update, context)
        elif update.callback_query.data == 'mark_answered':
            context.bot_data['question'].answered = True
            context.bot_data['question'].answer_time = timezone.now()
            context.bot_data['question'].save()
            try:
                return answer_questions(update, context)
            except IndexError:
                return get_questions(update, context)
        elif update.callback_query.data == 'next_question':
            try:
                return answer_questions(update, context)
            except IndexError:
                return get_questions(update, context)
    if update.message:
        answer = dedent(f"""
        Ответ на вопрос:
        <i>{context.bot_data['question'].text}</i>
        от <b>{context.bot_data['user']}</b>
        <code>{update.message.text}</code>
        """)
        context.bot.send_message(
            chat_id=int(context.bot_data['question'].asker.chat_id),
            text=answer,
            parse_mode='HTML'
        )
        context.bot_data['question'].answer = update.message.text
        context.bot_data['question'].answer_time = timezone.now()
        context.bot_data['question'].answered = True
        context.bot_data['question'].save()
        try:
            return answer_questions(update, context)
        except IndexError:
            return get_questions(update, context)


def show_speakers(update: Update, context: CallbackContext):
    speakers = User.objects.filter(status='SPEAKER')
    keyboard = [
        [InlineKeyboardButton(f"{speaker} - {speaker.company}", callback_data=str(speaker.id))]
        for speaker in speakers
    ] + [[InlineKeyboardButton('Главное меню', callback_data='to_start')]]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Список выступающих на митапе',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'GET_SPEAKER'


def show_program(update: Update, context: CallbackContext):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    events = Event.objects.all()
    keyboard = [
        [InlineKeyboardButton(f"{event.name} - {event.start_time.strftime('%H:%M')}",
         callback_data=str(event.id))]
        for event in events
    ] + [[InlineKeyboardButton('Главное меню', callback_data='to_start')]]

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
    return 'EVENT_DETAILS'


def ask_donation(update: Update, context: CallbackContext, text='Выберите сумму доната или введите произвольную, но не меньше 100 рублей'):
    keyboard = [
        [InlineKeyboardButton('100 р.', callback_data='100'), InlineKeyboardButton('300 р.', callback_data='300'), InlineKeyboardButton('1000 р.', callback_data='1000')],
        [InlineKeyboardButton('Главное меню', callback_data='start')]
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    message = update.effective_message
    context.bot.delete_message(
        chat_id=message.chat_id,
        message_id=message.message_id
    )
    return 'MAKE_DONATION'
