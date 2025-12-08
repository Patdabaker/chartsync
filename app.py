import os
import pandas as pd
import re
import spotipy
from dotenv import load_dotenv
from flask import Flask, redirect, request, url_for, session, render_template
from generate import create_songlist, cut_playlist, extract_main_artist, generate_playlist, get_dates
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Configure application
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope=os.getenv('SPOTIFY_SCOPE'),
        username=os.getenv('SPOTIFY_USERNAME')
    )

@app.route("/")
def index():
    chart_dict = {
        "Hot 100": {
            "name": "hot100.csv"
            },
        "Billboard 200": {
            "name": "billboard200.csv"
            },
        "Digital Songs": {
            "name": "digital_songs.csv"
            },
        "Radio": {
            "name": "radio.csv"
            },
        "Streaming Songs": {
            "name": "streaming_songs.csv"
            }
    }
    for key in chart_dict:
        chart = chart_dict[key]
        dates = get_dates(chart["name"])
        chart["min"], chart["max"] = dates[0], dates[1]

    return render_template("index.html", chart_dict=chart_dict)