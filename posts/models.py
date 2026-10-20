from django.db import models


class Post(models.Model):
    photo = models.ImageField(upload_to='images/')
