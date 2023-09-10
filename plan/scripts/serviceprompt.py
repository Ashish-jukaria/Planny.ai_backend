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
        prompt="""This format have some keys and understand those needs and and generate the if you cant understand by values understand
by the comment (starts and end with a `#`) as what to expect/generate there. consider those comments as requirement/prompts.
Generate the response"""
        prompt_data = self.fetch_prompt_data(key)
        if prompt_data:
            response_format = prompt_data.format
            header = prompt_data.header

            description = self.fetch_category_description(header)
            if description is not None:
                formatted_prompt = f"{description}  {response_format} \n{prompt}"
                formatted_prompt = formatted_prompt.replace("\r\n", " ")

                formatted_prompt = formatted_prompt.replace("{key}", key)
                formatted_prompt = formatted_prompt.replace("{event}", "")
                formatted_prompt = formatted_prompt.replace("{date}", "")
                formatted_prompt = formatted_prompt.replace("{venue}", "")
                formatted_prompt = formatted_prompt.replace("{time}", "")
                formatted_prompt = formatted_prompt.replace("{budget}", budget)

                formatted_prompt = formatted_prompt.replace("{{category}}", category)
                formatted_prompt = formatted_prompt.replace("{{plan_type}}", plan_type)
                formatted_prompt = formatted_prompt.replace("{{budget}}", budget)

                return formatted_prompt
            else:
                return "No category description found for the prompt."

        return "No prompt found in the database."


 # url to hit the service
 # http://127.0.0.1:8000/service/prompt/?key=1&category=some_category&plan_type=typeA&budget=100.