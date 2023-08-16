from django import forms
from .models import Event, EventType

class EventTypeForm(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ('title', 'description')

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('event_type', 'plan_id', 'title', 'description', 'image')
