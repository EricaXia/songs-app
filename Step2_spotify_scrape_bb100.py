import os
from glob import glob
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import json
import pickle

# find all csv files stored in 'data' folder
PATH = "data/"
EXT = "*.csv"
csv_files = [file
             for path, subdir, files in os.walk(PATH)
             for file in glob(os.path.join(path, EXT))]

spotify_ids = []

# loop over each BB100 CSV file
for file in csv_files:

    # path = r'data\2020-03-31_billboard_100.csv'
    # df_bb100 = pd.read_csv(path)

    df_bb100 = pd.read_csv(file)

    # inner loop for each song in 'Song' column of df
    for song in df_bb100['Song']:

        # Begin Spotify scrape
        client_id = 'f7e5487237a44720bc3fe1b2afc641ce'
        client_secret = 'b9c005c1698e4655aad6000750267140'

        auth_url = 'https://accounts.spotify.com/api/token'

        # authorization response
        resp = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        })

        json_data = resp.json()
        # Get OAUTH access token
        accesstoken = json_data['access_token']

        # Set the API Headers
        api_headers = {
            'Authorization': f'Bearer {accesstoken}'
        }

        # set base API URL
        api_url = 'https://api.spotify.com/v1/'

        # Search to find Track ID
        # search for Track ID, given a song's name and search name
        search_url = api_url + 'search?q={query}'

        # define a search query
        track_name = song.lower()
        # format by replacing space with '%'
        track_name_f = track_name.replace(' ', '%20')
        search_query = f'{track_name_f}&type=track'

        search_response = requests.get(
            search_url.format(query=search_query),
            headers=api_headers
        )

        search_response_dict = search_response.json()

        # get first search response's Track Id
        searched_track_id = search_response_dict['tracks']['items'][0]['id']

        track_id = searched_track_id

        # add to Spotify id list (to link with Genius data later)
        song_fname = re.sub('[^a-zA-Z0-9_]+', '', song)
        spotify_ids.append((song, song_fname, track_id))

        # get Track Info of searched Track id
        get_track_url = api_url + 'tracks/{id}'

        # GET call
        track_response = requests.get(
            get_track_url.format(id=track_id),
            headers=api_headers
        )

        # parsing the json reponse to Python dictonary
        track_response_dict = track_response.json()

        # Get the same track's Audio Features Info
        get_af_url = api_url + 'audio-features/{id}'

        af_response = requests.get(
            get_af_url.format(id=track_id),
            headers=api_headers
        )

        af_response_dict = af_response.json()

        # Get the track's Artist Info
        # get artist id from previous data above
        artist_id = track_response_dict['artists'][0]['id']

        get_artist_url = api_url + 'artists/{id}'

        artist_response = requests.get(
            get_artist_url.format(id=artist_id),
            headers=api_headers
        )

        artist_response_dict = artist_response.json()

        print(f"downloaded files for: {song}")

        fname = re.sub('[\W_]+', '', song)  # extract only alphanumeric chars
        fname1 = fname.replace(' ', '')

        # try export the 3 dicts to jsons
        with open(f"data/tracks/{fname1}_track.json", "w") as f:
            json.dump(track_response_dict, f)

        with open(f"data/tracks/{fname1}_af.json", "w") as f:
            json.dump(af_response_dict, f)

        with open(f"data/tracks/{fname1}_artist.json", "w") as f:
            json.dump(artist_response_dict, f)

# save track ids
with open(f"data/spotify_ids.pkl", "wb") as f:
    pickle.dump(spotify_ids, f)
