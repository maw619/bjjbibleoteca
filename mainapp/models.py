from django.db import models
from django.contrib.auth.models import User

     
class Category(models.Model):
    name = models.CharField(max_length=255)

class Section(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="sections", on_delete=models.CASCADE)

class Video(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    section = models.ForeignKey(Section, related_name="videos", on_delete=models.CASCADE)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    timestamp = models.FloatField(null=True, blank=True)  # seconds
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user} - {self.video}"
    
