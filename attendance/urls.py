from django.urls import path
from . import views

urlpatterns = [
    path('attendance/', views.attendance_view, name='attendance_view'),
    path('take-attendance/<int:group_id>/', views.take_attendance, name='take_attendance'),
    path('take-attendance/<int:group_id>/<str:period>/', views.take_attendance, name='take_attendance_period'),
    path('faculty/<int:faculty_id>/groups/', views.faculty_groups, name='faculty_groups'),
    path('attendance-details/<int:group_id>/', views.attendance_details, name='attendance_details'),
    path('attendance-details/<int:group_id>/<str:attendance_date>/', views.attendance_details, name='attendance_details_date'),
    path('attendance-details/<int:group_id>/<str:attendance_date>/<str:period>/', views.attendance_details, name='attendance_details_period'),
]