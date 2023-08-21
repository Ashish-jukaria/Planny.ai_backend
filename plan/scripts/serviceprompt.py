from plan.models import Prompts, Category

class ServicePrompt:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    #Getting the key from prompt table
    def fetch_prompt_data(self, key):
        prompt_data = Prompts.objects.filter(key=key).first()
        return prompt_data
    #matching header with title to link both the tables
    def fetch_category_description(self, header):
        category = Category.objects.filter(title=header).first()
        if category:
            return category.description
        return None

    def get_prompt(self, key, category, plan_type, budget):
        prompt_data = self.fetch_prompt_data(key)
        if prompt_data:
            response_format = prompt_data.format
            header = prompt_data.header

            description = self.fetch_category_description(header)
            if description is not None:
                formatted_prompt = f"{response_format}\n\n{description}"
                formatted_prompt = formatted_prompt.format(
                    category=category, plan_type=plan_type, budget=budget
                )
                return formatted_prompt
            else:
                return "No category description found for the prompt."

        return "No prompt found in the database."