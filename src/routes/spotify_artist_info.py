from flask import Blueprint, session, redirect, render_template
from spotipy import Spotify
from src.user_info import get_token
from src.models import db, Playlists, SongByPlaylist, Song, Artist, SongByArtist
from src.user_info import oauth_manager

spotify_artist_info_bp = Blueprint('spotify_artist_info', __name__)

@spotify_artist_info_bp.route("/spotify-info/artist")
def show_spotify_info_by_artist():
# Check if the user has an active session with a valid token
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        return redirect("/")

    # Set session info with token
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    # Setup Spotify object for API calls
    sp = Spotify(auth=session.get('token_info').get('access_token'))
    
    user_id = sp.me()["id"]

    # Query all playlists for the current user
    playlists = Playlists.query.filter_by(user_id=user_id).all()
    playlist_ids = [playlist.playlist_id for playlist in playlists]

    # Join tables to get the songs and their corresponding artists
    songs_by_playlist = db.session.query(SongByPlaylist, Song, Artist).join(
        Song, Song.song_id == SongByPlaylist.song_id).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).filter(
        SongByPlaylist.playlist_id.in_(playlist_ids)).all()

    # Create a dictionary with artist names as keys and lists of song names and IDs as values
    artist_dict = {}
    for song_by_playlist, song, artist in songs_by_playlist:
        if artist.artist_name not in artist_dict:
            artist_dict[artist.artist_name] = []
        # Add the song's name and ID as a dictionary in the list
        if not any(existing_song['id'] == song.song_id for existing_song in artist_dict[artist.artist_name]):
            artist_dict[artist.artist_name].append({'name': song.song_name, 'id': song.song_id})

    # Debugging: check the structure of the artist_dict

    return render_template("spotify_artist_info.html", ar=list(artist_dict.keys()), ad=artist_dict)