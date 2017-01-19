#Importing flask variables for a server side application
from flask import Flask, request, redirect, session

#Importing Yelp and their API / Authentication protocol
import requests
import oauth2

#Importing the credentials for the various APIs used
import credentials

#Importing BeautifulSoup to parse the HTML responses
from bs4 import BeautifulSoup

#Python module for parsing JSON
import json

#Session object makes use of 'a secret key'.
#SECRET_KEY = 'a secret key'

#Flask server side application setup
app = Flask(__name__)
app.config.from_object(__name__)

def request_yelp(url, url_params=None):
    #Initialization of credential parameters for Yelp API
    consumer_key = credentials.my_yelp_consumer_key
    consumer_secret = credentials.my_yelp_consumer_secret
    token = credentials.my_yelp_token
    token_secret = credentials.my_yelp_token_secret
    url_params = url_params or {}

    #Making the API get request using the oauth2 python library using the previously initialized credential parameters
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    oauthRequest = oauth2.Request(method="GET", url = url, parameters=url_params)
    oauthRequest.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': token,
            'oauth_consumer_key': consumer_key
        }
    )
    token = oauth2.Token(token, token_secret)
    oauthRequest.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signedURL = oauthRequest.to_url()

    #Returning the value of the API get request
    return requests.get(signedURL).json()

@app.route("/", methods=['GET', 'POST'])
def findPictureURLs():
    loc = request.args.get('location')

    searchParams = {
        'term': 'food',
        'limit': 5,
        'location': loc
    }

    yelpResponse = request_yelp("http://api.yelp.com/v2/search", searchParams)

    retResponse = {
        'businesses': []
    }

    for i in range(5):
        businessURL = yelpResponse['businesses'][i]['url']
        businessURL = businessURL.replace("/biz/", "/biz_photos/")
        businessName = yelpResponse['businesses'][i]['name']

        httpResp = requests.get(businessURL).text
        soup = BeautifulSoup(httpResp, "html.parser")

        imageURLs = []

        for item in soup.find_all(attrs={"data-photo-id": True}, limit=5):
            imageURLs.append("https://s3-media4.fl.yelpcdn.com/bphoto/" + item['data-photo-id'] + "/o.jpg")

        retResponse['businesses'].append({'images': imageURLs, 'name': businessName,})

    return json.dumps(retResponse)


if __name__ == "__main__":
    app.run(debug=True)
