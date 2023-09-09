from django.contrib import admin
from .models import *

admin.site.register(Plans)
admin.site.register(EventTypes)
admin.site.register(Events)
admin.site.register(Subscriptions)
admin.site.register(ItineraryTypes)
admin.site.register(Itinerary)
admin.site.register(Category)
admin.site.register(Prompts)

