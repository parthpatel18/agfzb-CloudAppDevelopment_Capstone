from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_by_state_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context={}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context) 


# Create a `contact` view to return a static contact page
def contact(request):
    context={}
    if request.method == "GET":
        return render(request, 'djangoapp/contact_us.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context={}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
            # return render(request, 'djangoapp/index.html', context)
        else:
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        password = request.POST['password']

        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug('{} is new User'.format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/0de7ff62-e93c-4d44-8eb2-0187fc810083/dealership-package/get-dealership.json"
        dealerships = get_dealers_from_cf(url)
        dealer_names = ''.join([(dealer.short_name) for dealer in dealerships])
        return HttpResponse(dealer_names)


def get_dealerships_by_state(request, state):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/0de7ff62-e93c-4d44-8eb2-0187fc810083/dealership-package/get-dealership.json"
        dealerships = get_dealer_by_state_from_cf(url, state)
        dealer_names = ''.join([(dealer.short_name) for dealer in dealerships])
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/0de7ff62-e93c-4d44-8eb2-0187fc810083/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        dealer_reviews = ''.join([(review.review + " " + review.sentiment) for review in reviews])
        return HttpResponse(dealer_reviews)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == 'GET':
            context= {}
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            context['cars'] = cars
            # get dealer information
            context['dealer'] = get_dealer_by_id(
                'https://us-south.functions.appdomain.cloud/api/v1/web/0de7ff62-e93c-4d44-8eb2-0187fc810083/dealership-package/get-dealership', dealer_id
            )
            return render(request, 'djangoapp/add_review.html', context)
        elif request.method == 'POST':
            # deal with the purchasecheck field
            purchase = request.POST.get('purchasecheck')
            if purchase is None:
                purchase = False
            else:
                if purchase == 'on':
                    purchase = True
                else:
                    purchase = False

            review = {
                'time': datetime.utcnow().isoformat(),
                'dealership': dealer_id,
                'review': request.POST['content'],
                'name': ' '.join([request.user.first_name, request.user.last_name]),
                'purchase': purchase
            }


            if review['purchase']:
                car = CarModel.objects.get(id=int(request.POST['car']))
                review.update({
                    'car_make': car.car_make.name,
                    'car_model': car.name,
                    'car_year': car.year.year,
                    'purchase_date': request.POST['purchasedate']
                })
            json_payload = {
                'review': review,            
            }
            response = post_request('https://us-south.functions.appdomain.cloud/api/v1/web/0de7ff62-e93c-4d44-8eb2-0187fc810083/dealership-package/post-review', 
                                    json_payload, dealerId=dealer_id)
    return HttpResponse(response)
    # return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

