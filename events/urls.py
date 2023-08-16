from django.urls import path
from . import views

urlpatterns = [
   # path('event/create/', views.create_event, name='create_event'),
    path('event', views.create_event, name='create_event'),
   # path('event_type/create/', views.create_event_type, name='create_event_type'),
]
