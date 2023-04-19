from bs4 import BeautifulSoup
import requests
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Scraping Billboard top 100
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
URL = f"https://www.billboard.com/charts/hot-100/{date}/"
response = requests.get(url=URL)
soup = BeautifulSoup(response.text, "html.parser")
song_names_spans = soup.find_all("h3", id="title-of-a-story", class_="c-title")
song_names = [song.getText() for song in song_names_spans]

song_list_not_formatted = []
for i in song_names_spans:
    line = i.getText().strip()
    if line == "Songwriter(s):" or line == "Producer(s):" or line == "Imprint/Promotion Label:" or line == "":
        pass
    else:
        song_list_not_formatted.append(line)

songs = song_list_not_formatted[3:-13]

# SPOTIFY AUTHENTICATION
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://www.example.com"
SPOTIFY_ENDPOINT = "https://api.spotify.com/"
oauth_object = SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
# print(oauth_object.get_access_token())
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_URI,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path=".cache"  # this file is created after authentication and must be in the root directory of project
    )
)
spotify_id = sp.current_user()["id"]

# SEARCH SPOTIFY FOR SONGS BY TITLE
song_urls_list = []
for song in songs:
    song_url = sp.search(q=song, type="track")
    try:
        url = song_url['tracks']['items'][0]['external_urls']['spotify']
        song_urls_list.append(url)
    except IndexError:
        print(f"{song} doesn't exist in Spotify.")

# CREATE A NEW PRIVATE PLAYLIST IN SPOTIFY
play_list = sp.user_playlist_create(user=spotify_id, name=f"{date} Billboard 100", public=False)

# ADD SONGS FOUND TO PLAYLIST
sp.playlist_add_items(playlist_id=play_list["id"], items=song_urls_list)
