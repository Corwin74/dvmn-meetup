# Generated by Django 4.0.6 on 2022-08-04 07:47

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('meetup', '0007_question_answer_alter_donut_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='answer_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время ответа'),
        ),
        migrations.AlterField(
            model_name='donut',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 4, 7, 47, 14, 661132, tzinfo=utc), verbose_name='Время доната'),
        ),
        migrations.AlterField(
            model_name='question',
            name='ask_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 4, 7, 47, 14, 660132, tzinfo=utc), verbose_name='Время создания'),
        ),
    ]