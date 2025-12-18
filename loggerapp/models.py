from django.contrib.auth.models import User
from django.db import models

class PredictionLog(models.Model):  # ✅ renamed from LogEntry to PredictionLog
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) #If the linked User is deleted, the user field will be set to NULL, not deleted.(ondelete=models.SET_NULL)
    text = models.TextField()
    intent = models.CharField(max_length=100)
    tone = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
