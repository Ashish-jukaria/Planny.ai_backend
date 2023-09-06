# urls.py
from django.urls import path
from .views import gpt_response_view
from .views import CategoryList, CategoryDetail

urlpatterns = [
path('gpt-response/', gpt_response_view, name='gpt_response'),
path('categories/', CategoryList.as_view(), name='category-list'),
path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
 
 ]

