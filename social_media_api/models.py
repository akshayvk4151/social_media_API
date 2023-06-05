from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100)
    weight = models.IntegerField()

    def __str__(self):
        return self.name


class Post(models.Model):
    description = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_posts', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_posts')

    def __str__(self):
        return self.description[:50]


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.image.name
    
