# urls.py
from django.urls import path
from .views import gpt_response_view
#service prompt
from .views import get_prompt_view

urlpatterns = [
 path('gpt-response/', gpt_response_view, name='gpt_response'),
 #prompt url->link to phurti's url
 path('prompt/',get_prompt_view,name="get_prompt"),
 ]

