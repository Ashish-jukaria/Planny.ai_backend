from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .utils import generate_gpt_response

@csrf_exempt
def gpt_response_view(request):
    if request.method == "POST":
        prompt_text = request.POST.get("prompt_text")
        print(prompt_text)
        response_text = generate_gpt_response(prompt_text)
        if response_text:
            return JsonResponse({"response": response_text})
        else:
            return JsonResponse({"error": "Failed to generate response. Please check your input or try again later."})
    else:
        return JsonResponse({"error": "Invalid request method"})