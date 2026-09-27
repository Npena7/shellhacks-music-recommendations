import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

artist_name = ""
# Get an artist name from the user
while not artist_name:
    artist_name = (input("Enter an artist name: ")).strip()


# Search for the artist using the Spotify API
results = sp.search(q=artist_name, type="artist", limit=1)
print(results)

# print(results["artists"]["items"][0]["name"])

# artist_id = results["artists"]["items"][0]["id"]
# print(sp.artist(artist_id))
