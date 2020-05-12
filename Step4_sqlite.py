import pandas as pd
import numpy as np
import json
import re
import sqlite3
import os
from glob import glob
import pickle
import dask.dataframe as dd

# Add all Spotify data to db  ---------
print("Adding Spotify data to SQLite3 database...")

conn = sqlite3.connect('music.db')
c = conn.cursor()

# Add 'track' table to db
c.execute(
    """
    DROP TABLE IF EXISTS track;
    """
)

c.execute("""
    CREATE TABLE track (
    album_name VARCHAR(255),  
    album_id VARCHAR(255), 
    artist_name VARCHAR(255), 
    artist_id VARCHAR(255),
    disc_number INT,
    duration_ms REAL,
    explicit VARCHAR(255),
    external_urls VARCHAR(255),  
    href VARCHAR(255),
    id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    popularity INT,
    track_number INT,
    type VARCHAR(255),
    uri VARCHAR(255),
    PRIMARY KEY (id)); 
    """)


# Insert all track json files into sqlite3 db
PATH = "data/tracks/"
EXT = "*_track.json"
t_jsons = [file
           for path, subdir, files in os.walk(PATH)
           for file in glob(os.path.join(path, EXT))]

for fname in t_jsons:

    with open(rf'{fname}') as f:
        t = json.load(f)

    c.execute(
        """
        INSERT OR IGNORE INTO track ( 
            album_name, album_id, artist_name, artist_id, disc_number, duration_ms, explicit, external_urls, href, id, name, popularity, track_number, type, uri) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            t['album']['name'],
            t['album']['id'],
            t['artists'][0]['name'],
            t['artists'][0]['id'],
            t['disc_number'],
            t['duration_ms'],
            t['explicit'],
            t['external_urls']['spotify'],
            t['href'],
            t['id'],
            t['name'],
            t['popularity'],
            t['track_number'],
            t['type'],
            t['uri']
        )
    )

conn.commit()

# Add 'audio features' table to db
c.execute(
    """
    DROP TABLE IF EXISTS audio_features;
    """
)

c.execute("""
    CREATE TABLE audio_features (
    danceability REAL,
    energy REAL,
    key INT,
    loudness REAL,
    mode INT,
    speechiness REAL,
    acousticness REAL,
    instrumentalness REAL,
    liveness REAL,
    valence REAL,
    tempo REAL, 
    type VARCHAR(255),
    id VARCHAR(22) NOT NULL,
    uri VARCHAR(255),
    track_href VARCHAR(255),
    analysis_url VARCHAR(255),
    duration_ms REAL,
    time_signature INT,
    PRIMARY KEY (id)); 
    """)


# find all "_af.json" artist files stored in 'data' folder
PATH = "data/tracks/"
EXT = "*_af.json"
af_jsons = [file
            for path, subdir, files in os.walk(PATH)
            for file in glob(os.path.join(path, EXT))]

for fname in af_jsons:

    with open(rf'{fname}') as f:
        af_dict = json.load(f)

# insert each af json key:value into db
    c.execute("""INSERT OR IGNORE INTO audio_features (danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, type, id, uri, track_href, analysis_url, duration_ms, time_signature) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
        af_dict['danceability'],
        af_dict['energy'],
        af_dict['key'],
        af_dict['loudness'],
        af_dict['mode'],
        af_dict['speechiness'],
        af_dict['acousticness'],
        af_dict['instrumentalness'],
        af_dict['liveness'],
        af_dict['valence'],
        af_dict['tempo'],
        af_dict['type'],
        af_dict['id'],
        af_dict['uri'],
        af_dict['track_href'],
        af_dict['analysis_url'],
        af_dict['duration_ms'],
        af_dict['time_signature']
    )
    )


conn.commit()

# Add 'artist' table to db
c.execute(
    """
    DROP TABLE IF EXISTS artist;
    """
)

c.execute("""
    CREATE TABLE artist (
    external_urls VARCHAR(255),  
    followers INT, 
    genre VARCHAR(255), 
    href VARCHAR(255),
    id VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    popularity INT,
    type VARCHAR(255),
    PRIMARY KEY (id)); 
    """)

# Insert all artist json files into sqlite3 db
PATH = "data/tracks/"
EXT = "*_artist.json"
a_jsons = [file
           for path, subdir, files in os.walk(PATH)
           for file in glob(os.path.join(path, EXT))]

for fname in a_jsons:

    with open(rf'{fname}') as f:
        a = json.load(f)

    try:
        genres = a['genres']
    except IndexError:
        genres = 'None'

    genres_str = ", ".join(genres)

    c.execute(
        """
        INSERT OR IGNORE INTO artist ( 
            external_urls, followers, genre, href, id, name, popularity, type) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
            a['external_urls']['spotify'],
            a['followers']['total'],
            genres_str,
            a['href'],
            a['id'],
            a['name'],
            a['popularity'],
            a['type']
        )
    )

conn.commit()

# Add Genius Lyrics data ---------
with open(r'data/spotify_ids.pkl', 'rb') as f:
    spotify_ids = pickle.load(f)

print("Adding Genius lyrics and Billboard 100 data to SQLite3 database...")
# connect to music sqlite3 database

# Join Spotify track ids to Genius lyrics data
PATH = "data/lyrics/"
EXT = "*.txt"

lyric_txts = [file
              for path, subdir, files in os.walk(PATH)
              for file in glob(os.path.join(path, EXT))]

lyrics_dict = {}

for fname in lyric_txts:
    fname_spl = fname.split('.txt')[0]
    fname_spl2 = fname_spl.split('\\')
    song = fname_spl2[1]

    with open(fname, 'r', encoding='utf8') as f:
        lyrics_dict[song] = f.read()

# df to store lyrics data
lyrics_df = (pd.DataFrame.from_dict(lyrics_dict, orient='index')).reset_index(
).rename(index=str, columns={'index': 'song_name', 0: 'text'})
# df to store spotify ids
spotify_df = pd.DataFrame(spotify_ids).rename(
    columns={0: 'song_name_orig', 1: 'song_name', 2: 'spotify_id'})

spotify_df.drop_duplicates(inplace=True)

# merge spotify ids df and lyrics df
merged = lyrics_df.merge(spotify_df, how='left', on='song_name')

# add to sqlite db
merged.to_sql('lyrics', con=conn, index=False, if_exists='replace')
conn.commit()


# Add BB100 data to sqlite db ---------

# find all csv files stored in 'data' folder
# Dask can read in multiple csvs to a single df
bb100_dask = dd.read_csv('data/*.csv')
bb100_df = bb100_dask.compute()  # convert to Pandas df

# add to sqlite db
bb100_df.to_sql('bb100', con=conn, index=False, if_exists='replace')
conn.commit()

# close the connection
conn.close()
