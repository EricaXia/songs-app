# A script to filter non-instrumental tracks from Spotify playlist
# Alternatively, to separate 1 playlist into 2 vocal or instrumental playlists

import os
from glob import glob
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import json
import pickle

client_id = '1697e60c847943509aac84bdfbdb7647'
client_secret = '8c2f6db8c0754f90af1a5a1005ca9f0b'

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
print(json_data)

# Set the API Headers
api_headers = {
    'Authorization': f'Bearer {accesstoken}'
}

# set base API URL
api_url = 'https://api.spotify.com/v1/'


# Try getting a playlist's tracks
# ENTER PLAYLIST ID HERE!!!
playlist_id = "2C7Y4FUCSW2vbDijeJWMVt"  # ENTER PLAYLIST ID HERE

playlist_url = api_url + f'playlists/{playlist_id}/tracks'

playlist_response = requests.get(
    playlist_url,
    headers=api_headers
)

response_dict = playlist_response.json()

# store playlist's track ids
track_ids = []
for i in response_dict['items']:
    track_ids.append((i['track']['name'], i['track']['id']))


# store initial isntrumental values for all tracks
instrum = []

# # Get Audio Features Info
for t in track_ids:

    name = t[0]
    id = t[1]

    get_af_url = api_url + 'audio-features/{id}'

    af_response = requests.get(
        get_af_url.format(id=id),
        headers=api_headers
    )

    af_response_dict = af_response.json()
    instrum.append([name, id, af_response_dict['instrumentalness']])


print("Initial song count:", len(instrum))

# Can adjust instrumentalness value up or down:
filter_instrumental = [tup for tup in instrum if tup[2] > 0.75]


print("Filtered instrumentals song count:", len(filter_instrumental))
# print(filter_instrumental)

filtered_ids = [l[1] for l in filter_instrumental]

print(filtered_ids)

# write to pickle
with open('filtered_ids.pkl', 'wb') as f:
    pickle.dump(filtered_ids, f)
