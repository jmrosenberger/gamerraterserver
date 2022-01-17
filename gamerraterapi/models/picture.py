from django.db import models

class Picture(models.Model):

    player = models.ForeignKey("Player", on_delete=models.CASCADE)
    game = models.ForeignKey(
        "Game", on_delete=models.CASCADE, related_name='pictures')
    image = models.ImageField(
        upload_to='gameimages/', height_field=None,
        width_field=None, max_length=None, null=True)
