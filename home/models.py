from django.db import models

class Message(models.Model):
    user_id = models.CharField(max_length=255)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
