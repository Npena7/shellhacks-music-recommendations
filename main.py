import os

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
API_KEY = os.getenv("LASTFM_API_KEY")
URL = "http://ws.audioscrobbler.com/2.0/"

# ask the user for an artist name
artist_name = ""
while not artist_name:
    artist_name = input("Enter an artist's name: ").strip()


# function to search for an artist using the Spotify API
def search_artist(name):
    spotify_results = sp.search(q=name, type="artist", limit=1)
    has_results = spotify_results["artists"]["items"]
    if not has_results:
        print("Artist not found.")
        return None
    else:
        artist = has_results[0]
        return artist


test_result = search_artist(artist_name)
print(test_result["name"])
