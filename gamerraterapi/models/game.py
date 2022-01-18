from django.db import models
from gamerraterapi.models.rating import Rating


class Game(models.Model):

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    designer = models.CharField(max_length=50)
    year_released = models.IntegerField()
    num_players = models.IntegerField()
    gameplay_length = models.IntegerField()
    age = models.IntegerField()
    categories = models.ManyToManyField(
        "Category", through="GameCategory", related_name="categories")

    @property
    def average_rating(self):
        """Average rating calculated attribute for each game"""
        ratings = Rating.objects.filter(game=self)

        # Sum all of the ratings for the game
        total_rating = 0
        for rating in ratings:
            total_rating += rating.rating
        if len(ratings) > 0:
            avg_rating = total_rating/len(ratings)
        else:
            avg_rating = 0
            
        return avg_rating 

        # Calculate the averge and return it.
        # If you don't know how to calculate averge, Google it.
