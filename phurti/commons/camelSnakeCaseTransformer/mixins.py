from rest_framework import renderers
from .renderers import CamelCaseRenderer
from .parsers import SnakeCaseParser
from .shouldTransform import ShouldTransform


class ToCamelCase(renderers.JSONRenderer, ShouldTransform):
    renderer_classes = [
        CamelCaseRenderer,
    ]


class FromCamelCase(ShouldTransform):
    parser_classes = [
        SnakeCaseParser,
    ]
