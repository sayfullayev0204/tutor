from django.contrib import admin
from .models import Mutaxassislik, Country, Region, District, TTJ, Student
from housing.models import Room
@admin.register(Mutaxassislik)
class MutaxassislikAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass

@admin.register(TTJ)
class TTJAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'capacity', 'manager_name')
    list_filter = ('condition', 'region', 'district')
    search_fields = ('name', 'address', 'manager_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'student_id', 'appartment_type', 'group')
    list_filter = ('appartment_type', 'talim_turi', 'tulov_turi', 'talim_shakli', 'gender')
    search_fields = ('first_name', 'last_name', 'student_id', 'jshshir', 'passport')
    raw_id_fields = ('group', 'mutaxassislik', 'country', 'const_region', 'const_district', 'temporary_region', 'temporary_district', 'room', 'ttj')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'middle_name', 'gender', 'birth_date', 'student_id', 'fuqaro', 'jshshir', 'passport')
        }),
        ('Academic Information', {
            'fields': ('group', 'otm', 'talim_turi', 'tulov_turi', 'talim_shakli', 'shifr', 'mutaxassislik')
        }),
        ('Address Information', {
            'fields': ('country', 'const_region', 'const_district', 'temporary_region', 'temporary_district', 'temporary_address', 'appartment_type', 'room', 'ttj')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Additional Information', {
            'fields': ('is_orphan', 'has_disability', 'lives_in_dormitory', 'is_renting', 'family_type')
        }),
    )