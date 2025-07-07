from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('rector/', views.rector_dashboard, name='rector_dashboard'),
    path('dean/', views.dean_dashboard, name='dean_dashboard'),
    path('tutor/', views.tutor_dashboard, name='tutor_dashboard'),
    path('statistics/', views.statistics, name='statistics'),
]
