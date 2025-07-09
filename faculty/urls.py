from django.urls import path
from . import views

urlpatterns = [
    # Faculty URLs (Rector only)
    path('faculties/', views.faculty_list, name='faculty_list'),
    path('faculties/create/', views.faculty_create, name='faculty_create'),
    path('faculties/<int:pk>/edit/', views.faculty_edit, name='faculty_edit'),
    path('faculties/<int:pk>/delete/', views.faculty_delete, name='faculty_delete'),
    path('faculties/<int:faculty_id>/', views.faculty_detail, name='faculty_detail'),
    # Group URLs
    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:pk>/', views.group_detail, name='group_detail'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    
    # Tutor URLs
    path('tutors/', views.tutor_list, name='tutor_list'),
    path('tutors/<int:tutor_id>/', views.tutor_detail, name='tutor_detail'),
    path('tutors/create/', views.tutor_create, name='tutor_create'),
    path('tutors/<int:tutor_id>/edit/', views.tutor_edit, name='tutor_edit'),
]
