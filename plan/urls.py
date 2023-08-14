# urls.py
from django.urls import path
from .views import *

urlpatterns = [
 path('gpt-response/', gpt_response_view, name='gpt_response'),
 path('categories/', CategoryListAPIView.as_view(), name='category-list-api'),

 
 ]

