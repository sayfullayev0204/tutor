from django.contrib import admin
from .models import HousingInspection, InspectionPhoto


class InspectionPhotoInline(admin.TabularInline):
    model = InspectionPhoto
    extra = 1


@admin.register(HousingInspection)
class HousingInspectionAdmin(admin.ModelAdmin):
    list_display = ('student', 'inspector', 'inspection_date', 'condition', 'status')
    list_filter = ('condition', 'status', 'inspection_date', 'student__group__faculty')
    search_fields = ('student__first_name', 'student__last_name', 'inspector__first_name', 'inspector__last_name')
    raw_id_fields = ('student', 'inspector', 'reviewed_by')
    inlines = [InspectionPhotoInline]
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('student', 'inspector', 'condition', 'comment')
        }),
        ('Ko\'rib chiqish', {
            'fields': ('status', 'dean_comment', 'reviewed_by', 'reviewed_at')
        }),
    )


@admin.register(InspectionPhoto)
class InspectionPhotoAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)
    raw_id_fields = ('inspection',)
