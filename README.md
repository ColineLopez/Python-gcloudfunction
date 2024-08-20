# 🎵 Typeform to Airtable Spotify Artist Data

This project automatically receives events from a Typeform form and extracts Spotify artist data.

## 🚀 Quick Start

### 📝 Typeform

The Typeform model used in this project includes three types of questions: text, URL, and email. The final question is for accepting the terms and conditions.

### 🔑 Airtable Authentication 

You need to set up your Airtable credentials as follows:

```python
from pyairtable import Table
AIRTABLE_API_KEY = "YOUR_AIRTABLE_API_KEY"
AIRTABLE_TOKEN   = "YOUR_AIRTABLE_TOKEN"
AIRTABLE_BASE_ID = "YOUR_AIRTABLE_BASE_ID"

table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_NAME)
```

### 🎵 Spotify Authentication

Configure Spotify credentials with the following setup:

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID     = 'YOUR_SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI  = 'YOUR_SPOTIPY_REDIRECT_URI'

sp = spotipy.Spotify(auth_manager =SpotifyOAuth(client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET, redirect_uri = SPOTIPY_REDIRECT_URI)) 
```

## 🔧 Functions 

### 📈 `get_artist_popularity`

Retrieve the popularity of an artist from their Spotify profile. Returns an integer between 0 and 100.

```python
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

```

### 📊 `get_artist_monthlyListeners`

Retrieve the monthly listeners of an artist from their Spotify profile. This function also returns a tier value:

- 1 if the artist has more than 1.5 million monthly listeners.
- 2 if they have between 100,000 and 1.5 million.
- 3 otherwise.


```python
from bs4 import BeautifulSoup

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

            # Initalisation Ã  0
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

```

### 📥 `post`

Extract form data and update Airtable with the ```table.create(inscription)``` method. This function also calls ```get_artist_popularity``` and ```get_artist_monthly_listeners``` to populate the Airtable database.

## ☁️ Google Cloud Platform

### Console initialization

Initialize Google Cloud Platform with:

```Bash
gcloud init
```

### Function deployment :

Deploy the function with:

```Bash
gcloud functions deploy webhook_response --runtime python37 --trigger-http 
```

After deployment, you should see a success message with the following details:

```Bash
availableMemoryMb: 256
entryPoint: webhook_response
httpsTrigger:
  url: https://us-central1-typeform-to-airtable.cloudfunctions.net/webhook_response
labels:
  deployment-tool: cli-gcloud
name: projects/typeform-to-airtable/locations/us-central1/functions/webhook_response
runtime: python37
```

Make sure to copy the URL from `httpsTrigger` and configure it in the Typeform webhook settings (tab Connect > Webhook) to integrate it with your form.
