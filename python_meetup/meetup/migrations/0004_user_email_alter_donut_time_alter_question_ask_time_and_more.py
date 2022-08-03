# Generated by Django 4.0.6 on 2022-08-03 08:29

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('meetup', '0003_question_donut'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(blank=True, max_length=100, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='donut',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 3, 8, 29, 29, 422337, tzinfo=utc), verbose_name='Время доната'),
        ),
        migrations.AlterField(
            model_name='question',
            name='ask_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 3, 8, 29, 29, 422337, tzinfo=utc), verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='user',
            name='tg_state',
            field=models.CharField(default='START', max_length=50, verbose_name='Состояние бота'),
        ),
    ]