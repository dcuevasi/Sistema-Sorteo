from django.contrib import admin
from .models import Participant, Winner


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'verification_status', 'is_participating', 'created_at')
    list_filter = ('verification_status', 'is_participating', 'created_at')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ('verification_token', 'created_at', 'updated_at')


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ('participant', 'draw_date', 'selected_by', 'notification_sent')
    list_filter = ('draw_date', 'notification_sent')
    search_fields = ('participant__full_name', 'participant__email')
    readonly_fields = ('draw_date', 'created_at')
