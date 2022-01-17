from django.db import models

class Entry(models.Model):
    
    entry = models.TextField()
    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    game = models.ForeignKey("Game", on_delete=models.CASCADE)