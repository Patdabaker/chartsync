import pandas as pd
import re

# token = spotipy.util.prompt_for_user_token(
#     SPOTIFY_USERNAME,
#     scope=SPOTIFY_SCOPE,
#     client_id=SPOTIFY_CLIENT_ID,
#     client_secret=SPOTIFY_CLIENT_SECRET,
#     redirect_uri=SPOTIFY_REDIRECT_URI
# )

FEATURE_PATTERNS = [
    r"\s+feat\.?\s+",
    r"\s+ft\.?\s+",
    r"\s+featuring\s+"
]


def create_songlist(start, end, chart, amount, omit=None):
    print("Reading Chart...")
    df = pd.read_csv(chart)
    filtered = df[
        (df['Date'] >= start) &
        (df['Date'] <= end)
    ]
    i = 1
    sl = set()
    songs = []
    print("Reading Chart Completed!")
    print("Creating Songlist...0%")

    while len(sl) < amount and i <= amount:
        top = filtered[filtered["Rank"] == i].drop_duplicates()
        for _, row in top.iterrows():
            title = row['Song']
            artist = row['Artist']
            image = row['Image URL']
            length = len(sl)
            dup = (title, artist) in sl

            if not dup:
                if omit:
                    if (title, artist) not in omit:
                        sl.add((title, artist))
                        songs.append([length + 1, image, title, artist])                   
                else:
                    sl.add((title, artist))
                    songs.append([length + 1, image, title, artist])
            p = float(length / amount) * 100
            if p < 100:
                print(f"Creating Songlist...{p:.2f}%")
        i += 1
    p = 100
    print(f"Creating Songlist...{p}%")
    print("Songlist Completed!")
    return songs

def cut_playlist(urilist, amount):
    while len(urilist) > amount:
        urilist.pop()
    print("Cutting Process Completed!")

def extract_main_artist(artist_str):
    s = artist_str.strip()

    # Lowercase copy for searching
    lower_s = s.lower()

    for pattern in FEATURE_PATTERNS:
        match = re.search(pattern, lower_s)
        if match:
            # Slice original string to preserve capitalization
            cut_index = match.start()
            return s[:cut_index].strip()

    # No feature pattern — return unchanged
    return s

def generate_playlist(songs, sp):
    urilist = []
    length = len(songs)
    print("Obtaining Track Ids...0%")
    for i in range(length):
        query = f"track:{songs[i][1]} artist:{extract_main_artist(songs[i][2])}"
        result = sp.search(q=query, type="track", limit=1)
        track = result.get("tracks", {}).get("items", [])
        try:
            urilist.append(track[0]["uri"])
        except IndexError:
            (print("Could not obtain song, moving on to next"))
        p = float(len(urilist) / length) * 100
        if p < 100:
            print(f"Obtaining Track Ids...{p:.2f}%")
    p = 100
    print(f"Obtaining Track Ids...{p}%")
    print("Obtained All Track Ids!")
    return urilist

def get_dates(chart):
    df = pd.read_csv(chart)
    return (str(df['Date'].min()), str(df['Date'].max()))

def set_default_art(songs):
    for i in range(len(songs)):
        if songs[i][1] == '#':
            songs[i][1] = 'static/images/default_art.png'

# if __name__ == '__main__':
#     startyear = '2015'
#     startmonth = '08'
#     startday = '01'
#     endyear = '2016'
#     endmonth = '06'
#     endday = '01'
#     chart = "hot100.csv"
#     name = 'Junior Year'
#     numsongs = 100

#     start = f"{startyear}-{startmonth}-{startday}"
#     end = f"{endyear}-{endmonth}-{endday}"

#     songs = create_songlist(start, end, chart, numsongs)
#     sp = spotipy.Spotify(auth=token)
#     uri = generate_playlist(songs, sp)
#     playlist = sp.user_playlist_create(SPOTIFY_USERNAME, name)
#     print("Playlist Created! Adding Track Ids to Playlist")
#     if len(uri) > numsongs:
#         print("Playlist too large, cutting process starting")
#         cut_playlist(uri, numsongs)
#     print("Adding all items to Playlist")
#     sp.playlist_add_items(playlist["id"], uri)
#     print("Success! Check your spotify account!")