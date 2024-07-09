from django.db import models
from user.models import UserProfile

# Create your models here.
class Article(models.Model):

    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    visibility = models.CharField(max_length=20)
    summary = models.CharField(max_length=200)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


