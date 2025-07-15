from django.contrib import admin
from .models import Event, EventPhoto
from .models import Message,MessageReply
class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 0
    readonly_fields = ['uploaded_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'event_date', 'category', 'status', 'participants_count']
    list_filter = ['status', 'category', 'event_date']
    search_fields = ['title', 'organizer__first_name', 'organizer__last_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [EventPhotoInline]
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'description', 'category', 'event_date', 'location')
        }),
        ('Tashkilotchi', {
            'fields': ('organizer', 'participants_count')
        }),
        ('Status', {
            'fields': ('status', 'reviewed_by', 'reviewed_at', 'dean_comment')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ['event', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    readonly_fields = ['uploaded_at']

admin.site.register(Message)
admin.site.register(MessageReply)