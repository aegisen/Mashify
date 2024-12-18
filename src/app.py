# run with
# flask --app app run --debug --port 3000

import os
import time

from flask import (
    Flask,
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)

from flask_sqlalchemy import SQLAlchemy #need to install
from sqlalchemy import Integer, String
from sqlalchemy import exc
from sqlalchemy.orm import Mapped, mapped_column

from spotipy import Spotify, CacheHandler
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import select
from src.models import db, User, Playlists, SongByPlaylist, Song, Artist, SongByArtist, Genre, ArtistByGenre
from src.services import CacheSessionHandler, get_token
from src.user_info import oauth_manager, get_token, get_playlist_info, get_song_info, get_artist_info  # Import the functions
from src.routes.homepage import homepage_bp
from src.routes.callback import callback_bp
from src.routes.spotify_info import spotify_info_bp
from src.routes.spotify_genre_info import spotify_genre_info_bp 
from src.routes.spotify_artist_info import spotify_artist_info_bp
from src.routes.create_playlist import create_playlist_bp



# setup flask app stuff
app = Flask(__name__,template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            instance_path=os.path.join(os.path.dirname(__file__), '..', 'instance'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
app.secret_key = "DEV"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


db.init_app(app)
app.app_context().push()

app.register_blueprint(homepage_bp)
app.register_blueprint(callback_bp)
app.register_blueprint(spotify_info_bp)
app.register_blueprint(spotify_genre_info_bp)
app.register_blueprint(spotify_artist_info_bp)
app.register_blueprint(create_playlist_bp)
