import requests
from rest_framework.renderers import JSONRenderer
import re
from rest_framework.parsers import JSONParser

def generate_gpt_response(prompt_text):
    openai_api_key="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"

    response = requests.post(
        "https://api.openai.com/v1/engines/gpt-3.5-turbo/completions",
        headers={"Authorization": f"Bearer {openai_api_key}"},
        json={"prompt": prompt_text, "max_tokens": 50},  # Adjust parameters as needed
    )
    data = response.json()
    
    if "choices" in data:
        completion_text = data["choices"][0]["text"]
        return completion_text
    else:
        return None

class CamelCaseJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        new_data = self.convert_keys_to_camel_case(data)
        return super().render(new_data, accepted_media_type, renderer_context)

    def convert_keys_to_camel_case(self, data):
        import ipdb
        ipdb.set_trace
        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                new_key = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), key)
                new_data[new_key] = self.convert_keys_to_camel_case(value)
            return new_data
        elif isinstance(data, list):
            return [self.convert_keys_to_camel_case(item) for item in data]
        else:
            return data


class CamelCaseJSONParser(JSONParser):
    def parse(self, stream, media_type=None, parser_context=None):
        data = super().parse(stream, media_type, parser_context)
        return self.convert_keys_to_snake_case(data)

    def convert_keys_to_snake_case(self, data):

        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                new_key = re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()
                new_data[new_key] = self.convert_keys_to_snake_case(value)
            return new_data
        elif isinstance(data, list):
            return [self.convert_keys_to_snake_case(item) for item in data]
        else:
            return data



