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
=======
class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


