from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from os import getenv

load_dotenv()

spotify = Spotify(
    auth_manager=SpotifyOAuth(
        scope = [
            'playlist-read-private',
            'playlist-modify-private',
        ],
    ),
    language=getenv("SPOTIPY_ACCEPT_LANGUAGE", None)
)
