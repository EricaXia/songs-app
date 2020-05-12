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
import wordcloud
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import re
# Plotly packages
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
temp.drop(columns=['duration_ms_y', 'type_y',
                   'type_x', 'uri_y', 'uri_x'], inplace=True)
temp.rename(columns={'duration_ms_x': 'duration_ms'}, inplace=True)

num_artists = temp['artist_name'].nunique()


# Create App Layout
app.layout = html.Div([
    # dcc.Markdown("""## My First Dash"""),
    html.H1('My First Dash', style={'color': 'green', 'text-align': 'center'}),

    # Unique artist count -----
    html.Div(
        html.Div(
            [html.H6(id="artist_text"), html.P("No. of Artists:")],
            id="artists",
            className="mini_container",
        ),
        id="info-container",
        className="row container-display"),
    html.Div(
        html.H2(f"{num_artists}")
    ),
    # -----------------

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
])


@app.callback(
    dash.dependencies.Output('dd-output-container', 'children'),
    [dash.dependencies.Input('histogram-dropdown', 'value')])
def update_output(value):
    return dcc.Graph(
        id='histograms',
        figure={
            'data': [
                go.Histogram(x=temp[value], nbinsx=40)
            ],
            'layout': go.Layout(height=600, width=800, title_text=f"Distribution of {value.title()}")
        }
    )

#

#     html.Div(className='row', children=[
#         html.Div([
#             dcc.Markdown("""
#                 **Hover Data**
#                 Mouse over values in the graph.
#             """),
#             html.Pre(id='hover-data', style=styles['pre'])
#         ], className='three columns'),
#         html.Div([
#             dcc.Markdown("""
#                 **Click Data**
#                 Click on points in the graph.
#             """),
#             html.Pre(id='click-data', style=styles['pre']),
#         ], className='three columns'),
#         html.Div([
#             dcc.Markdown("""
#                 **Selection Data**
#                 Choose the lasso or rectangle tool in the graph's menu
#                 bar and then select points in the graph.
#                 Note that if `layout.clickmode = 'event+select'`, selection data also
#                 accumulates (or un-accumulates) selected data if you hold down the shift
#                 button while clicking.
#             """),
#             html.Pre(id='selected-data', style=styles['pre']),
#         ], className='three columns'),
#         html.Div([
#             dcc.Markdown("""
#                 **Zoom and Relayout Data**
#                 Click and drag on the graph to zoom or click on the zoom
#                 buttons in the graph's menu bar.
#                 Clicking on legend items will also fire
#                 this event.
#             """),
#             html.Pre(id='relayout-data', style=styles['pre']),
#         ], className='three columns')
#     ])
# ])

# @app.callback(
#     Output('hover-data', 'children'),
#     [Input('basic-interactions', 'hoverData')])
# def display_hover_data(hoverData):
#     return json.dumps(hoverData, indent=2)

# @app.callback(
#     Output('click-data', 'children'),
#     [Input('basic-interactions', 'clickData')])
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)

# @app.callback(
#     Output('selected-data', 'children'),
#     [Input('basic-interactions', 'selectedData')])
# def display_selected_data(selectedData):
#     return json.dumps(selectedData, indent=2)


# @app.callback(
#     Output('relayout-data', 'children'),
#     [Input('basic-interactions', 'relayoutData')])
# def display_relayout_data(relayoutData):
#     return json.dumps(relayoutData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
