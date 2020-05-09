#!/usr/bin/env python
# coding: utf-8

import sqlite3
import sqlalchemy
import pandas as pd
import numpy as np
import json
import re
import os
from glob import glob
import pickle
import dask.dataframe as dd



with open (r'data/spotify_ids.pkl', 'rb') as f:
    spotify_ids = pickle.load(f)


# connect to music sqlite3 database 
conn = sqlite3.connect('music.db')
c = conn.cursor()


# Join Spotify track ids to Genius lyrics data
PATH = "data/lyrics/"
EXT = "*.txt"

lyric_txts = [file
             for path, subdir, files in os.walk(PATH)
             for file in glob(os.path.join(path, EXT))]

lyrics_dict = {}   # dict to store {song: lyrics} values

for fname in lyric_txts:
    fname_spl = fname.split('.txt')[0]
    fname_spl2 = fname_spl.split('\\')
    song = fname_spl2[1]
    
    with open(fname, 'r', encoding='utf8') as f:
        lyrics_dict[song] = f.read()


lyrics_df = (pd.DataFrame.from_dict(lyrics_dict, orient='index')).reset_index().rename(index = str, columns = {'index': 'song_name', 0: 'text'})


spotify_df = pd.DataFrame(spotify_ids).rename(columns = {0: 'song_name_orig', 1: 'song_name', 2: 'spotify_id'})


spotify_df.drop_duplicates(inplace=True)


# merge spotify ids df and lyrics df
merged = lyrics_df.merge(spotify_df, how='left', on='song_name')


# add to sqlite db
merged.to_sql('lyrics', con=conn, index=False, if_exists='replace')
conn.commit()



# Add BB100 data to sqlite db

# find all csv files stored in 'data' folder
bb100_dask = dd.read_csv('data/*.csv')  # Dask can read in multiple csvs to a single df
bb100_df = bb100_dask.compute()  # convert Dask df to Pandas df

# add to sqlite db
bb100_df.to_sql('bb100', con=conn, index=False, if_exists='replace')
conn.commit()


conn.close()

