from rest_framework import parsers
from phurti.commons.camelSnakeCaseTransformer.utils import deep_snake_case_transform


class SnakeCaseParser(parsers.JSONParser):
    def parse(self, stream, *args, **kwargs):
        data = super().parse(stream, *args, **kwargs)
        return deep_snake_case_transform(data)
