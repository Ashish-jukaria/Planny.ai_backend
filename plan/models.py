from django.db import models

class Prompts(models.Model):
    key = models.IntegerField(unique=True)
    header = models.CharField(max_length=100)
    format = models.JSONField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.key)  
    class Meta:
        verbose_name_plural = "Prompts"


class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/')  
    route = models.SlugField(unique=True)

    def __str__(self):
        return self.titled 