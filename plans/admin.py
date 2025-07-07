from django.contrib import admin
from .models import Plan, Reminder


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'tutor', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['priority', 'status', 'created_at', 'due_date']
    search_fields = ['title', 'description', 'tutor__username']
    date_hierarchy = 'due_date'


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'plan', 'remind_at', 'is_sent', 'created_at']
    list_filter = ['is_sent', 'remind_at', 'created_at']
    search_fields = ['title', 'message', 'plan__title']
