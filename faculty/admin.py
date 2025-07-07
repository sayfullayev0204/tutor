from django.contrib import admin
from .models import Faculty, Group


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'dean', 'groups_count', 'students_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    raw_id_fields = ('dean',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'tutor', 'course', 'students_count', 'created_at')
    list_filter = ('faculty', 'course', 'created_at')
    search_fields = ('name',)
    raw_id_fields = ('tutor',)
