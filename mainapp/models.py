from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)

class Section(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="sections", on_delete=models.CASCADE)

class Video(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    section = models.ForeignKey(Section, related_name="videos", on_delete=models.CASCADE)