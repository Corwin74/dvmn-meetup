from django.db import models

class Event(models.Model):
    name = models.CharField(
        'Название',
        max_length=100,
    )

    start_time = models.DateTimeField(
        'Время начала'
    )

    finish_time = models.DateTimeField(
        'Время окончания мероприятия'
    )

    description = models.TextField(
        'Описание мероприятия',
        blank=True
    )

    def __str__(self) -> str:
        return f'{self.name} {str(self.start_time)} - {str(self.finish_time)}'

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
