from django.contrib import admin

from .models import Event, User, Question, Donut

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_time',
        'finish_time'
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'company',
        'position',
        'status',
        'networking'
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    raw_id_fields = (
        'asker',
        'answerer'
    )

@admin.register(Donut)
class DonutAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
