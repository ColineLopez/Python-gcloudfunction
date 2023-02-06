# Typeform to Airtable Spotify Artist Data

### Automatic reception of events from a typeform form &amp; Spotify Artist data extraction

## Quick Start

# Typeform

The typeform model used for this example requires 3 types of questions : text, URL and email. The last question is about accepting the terms and conditions. 

# Airtable Authentication 

```python
from pyairtable import Table
AIRTABLE_API_KEY = "YOUR_AIRTABLE_API_KEY"
AIRTABLE_TOKEN   = "YOUR_AIRTABLE_TOKEN"
AIRTABLE_BASE_ID = "YOUR_AIRTABLE_BASE_ID"

table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_NAME)
```

# Spotify Authentication

```python
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIPY_CLIENT_ID     = 'YOUR_SPOTIPY_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'YOUR_SPOTIPY_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI  = 'YOUR_SPOTIPY_REDIRECT_URI'

sp = spotipy.Spotify(auth_manager =SpotifyOAuth(client_id = SPOTIPY_CLIENT_ID, client_secret = SPOTIPY_CLIENT_SECRET, redirect_uri = SPOTIPY_REDIRECT_URI)) 
```

### Functions 

# get_artist_popularity

Get the artist popularity from his spotify profile. This function will return an integer between 0 and 100. 

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

# get_artist_monthlyListeners

Get the monthly listeners of an artist from his spotify profile. This information will be extracted by reading the HTML code source from the artist's spotify profile. This function also returns the value of tier (1 if the artist has more than 1.5e6 monthly listeners, 2 if they are between 1e5 and 1.5e6, 3 otherwise).


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

# post

Get the form data. This function also calls ```get_artist_popularity``` and ```get_artist_monthlyListeners```, to feed the Airtable database with ```table.create(inscription)```. 


## Gougle Cloud Platform

Console initialization :

```Bash
gcloud init
```

Function deployment :

```Bash
gcloud functions deploy webhook_response --runtime python37 --trigger-http 
```

After a few minutes, the success message on the console should be as follows :

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

Be aware that you need to copy the right `url` from the `httpsTrigger`. It will be necessary to copy it on the typeform webhook (tab connect > webhook), so that it will connect with the form. 
