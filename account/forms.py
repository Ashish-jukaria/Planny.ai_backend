from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class ProfileForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = "__all__"
