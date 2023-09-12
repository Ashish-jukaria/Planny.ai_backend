from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .utils import generate_gpt_response
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework import viewsets
from .models import Category
from .serializers import CategorySerializer



@csrf_exempt
def gpt_response_view(request):
    if request.method == "POST":
        prompt_text = request.POST.get("prompt_text")
        print(prompt_text)
        response_text = generate_gpt_response(prompt_text)
        if response_text:
            return JsonResponse({"response": response_text})
        else:
            return JsonResponse(
                {
                    "error": "Failed to generate response. Please check your input or try again later."
                }
            )
    else:
        return JsonResponse({"error": "Invalid request method"})

from plan.models import Prompts, Category
from .scripts.serviceprompt import ServicePrompt
import sqlite3
def get_prompt_view(request):
    if request.method == 'GET':
        key = request.GET.get('key')
        category = request.GET.get('category')
        plan_type = request.GET.get('plan_type')
        budget = request.GET.get('budget')
        db_connection=sqlite3.connect(".db")
        service = ServicePrompt(db_connection)
        formatted_prompt = service.get_prompt(key, category, plan_type, budget)
        db_connection.close()
        return JsonResponse({'prompt': formatted_prompt})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

class SubscriptionListCreateView(generics.ListCreateAPIView):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionSerializer


class SubscriptionRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscriptions.objects.all()
    serializer_class = SubscriptionSerializer


class PlansListCreateView(generics.ListCreateAPIView):
    queryset = Plans.objects.all()
    serializer_class = PlansSerializer


class PlansRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plans.objects.all()
    serializer_class = PlansSerializer


class EventsListCreateView(generics.ListCreateAPIView):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer


class EventsRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Events.objects.all()
    serializer_class = EventsSerializer


class ItineraryListCreateView(generics.ListCreateAPIView):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer


class ItineraryRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


