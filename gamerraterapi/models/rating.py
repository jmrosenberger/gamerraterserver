from django.db import models

class Rating(models.Model):

    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    rating = models.IntegerField()
