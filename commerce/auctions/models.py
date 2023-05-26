from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    startbid = models.IntegerField()
    img = models.URLField(max_length=200)

class Bids(models.Model):
    currentBid = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    #Change from key to string?
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)
    watchlist = models.BooleanField()

class Comments(models.Model):
    comment = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listings, on_delete=models.CASCADE)