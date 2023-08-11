from django.contrib import admin
from .models import *


class CallbackRequestAdmin(admin.ModelAdmin):
    model = CallbackRequest


admin.site.register(CallbackRequest, CallbackRequestAdmin)
