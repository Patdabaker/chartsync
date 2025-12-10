import os
import spotipy
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request, url_for, session, render_template
from generate import create_songlist, cut_playlist, extract_main_artist, generate_playlist, get_dates, set_default_art
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Configure application
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
client_id=os.getenv('SPOTIFY_CLIENT_ID')
client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI')
scope=os.getenv('SPOTIFY_SCOPE'),
username=os.getenv('SPOTIFY_USERNAME')

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

@app.route("/")
def index():
    username = session.get('username')
    return render_template("index.html", chart_dict=chart_dict, username=username)

@app.route("/generate", methods=["POST"])
def generate():
    # Receive form info from JS
    data = request.get_json()
    try:
        csv = chart_dict[data['chart']]
    except KeyError:
        return jsonify({"success": False, "error": "Invalid Chart"}), 400
    chart  = csv['name']
    start  = data['start']
    end    = data['end']
    name   = data['name']
    amount = data['amount']
    omit   = data['omit']

    if not name:
        name = f"Top {amount} songs from Billboard's {data['chart']} chart from {start} to {end}"

    if chart is None:
        return jsonify({"success": False, "error": "Invalid Chart"}), 400

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Invalid Start Date"}), 400
    try:
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Invalid End Date"}), 400
    date_min = datetime.strptime(csv['min'], "%Y-%m-%d")
    date_max = datetime.strptime(csv['max'], "%Y-%m-%d")

    if start is None or start_date < date_min or start_date > date_max:
        return jsonify({"success": False, "error": "Invalid Start Date"}), 400
    if end is None or end_date < date_min or end_date > date_max:
        return jsonify({"success": False, "error": "Invalid End Date"}), 400
    if start_date > end_date:
        return jsonify({"success": False, "error": "Invalid Date Range"}), 400
    if amount is None or isinstance(amount, float) or amount <= 0:
        return jsonify({"success": False, "error": "Invalid Song Amount"}), 400

    print(omit)
    songs = create_songlist(start, end, chart, amount, omit)
    if len(songs) > amount:
        print("Playlist too large, cutting process starting")
        cut_playlist(songs, amount)
    set_default_art(songs)

    return jsonify({
        "success": True,
        "chart": chart,
        "startDate": start,
        "endDate": end,
        "playlistName": name,
        "songAmount": amount,
        "songs": songs
    })

@app.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    songs = data['songs']
    name = data['name']
    omit = data['omit']
    token_info = get_token()
    if not token_info:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    sp = spotipy.Spotify(auth=token_info["access_token"])

    gp = generate_playlist(songs, sp, omit)
    uri, failed = gp[0], gp[1]
    username = session['username']
    playlist = sp.user_playlist_create(username, name, public=False)
    sp.playlist_add_items(playlist['id'], uri)
    return jsonify({"success": True, "failed": failed})

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path=None
    )

def get_token():
    token_info = session.get("token_info", None)

    if not token_info:
        return None  # user not logged in

    now = int(time.time())

    # If expired, refresh it
    if token_info["expires_at"] - now < 60:  # expires in <60 sec
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info  # save updated token

    return token_info

@app.route("/login")
def login():
    sp_oauth = get_spotify_oauth()
    url = sp_oauth.get_authorize_url()
    return redirect(url)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/callback")
def callback():
    sp_oauth = get_spotify_oauth()

    code = request.args.get("code")

    token_info = sp_oauth.get_access_token(code, as_dict=True)

    session["token_info"] = token_info

    sp = spotipy.Spotify(auth=token_info["access_token"])
    profile = sp.current_user()

    session["username"] = profile["display_name"]
    session["user_id"] = profile["id"]
    session["profile_pic"] = profile["images"][0]["url"] if profile["images"] else None
    return redirect("/")
