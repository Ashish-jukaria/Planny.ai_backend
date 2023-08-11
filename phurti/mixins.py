from rest_framework import renderers

from phurti.commons.camelSnakeCaseTransformer.renderers import (
    BrowsableCamelCaseRenderer,
    CamelCaseRenderer,
)
from phurti.commons.camelSnakeCaseTransformer.parsers import SnakeCaseParser
from phurti.commons.camelSnakeCaseTransformer.shouldTransform import ShouldTransform


class ToCamelCase(renderers.BrowsableAPIRenderer, ShouldTransform):
    renderer_classes = (
        BrowsableCamelCaseRenderer,
        CamelCaseRenderer,
    )


class FromCamelCase(ShouldTransform):
    parser_classes = (SnakeCaseParser,)
