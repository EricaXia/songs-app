""" Python script to scrape the Billboard Top 100 Ranked Songs """

import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import datetime
import os

# base url defaults to most recent week
base_url = 'https://www.billboard.com/charts/hot-100/'

# can change the number of weeks as desired
numweeks = 4
today = datetime.datetime.today()
# get list of dates of the past n weeks
d_list = [today - datetime.timedelta(weeks=x) for x in range(numweeks)]
dates = [d.strftime('%Y-%m-%d') for d in d_list]

# Loop over each week and download the top 100 songs' data
for d in dates:

    url = base_url + d
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # download songs and artists
    songs = soup.find_all(
        'span', attrs={'class': 'chart-element__information__song'})
    artists = soup.find_all(
        'span', attrs={'class': 'chart-element__information__artist'})

    # download rankings
    # Default ranking
    delta_default = soup.find_all(
        'span', attrs={'class': 'chart-element__information__delta__text text--default'})
    # Last week ranking
    delta_last = soup.find_all(
        'span', attrs={'class': 'chart-element__information__delta__text text--last'})
    # Peak ranking
    delta_peak = soup.find_all(
        'span', attrs={'class': 'chart-element__information__delta__text text--peak'})
    # Num weeks on chart
    delta_week = soup.find_all(
        'span', attrs={'class': 'chart-element__information__delta__text text--week'})

    # convert to lists
    songs_list = [s.text for s in songs]
    artists_list = [a.text for a in artists]
    delta_default_list = [i.text for i in delta_default]
    delta_last_list = [i.text for i in delta_last]
    delta_peak_list = [i.text for i in delta_peak]
    delta_week_list = [i.text for i in delta_week]
    curr_week_list = [d] * len(songs_list)

    # combine all to combined list of tuples
    song_tuples = list(zip(songs_list, artists_list, delta_default_list,
                           delta_last_list, delta_peak_list, delta_week_list, curr_week_list))

    columns = ["Song", "Artist", "Rank_Default",
               "Rank_LastWeek", "Rank_Peak", "Num_Weeks_on_Chart", "Curr_Week"]

    # convert to Pandas df
    songs_df = pd.DataFrame(song_tuples, columns=columns)

    # data cleanup
    # extract only numbers from all 'rankings' columns & convert to numeric type
    songs_df['Rank_Default'] = songs_df['Rank_Default'].map(
        lambda x: x.lstrip('+'))
    songs_df['Rank_Default'] = songs_df['Rank_Default'].str.replace(
        '^-$', '', regex=True)
    songs_df['Rank_Default'] = songs_df['Rank_Default'].str.strip()
    songs_df['Rank_Default'] = pd.to_numeric(songs_df['Rank_Default'])

    songs_df['Rank_LastWeek'] = songs_df['Rank_LastWeek'].str.extract('(\d+)')
    songs_df['Rank_LastWeek'] = pd.to_numeric(songs_df['Rank_LastWeek'])

    songs_df['Rank_Peak'] = songs_df['Rank_Peak'].str.extract('(\d+)')
    songs_df['Rank_Peak'] = pd.to_numeric(songs_df['Rank_Peak'])

    songs_df['Num_Weeks_on_Chart'] = songs_df['Num_Weeks_on_Chart'].str.extract(
        '(\d+)')
    songs_df['Num_Weeks_on_Chart'] = pd.to_numeric(
        songs_df['Num_Weeks_on_Chart'])

    # replace NaNs with zeros
    songs_df.fillna(0, inplace=True)

    # export to CSV & save in data folder
    path = rf"data\{d}_billboard_100.csv"
    songs_df.to_csv(path, index=None)
    print(f"Saved week {d} to CSV")
