from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class Article(models.Model):
    uuid = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(default='https://example.com')
    image_url = models.URLField(null=True, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)  

class ArticleLike(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    ip_address = models.GenericIPAddressField()

    class Meta:
        unique_together = ('article', 'ip_address')
    