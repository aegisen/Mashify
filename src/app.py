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



# setup flask app stuff
app = Flask(__name__,template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
            instance_path=os.path.join(os.path.dirname(__file__), '..', 'instance'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
app.secret_key = "DEV"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


db.init_app(app)
app.app_context().push()



# setup spotify stuff
SCOPE = "user-read-email user-read-private playlist-read-private playlist-read-collaborative user-library-read playlist-modify-public playlist-modify-private"
SPOITFY_CLIENT_ID = "d511528d911b44e9a81863869ee60809"
SPOTIFY_CLIENT_SECRET = "2b40cfddb1c74814a4092114c8ffc206"
REDIRECT_URI = "http://127.0.0.1:3000"
SHOW_DIALOG = True

# i might update URI later so you don't have to add /callback to end
oauth_manager = SpotifyOAuth(
    client_id=SPOITFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI+"/callback",
    scope=SCOPE,
    cache_handler=CacheSessionHandler(session, "spotify_token"),
    show_dialog=SHOW_DIALOG,
)


# app stuff
@app.route("/")
def homepage():
    jinja_env = {}

    return render_template(
        "index.html", spotify_auth_url=oauth_manager.get_authorize_url()
        # this is the login page
    )


@app.route("/callback")
def callback():
    session.clear()
    
    # setup auth again to be safe... also get token
    oauth = SpotifyOAuth(
        client_id=SPOITFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI+"/callback",
        scope=SCOPE,
        cache_handler=CacheSessionHandler(session, "spotify_token"),
        show_dialog=SHOW_DIALOG,
    )

    # get user session info
    code = request.args.get('code')
    token_info = oauth.get_access_token(code)

    # save user token info
    session["token_info"] = token_info

    # redirect to playlist info page
    return redirect("/spotify-info")





# HELPER FUNCTIONS TO GET SPOTIFY INFO

def get_playlist_info(playlist):
    # get playlist info
    playlist_id = playlist["id"]
    playlist_name = playlist["name"]
    playlist_snapshot_id = playlist["snapshot_id"]

    return playlist_id, playlist_name, playlist_snapshot_id


def get_song_info(sp, song):
    # for song, genre, songByGenre
    song_id = song["id"]
    song_name = song["name"]
    duration = song["duration_ms"]
    artists = [artist["name"] for artist in song["artists"]]
    release_date = song["album"]["release_date"]

    return song_id, song_name, duration, artists, release_date

def get_artist_info(sp, artist):
    # for artist, genre, artistByGenre
    # get artist info first, for each artist in track
    artist_id = artist["id"]
    artist_info = sp.artist(artist_id)

    artist_name = artist_info["name"]
    artist_genres = artist_info["genres"] # may have multiple genres too

    return artist_id, artist_name, artist_genres

# this is where we get spotify info
@app.route("/spotify-info")
def show_spotify_info():
    # if somehow didn't grab user token, redirect to login
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        return redirect("/")

    # set our session info
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    #data = request.form
    # setup spotify object so we can get our data
    sp = Spotify(auth=session.get('token_info').get('access_token'))
    songs = {}

    # get user_id
    user_info = sp.me()
    user_id = user_info["id"]

    new_user = User(user_id = user_id)
    try:
        db.session.add(new_user)
        db.session.commit()
        
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        #print(e)
        pass   
        

    # try to get user playlists
    #       get user's playlists, then add n stuff
    #       loop to get all playlists, and bypass 50 limit
    playlists = []
    limit_step = 50

    for offset in range(0, 1000, limit_step):
        res = sp.current_user_playlists(limit=limit_step, offset=offset)
        #print(res)
        if len(res["items"]) == 0:
            break
        playlists.extend(res["items"])

    # remove None items from playlists (Idk why they're none, smth changed w API?)
    playlists = list(filter(lambda item: item is not None, playlists))

    # check db if user exists; if yes, check if playlists are up to date
    exists = db.session.query(User.user_id).filter_by(user_id = user_id).first() is not None
    if exists:
        # get current db playlists
        db_playlists = Playlists.query.filter_by(user_id = user_id).all()
        db_playlist_ids = [playlist.playlist_id for playlist in db_playlists]

        # get ids of playlists from spotify that are not in db
        new_playlists = [playlist for playlist in playlists if playlist["id"] not in db_playlist_ids]
        

        # also get playlists with differing snapshot ids
        for playlist in db_playlists:
            for new_playlist in playlists:
                if playlist.playlist_id == new_playlist["id"]:
                    #print(playlist.playlist_name, ": ", playlist.snapshot_id, " vs ", new_playlist["snapshot_id"])
                    if playlist.snapshot_id != new_playlist["snapshot_id"]:
                        new_playlists.append(new_playlist)
        
        print(new_playlists)
    
    else: # if user doesn't exist, add all playlists
        new_playlists = playlists

                        
    # for each new playlist, get info and add to db
    for new_playlist in new_playlists:
        songs_in_playlist = [] # temp
        playlist_id, playlist_name, playlist_snapshot_id = get_playlist_info(new_playlist)
        new_playlist_entry = Playlists(playlist_id = playlist_id, playlist_name = playlist_name, user_id = user_id, snapshot_id = playlist_snapshot_id)
        
        # add to db

        # check if playlist already exists
        exists = db.session.query(Playlists.playlist_id).filter_by(playlist_id = playlist_id).first() is not None
        if exists:
            # update if snapshot id is different
            db_playlist = Playlists.query.filter_by(playlist_id = playlist_id).first()
            if db_playlist.snapshot_id != playlist_snapshot_id:
                db_playlist.snapshot_id = playlist_snapshot_id
                db.session.commit()
        else:
            try:
                db.session.add(new_playlist_entry)
                db.session.commit()
                
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                #print(e)
                pass

        # get songs from playlist
        results = sp.playlist_tracks(playlist_id)
        tracks = results["items"]

        while results["next"]:
            results = sp.next(results)
            tracks.extend(results["items"])
        

        if len(tracks) == 0:
            continue

        for i in range(0, len(tracks)):
            songs_in_playlist.append(tracks[i]["track"]["name"]) # temp for page render purposes
            track = tracks[i]["track"]

            # get song info
            song_id, song_name, duration, artists, release_date = get_song_info(sp, track)

            # add to song table in db
            new_song = Song(song_id = song_id, song_name = song_name, year = release_date[:4], month = release_date[5:7], day = release_date[8:10])
            try:
                db.session.add(new_song)
                db.session.commit()
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                ##print(e)
                pass

            # add to songByPlaylist table in db
            new_song_by_playlist = SongByPlaylist(song_id = song_id, playlist_id = playlist_id)
            try:
                db.session.add(new_song_by_playlist)
                db.session.commit()
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                ##print(e)
                pass

            # get artist info
            for artist in track["artists"]:
                artist_id, artist_name, artist_genres = get_artist_info(sp, artist)

                # add to artist table in db
                new_artist = Artist(artist_id = artist_id, artist_name = artist_name)
                try:
                    db.session.add(new_artist)
                    db.session.commit()
                except exc.SQLAlchemyError as e:
                    db.session.rollback()
                    ##print(e)
                    pass

                # add to songByArtist table in db
                new_song_by_artist = SongByArtist(song_id = song_id, artist_id = artist_id)
                try:
                    db.session.add(new_song_by_artist)
                    db.session.commit()
                except exc.SQLAlchemyError as e:
                    db.session.rollback()
                    ##print(e)
                    pass

                # add genre info
                for genre in artist_genres:
                    newGenre = Genre(genre_name = genre)
                    try:
                        db.session.add(newGenre)
                        db.session.commit()
                    except exc.SQLAlchemyError as e:
                        db.session.rollback()
                        ##print(e)
                        pass

                    # add to artistByGenre table in db
                    # get genre id from db
                    genre_id = Genre.query.filter_by(genre_name = genre).first().genre_id
                    # make artist_by_genre entry
                    new_artist_by_genre = ArtistByGenre(artist_id = artist_id, genre_id = genre_id)
                    try:
                        db.session.add(new_artist_by_genre)
                        db.session.commit()
                    except exc.SQLAlchemyError as e:
                        db.session.rollback()
                        #print(e)
                        pass
             

                

        songs[playlist_id] = songs_in_playlist
        
        

    # get info from db to display
    # create dictionary of playlists and songs

    # fetch playlists names, playlist ids from db
    playlists = Playlists.query.filter_by(user_id = user_id).all()
    songs_by_playlist = db.session.query(SongByPlaylist, Song).join(Song, Song.song_id == SongByPlaylist.song_id).all()

    playlist_dict = {}
    for playlist in playlists:
        playlist_dict[playlist.playlist_name] = [{"name":song.song_name,"id":song.song_id} for song_by_playlist, song in songs_by_playlist if song_by_playlist.playlist_id == playlist.playlist_id]

    return render_template("spotify_info.html", ps=playlists, sg = playlist_dict)

@app.route("/spotify-info/genre")
def show_spotify_info_by_genre():
    # if somehow didn't grab user token, redirect to login
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        return redirect("/")

    # set our session info
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    # setup spotify object so we can get our data
    sp = Spotify(auth=session.get('token_info').get('access_token'))
    
    user_id = sp.me()["id"]

   # Query all playlists from the current user
    playlists = Playlists.query.filter_by(user_id=user_id).all()
    playlist_ids = [playlist.playlist_id for playlist in playlists]

    # Join with SongByPlaylist where playlist ID matches
    songs_by_playlist = db.session.query(SongByPlaylist, Song, Artist).join(
        Song, Song.song_id == SongByPlaylist.song_id).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).filter(
        SongByPlaylist.playlist_id.in_(playlist_ids)).all()

    songs_by_playlists_ids = [song_by_playlist.song_id for song_by_playlist, song, artist in songs_by_playlist]

    # Get genre info by connecting with Artist and ArtistByGenre
    songs_by_genre = db.session.query(Song, Artist, Genre).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).join(
        ArtistByGenre, Artist.artist_id == ArtistByGenre.artist_id).join(
        Genre, Genre.genre_id == ArtistByGenre.genre_id).filter(
        Song.song_id.in_(songs_by_playlists_ids)).all()

    # Create a dictionary with genre names as keys and lists of song names as values
    genre_dict = {}
    for song, artist, genre in songs_by_genre:
        if genre.genre_name not in genre_dict:
            genre_dict[genre.genre_name] = []
        genre_dict[genre.genre_name].append({'name': song.song_name, 'id': song.song_id})


    return render_template("spotify_genre_info.html", gn=list(genre_dict.keys()), sg=genre_dict)


