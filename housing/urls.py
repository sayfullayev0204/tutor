from django.urls import path
from . import views

urlpatterns = [
    path('', views.inspection_list, name='inspection_list'),
    path('create/<int:student_id>/', views.create_inspection, name='create_inspection'),
    path('<int:pk>/', views.inspection_detail, name='inspection_detail'),
    path('<int:pk>/review/', views.review_inspection, name='review_inspection'),
    path('dean/inspections/', views.dean_inspections, name='dean_inspections'),
    path('inspections/<int:inspection_id>/approve/', views.approve_inspection, name='approve_inspection'),
    path('rooms/<int:room_id>/inspect/', views.create_inspection, name='create_inspection'),
    path('dean/inspections/', views.dean_inspections, name='dean_inspections'),
    path('inspections/<int:inspection_id>/approve/', views.approve_inspection, name='approve_inspection'),

    path('pending/', views.pending_inspections, name='pending_inspections'),
    path('room/create/', views.room_create, name='room_create'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('inspections/<int:pk>/photos/', views.inspection_photos, name='inspection_photos'),
    path('rooms/', views.room_list, name='room_list'),
    
]
