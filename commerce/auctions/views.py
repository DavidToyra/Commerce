from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listings, Bids, Comments
from django.conf import settings

def index(request):
    listings = Listings.objects.all()
    print(settings.BASE_DIR)

    return render(request, "auctions/index.html", {'listings': listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")
    
    elif request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        startBid = request.POST["startbid"]
        img = request.POST["urlimage"]
        
        print(title, description,startBid)

        listing = Listings(title=title, description = description, startbid=startBid, img=img)
        listing.save()
       
        return HttpResponseRedirect(reverse("index"))
    
def listing(request,title):
    if request.method == "GET":
        listing = Listings.objects.get(title=title)
        return render(request, "auctions/listing.html",{
            "listing": listing
        })
    if request.method == "POST":
        if 'watchlist' in request.POST:
            #Add to watchlist
            bid, created = Bids.objects.get(user=request.user, listing=title)
            bid.currentBid = request.POST["bid"]
            listing = Listings.objects.get(title=title)
            listing.startbid = request.POST["bid"]
        