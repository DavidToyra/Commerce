from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchcounter = models.IntegerField(default=0)

class Categories(models.Model):
    category = models.CharField(max_length=64)

class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    price = models.IntegerField()
    img = models.URLField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_user")
    winner = models.ForeignKey(User, null=True, default=None, on_delete=models.CASCADE, related_name="winner_user")
    active = models.BooleanField()
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)



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