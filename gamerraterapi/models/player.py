from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):

    bio = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    