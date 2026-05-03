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


class NoteComment(models.Model):
    note = models.ForeignKey(Note, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user} on note {self.note_id}"


class NoteLike(models.Model):
    note = models.ForeignKey(Note, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["note", "user"], name="unique_note_like")
        ]

    def __str__(self):
        return f"{self.user} liked note {self.note_id}"
    


class VideoLike(models.Model):
    video = models.ForeignKey(Video, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["video", "user"], name="unique_video_like")
        ]

    def __str__(self):
        return f"{self.user} liked video {self.video_id}"
