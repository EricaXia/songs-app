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
conn.close()
