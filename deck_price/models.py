from django.db import models

class Decks(models.Model):
    hash = models.CharField(max_length=25, unique=True)
    post = models.CharField(max_length=1000)
