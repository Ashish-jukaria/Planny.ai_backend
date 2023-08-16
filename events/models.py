from django.db import models

class EventType(models.Model):
    class Meta:
        app_label = "events"
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title

class Event(models.Model):
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    plan_id = models.IntegerField()
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return self.title
