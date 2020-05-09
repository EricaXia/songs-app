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

# 10 cols to insert

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
conn.close()
