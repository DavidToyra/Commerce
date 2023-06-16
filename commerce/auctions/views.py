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

        listing = Listings(title=title, description = description, startbid=startBid, img=img,owner=request.user)
        listing.save()
       
        return HttpResponseRedirect(reverse("index"))
    
def listing(request,title):
    if request.method == "GET":
        listing = Listings.objects.get(title=title)

        # Check if a bid model exists for this user, if not display default values on listing page
        try:
            bid = Bids.objects.get(user=request.user, listing=listing)
        except Bids.DoesNotExist:

            return render(request, "auctions/listing.html",{
            "listing": listing
        })
           
        return render(request, "auctions/listing.html",{
            "listing": listing, "bids":bid
        })
    if request.method == "POST":
        listID = Listings.objects.get(title=title)
        if 'watchlist' in request.POST:
            #Add to watchlist
            print("add to watchlist")
            #TODO: FIX SO IT UPDATE WATCHLIST INSTEAD OF CREATING A NEW BID MODEL
            try:
                bid = Bids.objects.get(user=request.user, listing=listID)
            except Bids.DoesNotExist:
                
            bid = Bids.objects.get_or_create(user=request.user, listing=listID, watchlist=True, currentBid=0)
            return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Added to watchlist", "bids": bid
            })
        elif 'unwatch' in request.POST:
            #Remove from watch list
            print("remove from watchlist")
            bid = Bids.objects.get(user=request.user, listing=listID)
            bid.watchlist=False
            bid.save()
            return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Removed from watchlist", "bids": bid
            })
        elif 'bid' in request.POST:
            #Add bid on existing auction
            bid = request.POST["bid"]
            try:
                bid = Bids.objects.get(user=request.use, listing=listID)
                if request.POST["bid"] > bid.currentBid and request.POST["bid"] >= listing.startbid:
                    bid.currentBid = request.POST["bid"]
                    bid.save()
            except Bids.DoesNotExist:
                if request.POST["bid"] >= listing.startbid:
                    bid = Bids.objects.get_or_create(user=request.use, listing=listID,
                                                    watchList=False, currentBid=request.POST["bid"])
        elif 'comment' in request.POST:
            comment = Comments(comment=comment, user=request.user, listing=listID)
            comment.save()

        
