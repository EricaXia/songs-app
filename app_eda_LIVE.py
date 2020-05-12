# App packages
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import os
import sys
import pandas as pd
import numpy as np
import sqlite3
import time
import re
# Plotly packages
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Data Extraction: Run steps 1-4 scripts
exec(open('Step1_billboard_100_weekly_scrape.py').read())
exec(open('Step2_spotify_scrape_bb100.py').read())
exec(open('Step3_genius_scrape.py').read())
exec(open('Step4_sqlite.py').read())

print ("Starting app...")


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# FETCH DATA-----
# connect to music sqlite3 database
conn = sqlite3.connect('music.db')
tracks = pd.read_sql("SELECT * FROM track", conn)
af = pd.read_sql("SELECT * FROM audio_features", conn)
artists = pd.read_sql("SELECT * FROM artist", conn)
lyrics = pd.read_sql("SELECT * FROM lyrics", conn)
bb100 = pd.read_sql("SELECT * FROM bb100", conn)
temp = pd.merge(tracks, af, left_on='id', right_on='id', how='inner')
temp.drop(columns=['duration_ms_y', 'type_y', 'uri_y', 'uri_x'], inplace=True)
temp.rename(columns={'duration_ms_x': 'duration_ms'}, inplace=True)

# CALCULATE METRICS
dates = bb100['Curr_Week'].unique()
curr_dates = f'{min(dates)} to {max(dates)}'
num_artists = temp['artist_name'].nunique()
num_songs = temp['name'].nunique()
major = temp[temp['mode'] == 1]['type_x'].value_counts()
minor = temp[temp['mode'] == 0]['type_x'].value_counts()
# convert key integers to name for visualization purpoes
music_keys = {0: 'C',
              1: 'C#/Db',
              2: 'D',
              3: 'D#/Cb',
              4: 'E',
              5: 'F',
              6: 'F#/Gb',
              7: 'G',
              8: 'G#/Ab',
              9: 'A',
              10: 'A#/Bb',
              11: 'B'}


def convert_key(num):
    return music_keys[num]


temp['key_name'] = temp['key'].apply(convert_key)
# Create graph
temp2 = temp[['popularity', 'duration_ms', 'danceability', 'energy', 'loudness',
              'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']]
# af correlations
corr2 = temp2.corr()
fig_heatmap = px.imshow(
    corr2,
    labels=dict(color="Correlation"),
    title="Heatmap of Audio Features",
    x=temp2.columns,
    y=temp2.columns,
    color_continuous_scale='plasma'
)
fig_heatmap.update_layout(
    title="Heatmap of Audio Features",
    font=dict(family='Rockwell'))

# Popularity scatterplots -----
# Create scatterplots of popularity vs other features
fig_scatter = make_subplots(rows=2, cols=3, subplot_titles=('danceability',
                                                            'energy', 'loudness', 'speechiness', 'acousticness',
                                                            'instrumentalness', 'liveness', 'valence'))
fig_scatter.add_trace(
    go.Scatter(x=temp['danceability'], y=temp['popularity'], mode='markers'),
    row=1,
    col=1
)
fig_scatter.add_trace(
    go.Scatter(x=temp['energy'], y=temp['popularity'], mode='markers'),
    row=1,
    col=2
)
fig_scatter.add_trace(
    go.Scatter(x=temp['loudness'], y=temp['popularity'], mode='markers'),
    row=1,
    col=3
)
fig_scatter.add_trace(
    go.Scatter(x=temp['acousticness'], y=temp['popularity'], mode='markers'),
    row=2,
    col=1
)
fig_scatter.add_trace(
    go.Scatter(x=temp['instrumentalness'],
               y=temp['popularity'], mode='markers'),
    row=2,
    col=2
)
fig_scatter.add_trace(
    go.Scatter(x=temp['liveness'], y=temp['popularity'], mode='markers'),
    row=2,
    col=3
)
fig_scatter.update_layout(
    font=dict(family='Rockwell'),
    title="Popularity vs Audio Features",
    yaxis=dict(title='Popularity'),
    showlegend=False,
    height=500,
    width=600
)
# ----
# Create time series chart
to_graph = bb100.sort_values(
    by='Num_Weeks_on_Chart', ascending=False).iloc[0:45]
