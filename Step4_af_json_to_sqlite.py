import pandas as pd
import numpy as np
import json
import re
import sqlite3
import os
from glob import glob

conn = sqlite3.connect('music.db')
c = conn.cursor()

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
conn.close()