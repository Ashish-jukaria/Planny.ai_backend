# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path("gpt-response/", gpt_response_view, name="gpt_response"),
    path("gpt-response/", gpt_response_view, name="gpt_response"),
    path(
        "subscriptions/",
        SubscriptionListCreateView.as_view(),
        name="subscription-list-create",
    ),
    path(
        "subscriptions/<int:pk>/",
        SubscriptionRetrieveUpdateDeleteView.as_view(),
        name="subscription-retrieve-update-delete",
    ),
    path("plans/", PlansListCreateView.as_view(), name="plans-list-create"),
    path(
        "plans/<int:pk>/",
        PlansRetrieveUpdateDeleteView.as_view(),
        name="plans-retrieve-update-delete",
    ),
    path("events/", EventsListCreateView.as_view(), name="events-list-create"),
    path(
        "events/<int:pk>/",
        EventsRetrieveUpdateDeleteView.as_view(),
        name="events-retrieve-update-delete",
    ),
    path(
        "itineraries/",
        ItineraryListCreateView.as_view(),
        name="itinerary-list-create",
    ),
    path(
        "itineraries/<int:pk>/",
        ItineraryRetrieveUpdateDeleteView.as_view(),
        name="itinerary-retrieve-update-delete",
    ),
]
