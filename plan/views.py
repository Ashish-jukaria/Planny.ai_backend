from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .utils import generate_gpt_response

@csrf_exempt
def gpt_response_view(request):
    if request.method == "POST":
        prompt_text = request.POST.get("prompt_text")
        response_text = generate_gpt_response(prompt_text)
        if response_text:
            return JsonResponse({"response": response_text})
        else:
            return JsonResponse({"error": "Failed to generate response. Please check your input or try again later."})
    else:
        return JsonResponse({"error": "Invalid request method"})

# views func for serviceprompt
import sqlite3
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from plan.models import Prompts, Category
from .scripts.serviceprompt import ServicePrompt


def get_prompt_view(request):
    if request.method == "GET":
        key = request.GET.get("key")
        category = request.GET.get("category")
        plan_type = request.GET.get("plan_type")
        budget = request.GET.get("budget")

        # aug 22nd part 2-> database connection
        db_connection = sqlite3.connect(".db")

        # Create an instance of ServicePrompt with a valid database connection
        service = ServicePrompt(db_connection)
        formatted_prompt = service.get_prompt(key, category, plan_type, budget)
        # part 3-> closing db_connection
        db_connection.close()

        return JsonResponse({"prompt": formatted_prompt})

    return JsonResponse({"error": "Invalid request method"}, status=400)