from time import sleep
import requests

from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone

from .models import Event, User, Question, Donate, Message


class EventStatusFilter(SimpleListFilter):
    title = 'Статус'
    parameter_name = 'finish_time'

    def lookups(self, request, model_admin):
        return (
            ('passed', 'Прошедшие'),
            ('future', 'Запланированные'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'passed':
            return queryset.filter(
                finish_time__lte=timezone.now()
            )
        if self.value() == 'future':
            return queryset.filter(
                finish_time__gte=timezone.now()
            )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_time',
        'finish_time'
    )
    list_filter = (EventStatusFilter,)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'company',
        'position',
        'status',
        'networking'
    )
    list_filter = ('status', 'networking')
    list_display_links = (
        '__str__',
        'status'
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    raw_id_fields = (
        'asker',
        'answerer'
    )
    list_display = (
        'asker',
        'answerer',
        'answered',
        'ask_time',
    )
    readonly_fields = (
        'ask_time',
        'answer_time',
    )


@admin.register(Donate)
class DonateAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_filter = ('amount',)
    list_display = (
        'user',
        'amount',
        'time'
    )
    readonly_fields = ('time', 'user', 'amount')



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('time_sent',)
    raw_id_fields = ('targets',)
    list_display = ('__str__', 'time_sent')

    def response_add(self, request, obj, post_url_continue=...):
        if not obj.to_send:
            return super().response_add(request, obj, post_url_continue)
        token = settings.TG_TOKEN
        destinations = [target.chat_id for target in obj.targets.all()]
        for chat_id in destinations:
            response = requests.post(
                url=f'https://api.telegram.org/bot{token}/sendMessage', data={
                    'chat_id': chat_id,
                    'text': obj.text,
                }
            )
            print(response)
            response.raise_for_status()
            sleep(2)
        obj.to_send = False
        obj.time_sent = timezone.now()
        obj.save()
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if not obj.to_send:
            return super().response_change(request, obj)
        token = settings.TG_TOKEN
        destinations = [target.chat_id for target in obj.targets.all()]
        for chat_id in destinations:
            response = requests.post(
                url=f'https://api.telegram.org/bot{token}/sendMessage', data={
                    'chat_id': chat_id,
                    'text': obj.text,
                }
            )
            print(response)
            response.raise_for_status()
            sleep(2)
        obj.to_send = False
        obj.time_sent = timezone.now()
        obj.save()
        return super().response_change(request, obj)
