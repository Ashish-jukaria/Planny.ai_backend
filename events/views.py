# from django.shortcuts import render, redirect
# from .forms import EventForm, EventTypeForm

# def create_event(request):
#     if request.method == 'POST':
#         event_form = EventForm(request.POST, request.FILES)
#         if event_form.is_valid():
#             event_form.save()
#             return redirect('event_created')  # Redirect to a success page
#     else:
#         event_form = EventForm()

#     return render(request, 'events/event_form.html', {'event_form': event_form})

# def create_event_type(request):
#     if request.method == 'POST':
#         event_type_form = EventTypeForm(request.POST)
#         if event_type_form.is_valid():
#             event_type_form.save()
#             return redirect('event_type_created')  # Redirect to a success page
#     else:
#         event_type_form = EventTypeForm()

#     return render(request, 'events/event_type_form.html', {'event_type_form': event_type_form})


from django.http import JsonResponse
from .utils import generate_wedding_plan

def wedding_plan_view(request):
    budget = 4000000  # Adjust the budget as needed
    response_data = generate_wedding_plan(budget)
    return JsonResponse(response_data)
