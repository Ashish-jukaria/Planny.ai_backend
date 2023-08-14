# urls.py
from django.urls import path
from .views import gpt_response_view

urlpatterns = [
 path('gpt-response/', gpt_response_view, name='gpt_response'),
 
 ]

