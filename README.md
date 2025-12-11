# 🎵 **ChartSync**

### **Billboard → Spotify Playlist Generator**

ChartSync is a full-stack web application that lets users transform any Billboard chart into a fully generated Spotify playlist — customized, editable, and built using real historical chart data.

The user selects a chart, date range, number of songs, and ChartSync automatically builds a playlist, lets the user edit it inline, and then adds it directly to their Spotify account using OAuth authentication.

---

## 🚀 **Features**

### 📊 Billboard Chart Integration

* Pulls tracks from multiple Billboard charts (`Hot 100`, `Billboard 200`, `Radio`, etc.)
* Dynamically restricts date ranges based on each chart’s actual data
* CSV parsing with Pandas to extract song data

### 📝 Playlist Builder

* Generates a playlist from chart rankings for a chosen date range
* Duplicate handling + “omit song” support
* Per-track album art, title, and artist info
* Tracks missing album art use a fallback default image

### 🗂️ Interactive Editing

* Delete songs by clicking checkbox
* Regenerate playlist without removed songs
* No page refresh — everything async via `fetch()` + JSON

### 🎧 Spotify Login & Playlist Upload

* OAuth login with Spotipy & Spotify API
* Tokens securely stored in session
* Automatic token refresh
* Create playlist on the user’s Spotify account
* Batch add tracks for large playlists
* Returns songs that failed to match Spotify’s catalog

### ⚡ Fully Asynchronous Frontend

* JS fetch calls → Flask backend → JSON responses
* Loading states, error handling, and dynamic UI updates
* Responsive “results window” that scrolls independently
* Reset, regenerate, and add-to-Spotify actions

### 🎨 Styled UI

* Modern Spotify-inspired design
* Centered header layout with right-aligned login/profile
* Responsive layout
* (CSS delivered separately)

---

## 🛠️ **Tech Stack**

### **Frontend**

* HTML5, CSS3
* Vanilla JavaScript (async + fetch API)
* Dynamic DOM updates and event-driven UI

### **Backend**

* Python 3
* Flask (routes, sessions, JSON API endpoints)
* Spotipy (Spotify API client)
* Pandas (CSV/chart parsing)

### **Infrastructure**

* Virtual environment (`venv`)
* Gunicorn (production server)
* Procfile for deployment
* Environment variables via `.env`

---

## 📚 **How It Works**

### 1. User Selects Chart + Date Range

JS updates date min/max dynamically based on chart metadata derived from CSV.

### 2. User Submits → Async Request

Payload sent as JSON:

```json
{
  "chart": "Hot 100",
  "start": "2024-01-01",
  "end": "2024-02-01",
  "name": "My Playlist",
  "amount": 50,
  "omit": [],
  "songs": []
}
```

### 3. Flask Generates Playlist

* Reads chart CSV
* Filters by date
* Picks top N songs
* Removes omitted songs
* Returns a structured JSON list of tracks

### 4. User Edits Playlist

* Checkboxes auto-select the entire row
* Deleted songs get pushed into the `omit` list

### 5. Add to Spotify

* OAuth login required
* Application creates playlist under the user’s Spotify account
* Adds track URIs in batches
* Returns any tracks not found by Spotify

---

## 🧪 **Local Development Setup**

### 1. Clone Repo

```bash
git clone https://github.com/Patdabaker/chartsync.git
cd chartsync
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Assign Environment Variables

Create `.env`:

```
FLASK_SECRET_KEY=your-secret
SPOTIFY_CLIENT_ID=your-client-id
SPOTIFY_CLIENT_SECRET=your-client-secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/callback
SPOTIFY_SCOPE='playlist-modify-private playlist-modify-public'
```

### 5. Run Flask

```bash
flask run
```

---

## 🌐 **Deployment**

ChartSync supports deployment via:

### ✔ Fly.io

### ✔ Render

### ✔ Railway

### ✔ Heroku-equivalent platforms (Gunicorn + Procfile)

Your `Procfile` typically contains:

```
web: gunicorn app:app
```

---

## 🧩 Project Structure

```
chartsync/
│
├── app.py               # Flask backend
├── generate.py          # Chart parsing + playlist logic
├── static/
│   ├── images/
│   │   └── default_art.png
│   ├── css/
│   │   └── styles.css
│   └── main.js
├── templates/
│   ├── base.html
│   └── index.html
├── requirements.txt
├── Procfile
└── README.md
```

---

## 🚧 **Future Enhancements**

These are optional upgrade ideas:

* OAuth auto-refresh UI
* Multi-chart mixed playlists
* Genre filtering
* “Include featured artists” toggle
* Shareable playlist preview page
* Light/Dark theme toggle
* More Spotify-like UI components
* Mobile responsive optimization
* Background task queue for long operations
* Cloud caching (Redis)

---

## 📄 **License**

MIT License — feel free to fork, remix, and build upon!

---

## 🙌 **Acknowledgements**

* Billboard for chart data
* Spotify API + Spotipy
* CS50x (project inspiration)
* Album art sources from dataset

---