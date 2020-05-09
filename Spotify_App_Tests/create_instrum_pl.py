""" 
Run this file as "python create_instrum_pl.py 7b2rrjtyfs5b6ud2z07qscvci"
 """
import pickle
import sys
import spotipy
import spotipy.util as util
import os

# Load the track ids to add to the playlist
filtered_ids = pickle.load(
    open(r'filtered_ids.pkl', 'rb'))

scope = 'playlist-modify-public'

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Usage: %s username" % (sys.argv[0],))
    sys.exit()

token = util.prompt_for_user_token(username,
                                   scope,
                                   client_id='1697e60c847943509aac84bdfbdb7647',
                                   client_secret='8c2f6db8c0754f90af1a5a1005ca9f0b',
                                   redirect_uri='https://spotify.com')


if token:
    sp = spotipy.Spotify(auth=token)
    my_user_id = "7b2rrjtyfs5b6ud2z07qscvci"
    pl_name = "Chill Instrumental - New"

    # Create new playlist
    pl = sp.user_playlist_create(user=my_user_id, name=pl_name,
                                 public=True, description='')

    print(f"New playlist '{pl_name}' created!")
    print(f"Playlist id: {pl['id']}")

    sp.trace = False
    # Add tracks to playlist
    results = sp.user_playlist_add_tracks(my_user_id, pl['id'], filtered_ids)

    print("Instrumental tracks added.")

else:
    print("Can't get token for", username)
