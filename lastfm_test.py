import os

import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LASTFM_API_KEY")
URL = "http://ws.audioscrobbler.com/2.0/"

# Ask the user for an artist name
artist_name = ""
while not artist_name:
    artist_name = input("Enter an artist's name: ").strip()

# params for the API request
params = {
    "method": "artist.getSimilar",
    "artist": artist_name,
    "api_key": API_KEY,
    "format": "json",
    "limit": 5,
}
data = requests.get(URL, params=params).json()

# check for error in request from last.fm
if "error" in data:
    print(f"Error: {data['message']}")
else:
    similar = data["similarartists"]["artist"]
    if not similar:
        print(f"No similar artists found for {artist_name}.")
    else:
        for artist in similar:
            print(artist["name"])
