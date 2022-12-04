import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if api_key is not None:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        print("Network exception occured")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
    except:
        print("Network exception occured")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result["result"]
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], 
                                   lat=dealer_doc["lat"], 
                                   long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], 
                                   st=dealer_doc["st"], 
                                   zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

#get_dealer_by_state
def get_dealer_by_state_from_cf(url, state):
    results = []
    json_result = get_request(url, state=state)
    if json_result:
        dealers = json_result["result"]
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], 
                                   lat=dealer_doc["lat"], 
                                   long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], 
                                   st=dealer_doc["st"], 
                                   zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

def get_dealer_by_id(url, dealer_id):
    dealer_obj = None
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    if json_result:
        if json_result["statusCode"] == 404:
            return dealer_obj
        dealer_doc = json_result["body"]
        # For each dealer object
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                short_name=dealer_doc["short_name"],
                                st=dealer_doc["st"], state=dealer_doc["state"], zip=dealer_doc["zip"])
    return dealer_obj

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_Id):
    result = []
    json_result = get_request(url, dealerId=dealer_Id)
    if json_result:
        reviews = json_result["data"]["docs"]
        for review_doc in reviews:
            #review_doc = review["docs"]
            review_obj = DealerReview(
                dealership = review_doc["dealership"],
                name = review_doc["name"],
                purchase = review_doc["purchase"],
                review = review_doc["review"],
                purchase_date = review_doc.get("purchase_date"),
                car_make = review_doc.get("car_make"),
                car_model = review_doc.get("car_model"),
                car_year = review_doc.get("car_year"),
                sentiment = analyze_review_sentiments(review_doc["review"]),
                review_id = review_doc.get("id")
            )
            result.append(review_obj)
    return result


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    json_result = get_request("https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/e983e9dd-40c9-4248-a519-ebc70870fa53",
                            api_key = "080PM4gjE02s9RfY7BrRlWf_gK2p6LgiJIhlcZqW6WE0",
                            text = dealerreview, features = 'sentiment',
                            return_analyzed_text = False, version = '2022-08-10')
    sentiment = 'unknown'
    print(json_result)
    sentiment_response = json_result.get("sentiment")
    if sentiment_response:
        sentiment = sentiment_response['document']['label']
    return sentiment