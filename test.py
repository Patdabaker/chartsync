import pandas as pd

df = pd.read_csv("hot100.csv")

filtered = df[
    (df['Date'] >= '2016-08-01') &
     (df['Date'] <= '2017-06-01')
]

songs = filtered[['Song', 'Artist']].drop_duplicates()
i = 1

songlist = set()
sl = {}

while len(songlist) < 100:
    top = filtered[filtered["Rank"] == i].drop_duplicates()
    for _, row in top.iterrows():
        title = row['Song']
        artist = row['Artist']
        duplicate = (title, artist) in songlist

        if not duplicate:
            songlist.add((title, artist))
            sl[title] = artist
    i += 1
print(sl)