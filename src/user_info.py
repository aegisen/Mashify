# spotify_info.py

import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from flask import session
from src.services import CacheSessionHandler

# Spotify OAuth constants
SCOPE = "user-read-email user-read-private playlist-read-private playlist-read-collaborative user-library-read playlist-modify-public playlist-modify-private"
SPOITFY_CLIENT_ID = "d511528d911b44e9a81863869ee60809"
SPOTIFY_CLIENT_SECRET = "2b40cfddb1c74814a4092114c8ffc206"
REDIRECT_URI = "http://127.0.0.1:3000"
SHOW_DIALOG = True

# OAuth Manager setup
oauth_manager = SpotifyOAuth(
    client_id=SPOITFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI+"/callback",
    scope=SCOPE,
    cache_handler=CacheSessionHandler(session, "spotify_token"),
    show_dialog=SHOW_DIALOG,
)

# Helper functions to get Spotify information
def get_playlist_info(playlist):
    """
    Extract and return important information about a playlist.

    Args:
        playlist (dict): A dictionary containing playlist information from Spotify API.

    Returns:
        Tuple[str, str, str]: A tuple containing the playlist ID, name, and snapshot ID.
    """
    playlist_id = playlist["id"]
    playlist_name = playlist["name"]
    playlist_snapshot_id = playlist["snapshot_id"]
    return playlist_id, playlist_name, playlist_snapshot_id

def get_song_info(sp, song):
    """
    Extract and return important information about a song.

    Args:
        sp (Spotify): The Spotify client instance.
        song (dict): A dictionary containing song information from the Spotify API.

    Returns:
        Tuple[str, str, int, List[str], str]: A tuple containing the song ID, name, duration in ms, 
                                               list of artist names, and release date.
    """
    song_id = song["id"]
    song_name = song["name"]
    duration = song["duration_ms"]
    artists = [artist["name"] for artist in song["artists"]]
    release_date = song["album"]["release_date"]
    return song_id, song_name, duration, artists, release_date

def get_artist_info(sp, artist):
    """
    Extract and return important information about an artist.

    Args:
        sp (Spotify): The Spotify client instance.
        artist (dict): A dictionary containing artist information from the Spotify API.

    Returns:
        Tuple[str, str, List[str]]: A tuple containing the artist ID, name, and a list of genres.
    """
    artist_id = artist["id"]
    artist_info = sp.artist(artist_id)
    artist_name = artist_info["name"]
    artist_genres = artist_info["genres"]
    return artist_id, artist_name, artist_genres

# Function to get token info
def get_token(session):
    """
    Retrieve the token information from the session and validate it.

    Args:
        session (flask.Session): The Flask session object containing token information.

    Returns:
        Tuple[dict, bool]: A tuple containing the token information dictionary and a boolean indicating 
                            whether the token is valid or not.
    """
    token_info = session.get('token_info', {})
    authorized = False
    if token_info:
        oauth = SpotifyOAuth(
            client_id=SPOITFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI + "/callback",
            scope=SCOPE,
            cache_handler=CacheSessionHandler(session, "spotify_token"),
            show_dialog=SHOW_DIALOG,
        )
        authorized = oauth.validate_token(token_info)
    return token_info, authorized