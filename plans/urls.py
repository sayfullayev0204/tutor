from django.urls import path
from . import views

urlpatterns = [
    path('', views.plan_list, name='plan_list'),
    path('<int:pk>/', views.plan_detail, name='plan_detail'),
    path('create/', views.plan_create, name='plan_create'),
    path('<int:pk>/edit/', views.plan_edit, name='plan_edit'),
    path('<int:pk>/delete/', views.plan_delete, name='plan_delete'),
    path('<int:pk>/status/', views.update_plan_status, name='update_plan_status'),
    path('<int:plan_pk>/reminder/', views.add_reminder, name='add_reminder'),
]
