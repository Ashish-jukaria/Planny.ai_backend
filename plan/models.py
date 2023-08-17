from django.db import models

from django.contrib.auth.models import User
from django.conf import settings


class Plans(models.Model):
    # category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class EventTypes(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Events(models.Model):
    type = models.ForeignKey(EventTypes, on_delete=models.CASCADE)
    plan_id = models.ForeignKey(Plans, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="event_images/")

    def __str__(self):
        return self.title


class Subscriptions(models.Model):
    title = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions_plan",
    )
    desc = models.TextField()
    supported_features = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title.username


class ItineraryTypes(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Itinerary(models.Model):
    event_id = models.ForeignKey("Events", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    type = models.ForeignKey(ItineraryTypes, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
