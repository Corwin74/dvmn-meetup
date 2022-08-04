# Generated by Django 4.0.6 on 2022-08-04 06:25

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('meetup', '0005_rename_second_name_user_lastname_alter_donut_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='info',
            field=models.TextField(blank=True, verbose_name='Информация о себе'),
        ),
        migrations.AlterField(
            model_name='donut',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 4, 6, 25, 35, 16886, tzinfo=utc), verbose_name='Время доната'),
        ),
        migrations.AlterField(
            model_name='question',
            name='ask_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 8, 4, 6, 25, 35, 16886, tzinfo=utc), verbose_name='Время создания'),
        ),
    ]