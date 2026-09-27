import os

import requests
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

from pprint import pprint

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
API_KEY = os.getenv("LASTFM_API_KEY")
URL = "http://ws.audioscrobbler.com/2.0/"


# function to search for an artist using the Spotify API
def search_artist(name):
    spotify_results = sp.search(q=name, type="artist", limit=1)
    results_list = spotify_results["artists"]["items"]
    if not results_list:
        return None
    return results_list[0]


# function to get similar artists from the Last.fm API, returns list of similar artists, and an error message if there is one
def get_similar_artists(name):
    params = {
        "method": "artist.getSimilar",
        "artist": name,
        "api_key": API_KEY,
        "format": "json",
        "limit": 5,
    }
    data = requests.get(URL, params=params).json()
    if "error" in data:
        return None, data["message"]
    return data["similarartists"]["artist"], None

# get artist info from last.fm api
def get_artist_info(name):
    params = {
        "method": "artist.getInfo",
        "artist": name,
        "api_key": API_KEY,
        "format": "json",
    }
    data = requests.get(URL, params=params).json()
    if "error" in data:
        return None, data["message"]
    return data["artist"], None


def main():
    # ask the user for an artist name
    artist_name = ""
    while not artist_name:
        artist_name = input("Enter an artist's name: ").strip()

    # Search for the artist using the Spotify API
    artist = search_artist(artist_name)
    if not artist:
        print(f"No artist found for {artist_name}.")
        return
    print(f"Showing results for {artist['name']}")

    # Find similar artists using the Last.fm API
    similar, error = get_similar_artists(artist["name"])
    if error:
        print(f"Error: {error}")
    elif not similar:
        print(f"No similar artists found for {artist['name']}.")
    else:
        print(f"Similar artists to {artist['name']}:")
        for sim_artist in similar:
            print(sim_artist["name"])
                



if __name__ == "__main__":
    main()
