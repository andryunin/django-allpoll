from django.contrib import admin
from allpoll.models import Poll, Choice, Vote


class ChoiceInlineModelAdmin(admin.TabularInline):
    model = Choice


class PollAdmin(admin.ModelAdmin):
    fields = (
        'question',
        ('start_date', 'stop_date'),
        'allow_anonymous'
    )

    inlines = (
        ChoiceInlineModelAdmin,
    )


admin.site.register(Poll, PollAdmin)
