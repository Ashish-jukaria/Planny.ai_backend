from app.models import Prompt  # Replace with the actual import path for your Prompt model

class ServicePrompt:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def fetch_prompt_data(self, key):
        # Replace this with your database query to fetch the data
        # key can be anything based on the requirement  
        try:
            prompt_data = Prompt.objects.get(key='planer')
            data = {
                'format': prompt_data.format,
                'description': prompt_data.description,
            }
            return data
        except Prompt.DoesNotExist:
            return None

    def get_prompt(self, key, category, plan_type, budget):
        data = self.fetch_prompt_data(key)
        if data:
            response_format = data['format']
            description = data['description']

            formatted_prompt = f"{response_format}\n\n{description}"
            formatted_prompt = formatted_prompt.format(
                category=category, plan_type=plan_type, budget=budget
            )

            return formatted_prompt
        else:
            return "No prompt found in the database."
