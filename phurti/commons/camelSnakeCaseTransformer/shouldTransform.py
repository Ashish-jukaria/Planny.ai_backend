from rest_framework import renderers
from rest_framework.settings import api_settings
from django.http import QueryDict
from .utils import deep_snake_case_transform


class ShouldTransform:
    def dispatch(self, request, *args, **kwargs):
        if not request.GET.get("_transform", False):
            """
            The purpose of this mixin is to add the <code data-enlighter-language="generic" class="EnlighterJSRAW">case-transformation</code> renderers and parsers
            only in case it's forced from the client (putting the '_transform' GET kwarg). If the client
            wants the data in the <code data-enlighter-language="generic" class="EnlighterJSRAW">snake_case</code> format we just put the default renderers and parsers.*
            * Check: https://github.com/encode/django-rest-framework/blob/master/rest_framework/views.py#L97
            """
            self.renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
            self.parser_classes = api_settings.DEFAULT_PARSER_CLASSES
        else:
            # Make request's GET QueryDict mutable
            request.GET._mutable = True
            # Delete <code data-enlighter-language="generic" class="EnlighterJSRAW">_transofrm</code> key since we don't need it
            del request.GET["_transform"]
            # Convert query params to snake_case
            request_get_dict = deep_snake_case_transform(request.GET.dict())
            # The following lines puts the snake_cased params back to the request.GET
            # https://docs.djangoproject.com/en/2.0/ref/request-response/#django.http.QueryDict.update
            request_get = QueryDict("", mutable=True)
            request_get.update(request_get_dict)
            request_get._mutable = False
            request.GET = request_get
        return super().dispatch(request, *args, **kwargs)
