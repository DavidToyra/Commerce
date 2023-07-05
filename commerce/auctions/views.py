from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listings, Bids, Comments, Categories
from django.conf import settings

def index(request):

    categories = Categories.objects.all()
    if request.method == "GET":
        listings = Listings.objects.all()
        print(settings.BASE_DIR)

    if request.method == "POST":
        # Display only listings of a certain category
        category = request.POST["category"]
        print("cat from POST:" ,category)
        listings = Listings.objects.filter(category=Categories.objects.get(category=category))
    
    # Render HTML page
    return render(request, "auctions/index.html", {'listings': listings, 'categories': categories})

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
        # Fetch the listing values from POST request
        title = request.POST["title"]
        description = request.POST["description"]
        price = int(request.POST["startbid"])
        img = request.POST["urlimage"]
        category = request.POST["category"]
        print(title, description,price,category)

        # Get category or create a new one
        dbCategory, created = Categories.objects.get_or_create(category=category)
        print(dbCategory)
        print(dbCategory.category)

        listing = Listings(title=title, description = description, price=price, img=img,owner=request.user, category=dbCategory,active=True)
        listing.save()
       
        return HttpResponseRedirect(reverse("index"))
    
def listing(request,title):
    if request.method == "GET":
        listing = Listings.objects.get(title=title)

        noBid = True
        # Check if a bid model exists for this user
        try:
            #Check if user is logged in before fetching bid model
            if request.user.is_authenticated:
                bid = Bids.objects.get(user=request.user, listing=listing)
                noBid = False
        except Bids.DoesNotExist:
            print("in except block")
        
        noComment = False
        try:
            comment = Comments.objects.filter(listing=listing)
        except Comments.DoesNotExist:
            noComment = True
            # If no bid or comment model has been made render only listing details
            if noBid:
                return render(request, "auctions/listing.html",{
                "listing": listing})
        
        #If bid exists but no comment
        if noComment and not noBid:
            return render(request, "auctions/listing.html",{
            "listing": listing, "bids":bid
            })
        
        #If comment exists but no bid
        elif not noComment and noBid:
            return render(request, "auctions/listing.html",{
            "listing": listing, 'comments':comment
            })
        
        #If both bid and comment exists
        print("list price:", listing.price, " bid:", bid.currentBid)
        return render(request, "auctions/listing.html",{
            "listing": listing,'bids':bid, 'comments':comment
            })
        
    # Check whether POST contains watchlist action, added a bid, made a comment, or closed auction.
    if request.method == "POST":
        listID = Listings.objects.get(title=title)
        if 'watchlist' in request.POST:
            #Add to watchlist
            print("add to watchlist")
            request.user.watchcounter +=1
            request.user.save()

            try:
                bid = Bids.objects.get(user=request.user, listing=listID)
                bid.watchlist = True
                bid.save()
                print("fetching bid in adding to watch...")
            except Bids.DoesNotExist:   
                bid,created = Bids.objects.get_or_create(user=request.user, listing=listID, watchlist=True, currentBid=0)
                if created == True:
                    print("created")
                print("bid did not exist while adding to watch..")
            print("bid is: ", bid.currentBid)
            try:
                comment = Comments.objects.filter(listing = listID)
                return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Added to watchlist", "bids": bid, 'comments':comment
            })
            except Comments.DoesNotExist:
                pass
            return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Added to watchlist", "bids": bid
            })
        
        elif 'unwatch' in request.POST:
            #Remove from watch list
            print("remove from watchlist")
            bid = Bids.objects.get(user=request.user, listing=listID)
            bid.watchlist=False
            bid.save()

            # Decrease user's watch list counter by 1
            request.user.watchcounter -=1
            request.user.save()
            try:
                comment = Comments.objects.filter(listing = listID)
                return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Removed from watchlist", "bids": bid, 'comments':comment
            })
            except Comments.DoesNotExist:
                pass

            return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Removed from watchlist", "bids": bid
            })
        
        elif 'bidbutton' in request.POST:
            # Try and fetch existing bid from db
            try:
                bid = Bids.objects.get(user=request.user, listing=listID)

                # Fetch bid value from POST and check if it's greater than current bid
                if int(request.POST["bid"]) > bid.currentBid and int(request.POST["bid"]) >= listID.price:
                    bid.currentBid = int(request.POST["bid"])
                    bid.save()
                    listID.price = int(request.POST["bid"])
                    listID.save()
                    print("bid exists bid made")
            except Bids.DoesNotExist:
                # If bid does not exist for this user yet create one and save to db
                if int(request.POST["bid"]) >= listID.price:
                    bid, created = Bids.objects.get_or_create(user=request.user, listing=listID,
                                                    watchlist=False, currentBid=int(request.POST["bid"]))
                    print("bid did not exist")
                    listID.price = int(request.POST["bid"])
                    listID.save()

            try:
                comment = Comments.objects.filter(listing = listID)
                return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Bid made", "bids": bid, 'comments':comment
            })
            except Comments.DoesNotExist:
                pass
            return render(request, "auctions/listing.html",{
                "listing": listID, "message": "Bid made", "bids": bid
            })
        
        elif 'commentbutton' in request.POST:
            # Fetch the comment value from the POST and insert into comment db
            comment = Comments(comment=request.POST["comment"], user=request.user, listing=listID)
            comment.save()
            comments = Comments.objects.filter(listing=listID)
            try:
                bid = Bids.objects.get(user=request.user, listing=listID)
                return render(request, "auctions/listing.html", {
                    'listing':listID, 'bids':bid, 'comments':comments
                })
            except Bids.DoesNotExist:
                 return render(request, "auctions/listing.html", {
                    'listing':listID, 'comments':comments
                })
            
        elif 'close' in request.POST:
            # Set the listing as not active, can only be sent by the owner of the listing
            listID.active=False
            listID.save()
            return HttpResponseRedirect(reverse("index"))
            
            
def watchlist(request):
    bids = Bids.objects.filter(user=request.user)
    listingList = []
    for bid in bids:
        if bid.watchlist:
            listingList.append(Listings.objects.get(id=bid.listing.id))
    
    return render(request, "auctions/watchlist.html",{'listings':listingList})

        
