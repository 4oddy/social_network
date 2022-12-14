from django.contrib import admin

from .models import (AbstractDialog, AbstractMessage, Conservation,
                     ConservationMessage, Dialog, DialogMessage)


class BaseMessageAdmin(admin.ModelAdmin):
    model = AbstractMessage
    list_display = ('text', 'sender', 'group', 'date_of_sending')
    list_select_related = ('sender', 'group', 'group__owner')


class BaseGroupAdmin(admin.ModelAdmin):
    model = AbstractDialog
    list_display = ('name', 'owner', 'date_of_creating')
    list_select_related = ('owner', )


@admin.register(Conservation)
class ConservationAdmin(BaseGroupAdmin):
    pass


@admin.register(Dialog)
class DialogAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'second_user', 'date_of_creating')
    list_select_related = ('owner', 'second_user')


@admin.register(ConservationMessage)
class ConservationMessageAdmin(BaseMessageAdmin):
    pass


@admin.register(DialogMessage)
class DialogMessageAdmin(BaseMessageAdmin):
    list_select_related = ('sender', 'group', 'group__owner', 'group__second_user')
