import os
import pandas as pd
import re
import spotipy
from dotenv import load_dotenv
from flask import Flask, redirect, request, url_for, session, render_template
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
    return render_template("index.html")