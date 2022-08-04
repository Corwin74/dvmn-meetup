from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils import timezone

from .models import Event, User, Question, Donate


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
    readonly_fields = ('time',)
