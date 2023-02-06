import os
from dotenv import load_dotenv
load_dotenv()

import json 
import requests 
import flask 
from pyairtable import Table

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from bs4 import BeautifulSoup

# Authentication AIRTABLE
AIRTABLE_API_KEY = os.getenv("YOUR_AIRTABLE_API_KEY")
AIRTABLE_TOKEN   = os.getenv("YOUR_AIRTABLE_TOKEN")
AIRTABLE_BASE_ID = os.getenv("YOUR_AIRTABLE_BASE_ID")

# Authentication SPOTIFY 
SPOTIPY_CLIENT_ID     = os.getenv("YOUR_SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("YOUR_SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI  = os.getenv("YOUR_SPOTIPY_REDIRECT_URI")

sp = spotipy.Spotify(auth_manager =SpotifyOAuth(client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET, redirect_uri = SPOTIPY_REDIRECT_URI)) #scope=scope))

# Webhook endpoint
AIRTABLE_URL = "YOUR_AIRTABLE_URL"
AIRTABLE_NAME = "YOUR_AIRTABLE_NAME"

# Typeform URL
TYPEFORM_URL = "YOURE_TYPEFORM_URL" 

# Gcloud Function
def webhook_response(request: flask.Request):
	if request.method == 'POST':
		return post(request)
	else:
		flask.abort(405)

# Form data
def post(request: flask.Request):
	data = request.get_json()
	inscription = { }
	# Simplified Data 
	formReponse = data['form_response']

	for reponse in formReponse['answers']:
		if reponse['type'] == 'text':
			inscription.update({"Nom artiste" : reponse['text']})
		if reponse['type'] == 'url':
			inscription.update({'Spotify ID' : reponse['url']})
		if reponse["type"] == 'email':
			inscription.update({'Email' : reponse['email']})
	url = inscription.get('Spotify ID')
	popularity = get_artist_popularity(url) 
	inscription.update({'Popularity' : popularity})
	monthlyListeners, tier = get_artist_monthlyListeners(url) 
	inscription.update({'Monthly Listeners' : monthlyListeners})
	inscription.update({'Tier': tier})
	table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_NAME)
	table.create(inscription)
	return inscription


def get_artist_popularity(spotifyID): 
    '''---------------------------
    Get the artist popularity from his spotify ID.

    Parameter :
    -----------
    - spotifyID : Artist's Spotify URL
    ------------------------------'''
    try:
        if sp.artist(spotifyID).get('popularity') != 0:
            return sp.artist(spotifyID).get('popularity')
    except:
        return 0


def get_artist_monthlyListeners(spotifyID):
    '''---------------------------
    Get the monthly listeners of an artist from his spotify profile.

    Parameter :
    -----------
    - spotifyID : Artist's Spotify URL
    ------------------------------'''
    try:
        if spotifyID is not None: 
            url = BeautifulSoup(requests.get(spotifyID).content, 'html.parser')

            divs = url.find_all("div")

            # Initalisation à 0
            monthlyListeners  = 0 
            tier = 0

            for div in divs:
	            try:
		            if(div['data-testid'] == 'monthly-listeners-label'):
			            monthlyListeners = int(div.text.split(' ')[0].replace(',',''))
	            except KeyError: 
		            pass

            if monthlyListeners >= 1.5e6:
	            tier = 1
            elif monthlyListeners >= 1e5 and monthlyListeners < 1.5e6:
	            tier = 2
            else:
	            tier = 3

            return monthlyListeners, tier 
    except:
        return 0



