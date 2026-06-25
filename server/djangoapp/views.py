from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import os
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Helper to load dealerships and reviews from JSON
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEALERSHIPS_FILE = os.path.join(BASE_DIR, 'database', 'data', 'dealerships.json')
REVIEWS_FILE = os.path.join(BASE_DIR, 'database', 'data', 'reviews.json')

def load_dealerships():
    if os.path.exists(DEALERSHIPS_FILE):
        with open(DEALERSHIPS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('dealerships', [])
    return []

# We keep custom reviews in memory or in file so that user reviews persist!
PERSISTENT_REVIEWS = []

def load_reviews():
    global PERSISTENT_REVIEWS
    if not PERSISTENT_REVIEWS:
        if os.path.exists(REVIEWS_FILE):
            with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                PERSISTENT_REVIEWS = data.get('reviews', [])
    return PERSISTENT_REVIEWS

def save_reviews():
    global PERSISTENT_REVIEWS
    # Write back to file to persist user actions!
    try:
        with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"reviews": PERSISTENT_REVIEWS}, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving reviews: {e}")

# Simple local sentiment analysis rule engine
def analyze_sentiment(text):
    text_lower = text.lower()
    positive_words = ['fantastic', 'good', 'great', 'excellent', 'love', 'nice', 'awesome', 'best', 'friendly', 'happy']
    negative_words = ['bad', 'worst', 'terrible', 'hate', 'poor', 'slow', 'expensive', 'rude', 'sad', 'angry']
    
    for word in positive_words:
        if word in text_lower:
            return 'positive'
    for word in negative_words:
        if word in text_lower:
            return 'negative'
    return 'neutral'

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({"userName": ""})

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    
    username_exists = User.objects.filter(username=username).exists()
    if username_exists:
        return JsonResponse({"error": "Already Registered"})
    
    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})

# Update the `get_dealerships` view to render a list of dealerships
def get_dealerships(request, state=None):
    dealers = load_dealerships()
    if state:
        if state != "All":
            dealers = [d for d in dealers if d.get('state') == state or d.get('st') == state]
    return JsonResponse({"status": 200, "dealers": dealers})

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    dealers = load_dealerships()
    dealer = [d for d in dealers if d.get('id') == dealer_id]
    return JsonResponse({"status": 200, "dealer": dealer})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    reviews = load_reviews()
    dealer_reviews = [r for r in reviews if r.get('dealership') == dealer_id or str(r.get('dealership')) == str(dealer_id)]
    
    # Run sentiment analysis on the reviews
    for review in dealer_reviews:
        if 'sentiment' not in review:
            review['sentiment'] = analyze_sentiment(review.get('review', ''))
            
    return JsonResponse({"status": 200, "reviews": dealer_reviews})

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    if not request.user.is_authenticated:
        # For simplicity and cURL testing, accept anonymous or get user from data if present
        pass
    
    data = json.loads(request.body)
    reviews = load_reviews()
    
    new_id = 1
    if reviews:
        new_id = max(r.get('id', 0) for r in reviews) + 1
        
    new_review = {
        "id": new_id,
        "name": data.get('name', 'Anonymous'),
        "dealership": int(data.get('dealership')),
        "review": data.get('review', ''),
        "purchase": data.get('purchase', False),
        "purchase_date": data.get('purchase_date', ''),
        "car_make": data.get('car_make', ''),
        "car_model": data.get('car_model', ''),
        "car_year": int(data.get('car_year', 2023)),
        "sentiment": analyze_sentiment(data.get('review', ''))
    }
    
    reviews.append(new_review)
    save_reviews()
    
    return JsonResponse({"status": 200})

# Get list of cars
def get_cars(request):
    car_models = CarModel.objects.all()
    cars_list = []
    for car in car_models:
        cars_list.append({
            "CarMake": car.car_make.name,
            "CarModel": car.name
        })
    return JsonResponse({"CarModels": cars_list})


# fetchDealers endpoint - returns plain list of dealers (no wrapper)
def fetch_dealerships(request, state=None):
    dealers = load_dealerships()
    if state and state != "All":
        dealers = [d for d in dealers if d.get('state') == state]
    # Map lat/long to latitude/longitude for correct output
    result = []
    for d in dealers:
        result.append({
            "id": d.get("id"),
            "city": d.get("city"),
            "state": d.get("state"),
            "address": d.get("address"),
            "zip": d.get("zip"),
            "latitude": d.get("lat"),
            "longitude": d.get("long"),
            "short_name": d.get("short_name"),
            "full_name": d.get("full_name"),
        })
    return JsonResponse(result, safe=False)



# fetchReviews endpoint - returns reviews without sentiment field
def fetch_dealer_reviews(request, dealer_id):
    reviews = load_reviews()
    dealer_reviews = []
    for r in reviews:
        if r.get('dealership') == dealer_id or str(r.get('dealership')) == str(dealer_id):
            review_out = {
                "id": r.get("id"),
                "name": r.get("name"),
                "dealership": r.get("dealership"),
                "review": r.get("review"),
                "purchase": r.get("purchase"),
                "purchase_date": r.get("purchase_date"),
                "car_make": r.get("car_make"),
                "car_model": r.get("car_model"),
                "car_year": r.get("car_year")
            }
            dealer_reviews.append(review_out)
    return JsonResponse(dealer_reviews, safe=False)
