from django.db import models

class Review(models.Model):

    game = models.ForeignKey("Game", on_delete=models.CASCADE)
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    review = models.CharField(max_length=50)
    date = models.DateTimeField()