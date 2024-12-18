from flask import Blueprint, session, redirect, render_template
from spotipy import Spotify
from src.user_info import get_token
from src.models import db, Playlists, SongByPlaylist, Song, Artist, SongByArtist, Genre, ArtistByGenre
from src.user_info import oauth_manager

spotify_genre_info_bp = Blueprint('spotify_genre_info', __name__)

@spotify_genre_info_bp.route("/spotify-info/genre")
def show_spotify_info_by_genre():
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        return redirect("/")

    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    sp = Spotify(auth=session.get('token_info').get('access_token'))
    user_id = sp.me()["id"]

    # Query all playlists from the current user
    playlists = Playlists.query.filter_by(user_id=user_id).all()
    playlist_ids = [playlist.playlist_id for playlist in playlists]

    # Join with SongByPlaylist and fetch relevant songs by playlist
    songs_by_playlist = db.session.query(SongByPlaylist, Song, Artist).join(
        Song, Song.song_id == SongByPlaylist.song_id).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).filter(
        SongByPlaylist.playlist_id.in_(playlist_ids)).all()

    songs_by_playlists_ids = [song_by_playlist.song_id for song_by_playlist, song, artist in songs_by_playlist]

    # Fetch genre info by joining with ArtistByGenre
    songs_by_genre = db.session.query(Song, Artist, Genre).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).join(
        ArtistByGenre, Artist.artist_id == ArtistByGenre.artist_id).join(
        Genre, Genre.genre_id == ArtistByGenre.genre_id).filter(
        Song.song_id.in_(songs_by_playlists_ids)).all()

    # Organize the data into a dictionary of genres and songs
    genre_dict = {}
    for song, artist, genre in songs_by_genre:
        if genre.genre_name not in genre_dict:
            genre_dict[genre.genre_name] = []
        genre_dict[genre.genre_name].append({'name': song.song_name, 'id': song.song_id})

    return render_template("spotify_genre_info.html", gn=list(genre_dict.keys()), sg=genre_dict)