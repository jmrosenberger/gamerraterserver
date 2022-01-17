from django.db import models

class Game(models.Model):
    
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    designer = models.CharField(max_length=50)
    year_released = models.IntegerField()
    num_players = models.IntegerField()
    gameplay_length = models.IntegerField()
    age = models.IntegerField()
    categories = models.ManyToManyField("Category", through="GameCategory", related_name="categories")
    