N = to_graph['Song'].nunique()
fig_ts = px.line(to_graph, x='Curr_Week', y='Rank_Default',
                 color='Song', line_shape='spline')
fig_ts.update_layout(
    font=dict(family='Rockwell'),
    title_text=f"Rankings for Current Top {N} Songs",
    yaxis=dict(title='Ranking'),
    xaxis=dict(title='Week'),
    height=480,
    width=600
)

p_style = {'color': 'black', 'font-weight': 'bold',
           'text-align': 'center', 'font-family': 'Rockwell'}

# Create App Layout -----------------
app.layout = html.Div(id='main-container', children=[
    html.H1('Billboard Top 100 Songs', style={
            'color': '#DA289F', 'font-weight': 'bold', 'text-align': 'center', 'font-family': 'Rockwell'}),
    html.H2('Visualized by Spotify Metrics', style={
        'color': '#1DB954', 'text-align': 'center', 'font-family': 'Rockwell'
    }),
    html.P(f'For Dates {curr_dates}', style=p_style),
    html.P(
        f'Unique Artist Count: {num_artists} | Unique Song Count: {num_songs}', style=p_style),

    # -----------------
    # ROW 1 ---
    html.Div(className='row', children=[
        html.Div(className='four columns', children=[
            dcc.Dropdown(
                id='histogram-dropdown',
                style={'height': '40px', 'width': '250px'},
                options=[
                    {'label': 'Danceability', 'value': 'danceability'},
                    {'label': 'Energy', 'value': 'energy'},
                    {'label': 'Loudness', 'value': 'loudness'},
                    {'label': 'Speechiness', 'value': 'speechiness'},
                    {'label': 'Acousticness', 'value': 'acousticness'},
                    {'label': 'Instrumentalness', 'value': 'instrumentalness'},
                    {'label': 'Liveness', 'value': 'liveness'},
                    {'label': 'Valence', 'value': 'valence'}
                ],
                value='danceability'),
            html.Div(id='dd-output-container')
        ], style={'marginLeft': '4%'}),


        html.Div(className='two columns', children=[
            # mode distribution
            dcc.Graph(
                id='modality',
                figure={
                    'data': [
                        go.Histogram(y=major, name="Major",
                                     marker_color='#ffdd00'),
                        go.Histogram(y=minor, name="Minor",
                                     marker_color='#0022cf')
                    ],
                    'layout': go.Layout(
                        barmode='stack',
                        height=300,
                        width=250,
                        title_text="Track Modality",
                        font_family="Rockwell",
                        legend={'traceorder': 'normal'}
                    )
                }
            )
        ], style={'marginTop': '4%'}),


        html.Div(className='two columns', children=[
            # mode distribution
            dcc.Graph(
                id='keys',
                figure={
                    'data': [
                        go.Bar(x=temp['key_name'].value_counts(
                        ).index, y=temp['key_name'].value_counts())
                    ],
                    'layout': go.Layout(
                        height=400,
                        width=600,
                        title_text="Key Distributions",
                        yaxis=dict(title='Count'),
                        xaxis=dict(title='Musical Key'),
                        font_family="Rockwell",
                        legend={'traceorder': 'normal'}
                    )
                }
            )
        ])




    ]),  # end of Row 1

    # begin Row 2
    html.Div(className='row', children=[
        html.Div(className='three columns', children=[
            dcc.Graph(
                id='heatmap',
                figure=fig_heatmap
            )
        ], style={'marginLeft': '4%'}),
        html.Div(className='four columns', children=[
            dcc.Graph(
                id='scatter',
                figure=fig_scatter
            )
        ]),
        html.Div(className='three columns', children=[
            dcc.Graph(
                id='ts',
                figure=fig_ts
            )
        ])

    ])  # end of Row 2

])  # End of App Layout


# Enable interactivity with callback function
@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('histogram-dropdown', 'value')])
def update_output(value):
    # updates the histogram
    return dcc.Graph(
        id='histograms',
        figure={
            'data': [
                go.Histogram(x=temp[value], nbinsx=40, marker_color='#BB86FC')
            ],
            'layout': go.Layout(
                height=400,
                width=600,
                title_text=f"Distribution of {value.title()}",
                font_family="Rockwell"
            )
        }
    )


if __name__ == '__main__':
    app.run_server(debug=True)
