import time
from flask import session, current_app
from spotipy.oauth2 import SpotifyOAuth
from spotipy import CacheHandler

class CacheSessionHandler(CacheHandler):
    def __init__(self, session, token_key):
        self.token_key = token_key
        self.session = session

    def get_cached_token(self):
        return self.session.get(self.token_key)

    def save_token_to_cache(self, token_info):
        self.session[self.token_key] = token_info
        session.modified = True


def get_token(session):
    token_valid = True
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        oauth = SpotifyOAuth(
            client_id=current_app.config["SPOITFY_CLIENT_ID"],
            client_secret=current_app.config["SPOTIFY_CLIENT_SECRET"],
            redirect_uri=current_app.config["REDIRECT_URI"] + "/callback",
            scope=current_app.config["SCOPE"],
            cache_handler=CacheSessionHandler(session, "spotify_token"),
            show_dialog=current_app.config["SHOW_DIALOG"],
        )
        token_info = oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid
