import re
import json

class CamelSnakeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Convert incoming JSON keys from camelCase to snake_case
        if request.method in ['POST', 'PUT']:
            try:
                data = json.loads(request.body)
                converted_data = self.convert_keys(data, self.camel_to_snake)
                request._body = json.dumps(converted_data).encode('utf-8')
            except json.JSONDecodeError:
                pass

        response = self.get_response(request)

        # Convert outgoing JSON keys from snake_case to camelCase
        if 'application/json' in response.get('Content-Type', ''):
            try:
                data = json.loads(response.content)
                converted_data = self.convert_keys(data, self.snake_to_camel)
                response.content = json.dumps(converted_data).encode('utf-8')
            except json.JSONDecodeError:
                pass

        return response

    def camel_to_snake(self, name):
        # Convert CamelCase to snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def snake_to_camel(self, name):
        # Convert snake_case to CamelCase
        components = name.split('_')
        return ''.join(x.title() for x in components)

    def convert_keys(self, data, conversion_fn):
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                new_key = conversion_fn(key)
                new_value = self.convert_keys(value, conversion_fn)
                new_data[new_key] = new_value
            return new_data
        elif isinstance(data, list):
            return [self.convert_keys(item, conversion_fn) for item in data]
        else:
            return data