@app.route("/spotify-info/artist")
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

@app.route("/create-playlist/<playlist_name>", methods=["POST"])
def create_playlist(playlist_name):
 # Validate token
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        return redirect("/")

    # Get session token info
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    # Setup Spotify client with the user's token
    sp = Spotify(auth=session.get('token_info').get('access_token'))
    user_id = sp.current_user()["id"]

    # Get the track data from the request
    data = request.get_json()
    print("Request Data:", data)
    track_ids = data.get('selectedSongs', [])  # Extract track titles

    # Prevent adding duplicate titles
    track_ids = list(set(track_ids))  # Remove duplicates
    print(track_ids)

    print("Track IDs to add:", track_ids)
    
    # If no tracks are found, return an error
    if not track_ids:
        return jsonify({"error": "No valid tracks found"}), 400

    try:
        # Create the new playlist on Spotify
        new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
        new_playlist_id = new_playlist["id"]
        print("New Playlist ID:", new_playlist_id)  # Debug log

        # Format track IDs to Spotify URI format
        tracklist = [f"spotify:track:{track}" for track in track_ids]
        print("Tracklist to be added:", tracklist)  # Debug log

        # Add tracks to the newly created playlist
        response = sp.user_playlist_add_tracks(user=user_id, playlist_id=new_playlist_id, tracks=tracklist)
        print("Add Tracks Response:", response)  # Debug log

        # Return a success message
        return jsonify({"message": f"Playlist '{playlist_name}' created successfully!"}), 200
    except Exception as e:
        # Catch any error and return the error response
        print("Error during playlist creation:", str(e))
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
