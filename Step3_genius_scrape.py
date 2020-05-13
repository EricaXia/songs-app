import requests
from bs4 import BeautifulSoup
import json
import re
import numpy as np
import pandas as pd
import os
from glob import glob
from requests_oauthlib import OAuth2Session  # requires installation

client_id = 'hjAAh3f8SCTjC8YwuWOw_SC1Bbrld0-8pHzps79gZRexkQqJ1wYDHZCX8bWmMaQ3'
client_secret = 'WwCsfJyYc0VeAM200jBFnVRAAZME2RAeJemDd65XIjUTInpH4uSgW88sDcfI0YH5uoQtZYzUJWp7qkjcQQFoXA'

redirect_uri = 'https://genius.com/'

# base url
base_url = 'https://api.genius.com/'

auth_url = 'https://api.genius.com/oauth/authorize'

token_url = 'https://api.genius.com/oauth/token'


genius = OAuth2Session(
    client_id, redirect_uri=redirect_uri, scope='me', state='1')

# Redirect user to Genius for authorization
print()
print("Genius.com username: musketeers1128@gmail.com")
print("Genius.com password: 5JL6wGJ1oqGD")
authorization_url, state = genius.authorization_url(auth_url)
print()
print('Please authorize by visiting the URL below. Login with provided credentials and click Approve:')
print(authorization_url)  # PLEASE GO TO THIS URL IN YOUR BROWSER

print()
print('Paste the response URL below:')
redirect_response = input()

# Fetches the access token
token_response = genius.fetch_token(token_url, client_secret=client_secret,
                                    authorization_response=redirect_response, client_id=client_id, response_type='code')

my_access_token = token_response['access_token']

# Set the API Headers
# fake the "User Agent" in the api header to avoid error
api_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36',
    'Authorization': f'Bearer {my_access_token}'
}


# Accessing Genius Song API and scraing Lyrics
# Begin loop HERE

# find all csv files stored in 'data' folder
PATH = "data/"
EXT = "*.csv"
csv_files = [file
             for path, subdir, files in os.walk(PATH)
             for file in glob(os.path.join(path, EXT))]

# loop over each BB100 CSV file (each file is one week on the BB100)
for file in csv_files:

    df_bb100 = pd.read_csv(file)
    unique_songs0 = []
    for s in df_bb100['Song']:
        unique_songs0.append(s)
    unique_songs = list(set(unique_songs0))

    # download lyrics for unique songs only (avoids duplicate dls)
    for song in unique_songs:
        # search for song via Genius API
        query = f'{song}'.replace(" ", "%20")
        # extract only alphanumeric chars and percent sign
        query = re.sub('[^a-zA-Z0-9%_]+', '', query)
        search_query = f'search?q={query}'
        search_url = base_url + search_query
        r = genius.get(search_url, headers=api_headers)
        search_api_path = r.json()['response']['hits'][0]['result']['api_path']

        # using found song's api path, get the song's page
        song_url = f"https://api.genius.com{search_api_path}&access_token={my_access_token}"
        r2 = genius.get(song_url, headers=api_headers)
        song_json = r2.json()['response']['song']
        lyrics_url = song_json['url']   # actual url for lyrics page

        # Scrape the actual song lyrics using BS4

        page = requests.get(lyrics_url)
        html = BeautifulSoup(page.text, "html.parser")
        lyrics = html.find("div", class_="lyrics").get_text()
        print(f"Downloaded lyrics for: {song}")

        # Write the song's lyrics to a text file

        fname = re.sub('[^a-zA-Z0-9_]+', '', song) + '.txt'

        with open(f'data/lyrics/{fname}', 'wb') as f:
            lyrics_encoded = lyrics.encode('utf8')
            f.write(lyrics_encoded)

        # Write the song's Genius metadata to json file
        fname2 = re.sub('[^a-zA-Z0-9_]+', '', song) + '.json'

        with open(f'data/lyrics/{fname2}', 'w') as f:
            json.dump(song_json, f)
