from django.contrib import admin
from .models import User, Listings, Bids, Comments, Categories

# Register your models here.
admin.site.register(User)
admin.site.register(Listings)
admin.site.register(Bids)

