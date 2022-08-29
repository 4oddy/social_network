from django.contrib import admin

from .models import Conservation, ConservationMessage, Dialog, DialogMessage


@admin.register(Conservation)
class ConservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_creating')


@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'second_user', 'date_of_creating')


@admin.register(ConservationMessage)
class ConservationMessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'sender', 'group', 'date_of_sending')


@admin.register(DialogMessage)
class DialogMessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'sender', 'group', 'date_of_sending')
