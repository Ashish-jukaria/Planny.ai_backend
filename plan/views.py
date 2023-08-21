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


#service prompt func

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from plan.models import Prompts, Category
from scripts import serviceprompt
def get_prompt_view(request):
    if request.method == 'GET':
        key = request.GET.get('key')
        category = request.GET.get('category')
        plan_type = request.GET.get('plan_type')
        budget = request.GET.get('budget')

        # Create an instance of ServicePrompt with a valid database connection
        service = serviceprompt()

        formatted_prompt = service.get_prompt(key, category, plan_type, budget)
        return JsonResponse({'prompt': formatted_prompt})

    return JsonResponse({'error': 'Invalid request method'}, status=400)