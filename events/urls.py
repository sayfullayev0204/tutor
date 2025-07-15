from django.urls import path
from . import views


urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/details/', views.event_details_modal, name='event_details_modal'),
    path('dean/', views.dean_events, name='dean_events'),
    path('<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('send/', views.create_message, name='send_message'),
    path('list/', views.message_list, name='message_list'),
    path('detail/<int:message_id>/', views.message_detail, name='message_detail'),
]
