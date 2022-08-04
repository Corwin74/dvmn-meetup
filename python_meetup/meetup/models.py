from django.db import models
from django.utils import timezone


class User(models.Model):
    tg_nick = models.CharField(
        'Ник в Телеграм',
        max_length=50,
    )
    chat_id = models.CharField(
        'Id для бота',
        max_length=50,
        blank=True,
    )
    tg_state = models.CharField(
        'Состояние бота',
        max_length=50,
        default='START'
    )
    email = models.CharField(
        'Email',
        max_length=100,
        blank=True
    )

    firstname = models.CharField(
        'Имя',
        max_length=50,
        blank=True
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=50,
        blank=True
    )
    company = models.CharField(
        'Компания',
        max_length=100,
        blank=True
    )
    position = models.CharField(
        'Должность',
        max_length=100,
        blank=True
    )
    info = models.TextField(
        'Информация о себе',
        blank=True,
    )

    STATUS_CHOICES = [
        ('PARTICIPANT', 'Участник'),
        ('SPEAKER', 'Спикер')
    ]
    status = models.CharField(
        'Статус',
        max_length=50,
        choices=STATUS_CHOICES,
        default='PARTICIPANT'
    )
    networking = models.BooleanField(
        'Готов к нетворкингу',
        default=False
    )

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname} {self.chat_id} {self.tg_nick}"

    class Meta:
        verbose_name = 'Участник',
        verbose_name_plural = 'Участники'


class Event(models.Model):
    name = models.CharField(
        'Название',
        max_length=100,
    )

    start_time = models.DateTimeField(
        'Время начала'
    )

    finish_time = models.DateTimeField(
        'Время окончания'
    )

    description = models.TextField(
        'Описание',
        blank=True
    )
    speaker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='Спикер',
        related_name='events',
        null=True
    )

    def __str__(self) -> str:
        return f"{self.name} {self.start_time.strftime('%H:%M')} - {self.finish_time.strftime('%H:%M')}"

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


class Question(models.Model):
    asker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='От кого',
        related_name='questions_from'
    )
    answerer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Кому',
        related_name='questions_to',
    )
    text = models.TextField(
        'Текст вопроса',
        blank=True,
    )
    ask_time = models.DateTimeField(
        'Время создания',
        default=timezone.now()
    )
    answered = models.BooleanField(
        'Отвечен',
        default=False
    )
    answer = models.TextField(
        'Ответ',
        blank=True
    )
    answer_time = models.DateTimeField(
        'Время ответа',
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self) -> str:
        return f"Вопрос {self.answerer.__str__()}"

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class Donut(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Кто донатил',
        related_name='donuts'
    )
    amount = models.DecimalField(
        'Сумма доната',
        decimal_places=2,
        max_digits=6,
        default=0
    )
    time = models.DateTimeField(
        'Время доната',
        default=timezone.now(),
    )

    def __str__(self) -> str:
        return f"{self.user.__str__()} - {self.amount}"

    class Meta:
        verbose_name = 'Донат'
        verbose_name_plural = 'Донаты'
