from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('renting/', views.renting_students, name='renting_students'),
    path('dormitory/', views.dormitory_students, name='ttj_students'),
    path('orphan/', views.orphan_students, name='yetim_talabalar'),
    path('disabled/', views.disabled_students, name='nogironligi_bor'),
    path('create/', views.student_create, name='student_create'),
    path('<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('api/districts/', views.get_districts, name='get_districts'),
]
