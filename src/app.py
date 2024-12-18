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
)

from flask_sqlalchemy import SQLAlchemy #need to install
from sqlalchemy import Integer, String
from sqlalchemy import exc
from sqlalchemy.orm import Mapped, mapped_column

from spotipy import Spotify, CacheHandler
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import select

class CacheSessionHandler(CacheHandler):
    def __init__(self, session, token_key):
        self.token_key = token_key
        self.session = session

    def get_cached_token(self):
        return self.session.get(self.token_key)

    def save_token_to_cache(self, token_info):
        self.session[self.token_key] = token_info
        session.modified = True



# setup flask app stuff
app = Flask(__name__)
app.secret_key = "DEV"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'


# database stuff

    # to set up database, do:
    #   from app import app, db, User, Playlists, SongByPlaylist, Song, Artist, SongByArtist, Genre, ArtistByGenre
    #   db.create_all()
    # to clear database, do:
    # models.[TABLE TO CLEAR].query.delete()

db = SQLAlchemy(app)
app.app_context().push()

# models
class User(db.Model):
    user_table_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)

    db.UniqueConstraint(user_id)


    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return f"User: ('{self.user_id}')"

class Playlists(db.Model):
    playlist_table_id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.String)
    playlist_name = db.Column(db.String)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    snapshot_id = db.Column(db.String)

    db.UniqueConstraint(playlist_id)


    def __init__(self, playlist_id, playlist_name, user_id, snapshot_id):
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.user_id = user_id
        self.snapshot_id = snapshot_id

    def __repr__(self):
        return f"Playlist: ('{self.playlist_id}', '{self.playlist_name}', '{self.snapshot_id}', '{self.user_id}')"

class SongByPlaylist(db.Model):
    song_table_id = db.Column(db.Integer(), primary_key=True)
    song_id = db.Column(db.String)
    playlist_id = db.Column(db.String, nullable=False) 

    db.UniqueConstraint(song_id, playlist_id)


    def __init__(self, song_id, playlist_id):
        self.song_id = song_id
        self.playlist_id = playlist_id

    def __repr__(self):
        return f"Song: ('{self.song_id}', '{self.playlist_id}')"

class Song(db.Model):
    song_table_id = db.Column(db.Integer(), primary_key=True)
    song_id = db.Column(db.String, nullable=False)
    song_name = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    month = db.Column(db.Integer(), nullable=False)
    day = db.Column(db.Integer(), nullable=False)

    db.UniqueConstraint(song_id)

    def __init__(self, song_id, song_name, year, month, day):
        self.song_id = song_id
        self.song_name = song_name
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        return f"Song: ('{self.song_id}', '{self.song_name}')"

class Artist(db.Model):
    artist_table_id = db.Column(db.Integer(), primary_key=True)
    artist_id = db.Column(db.String(50), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)

    db.UniqueConstraint(artist_id)

    def __init__(self, artist_id, artist_name):
        self.artist_id = artist_id
        self.artist_name = artist_name

    def __repr__(self):
        return f"Song: ('{self.artist_id}', '{self.artist_name}')"


class SongByArtist(db.Model):
    artist_song_table_id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.String,db.ForeignKey('song.song_id'),nullable=False)
    song_id = db.Column(db.String,db.ForeignKey('artist.artist_id'),nullable=False)
    
    db.UniqueConstraint(artist_id, song_id)

    def __init__(self, artist_id, song_id):
        self.artist_id = artist_id
        self.song_id = song_id

    def __repr__(self):
        return f"SongByArtist: ('{self.artist_id}','{self.genre_id}')"
    

class Genre(db.Model):
    genre_id = db.Column(db.Integer(), primary_key=True)
    genre_name = db.Column(db.String)

    db.UniqueConstraint(genre_name)

    def __init__(self,genre_name):
        self.genre_name = genre_name

    def __repr__(self):
        return f"Genre: ('{self.genre_name}')"


class ArtistByGenre(db.Model):
    artist_genre_table_id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.String,db.ForeignKey('artist.artist_id'),nullable=False)
    genre_id = db.Column(db.String,db.ForeignKey('genre.genre_id'),nullable=False)

    db.UniqueConstraint(artist_id, genre_id)

    def __init__(self, artist_id, genre_id):
        self.artist_id = artist_id
        self.genre_id = genre_id

    def __repr__(self):
        return f"ArtistByGenre: ('{self.artist_id}','{self.genre_id}')"


# BELOW IS DEPRECATED; USE ARTISTBYGENRE INSTEAD
# class SongByGenre(db.Model):
#     song_genre_table_id = db.Column(db.Integer, primary_key = True)
#     song_id = db.Column(db.String,db.ForeignKey('song.song_id'),nullable=False)
#     genre_id = db.Column(db.String,db.ForeignKey('genre.genre_id'),nullable=False)

#     def __init__(self, id, song_id, genre_id):
#         self.song_id = song_id
#         self.genre_id = genre_id

#     def __repr__(self):
#         return f"SongByGenre: ('{self.song_id}','{self.genre_id}')"


# TODO: add Genre, SongByArtist, SongByGenre
# https://www.geeksforgeeks.org/connect-flask-to-a-database-with-flask-sqlalchemy/#setting-up-sqlalchemy
# https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/#installation


# setup spotify stuff
SCOPE = "user-read-email user-read-private playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative user-library-read"
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

    # i will look at this later but i think i alr handled this in the callback
    # if request.args.get("code") or oauth_manager.validate_token(
    #     oauth_manager.get_cached_token()
    # ):
    #     oauth_manager.get_access_token(request.args.get("code"))
    #     return redirect("/spotify-info")

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

# this is just a helper function to get the token/check if it's still valid
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
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        oauth = SpotifyOAuth(
            client_id=SPOITFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI+"/callback",
            scope=SCOPE,
            cache_handler=CacheSessionHandler(session, "spotify_token"),
            show_dialog=SHOW_DIALOG,
        )
        token_info = oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid
# end helper




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
    #for artist in track["artists"]: # one song may have multiple artists
    artist_id = artist["id"]
    artist_info = sp.artist(artist_id)

    artist_name = artist_info["name"]
    artist_genres = artist_info["genres"] # may have multiple genres too

    return artist_id, artist_name, artist_genres

# this is where we get spotify info
# this is also where the user lands after logging in; it will be where all the user's playlist data is fetched and stored in the db
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

    # setup spotify object so we can get our data
    sp = Spotify(auth=session.get('token_info').get('access_token'))
    songs = {}

    # get user_id
    user_info = sp.me()
    user_id = user_info["id"]

    # try to add user if we do not have them in db
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
        if len(res["items"]) == 0:
            break
        playlists.extend(res["items"])

    # remove None items from playlists (not sure why they're none, smth changed w API?)
    playlists = list(filter(lambda item: item is not None, playlists))

    # check db if user exists; if yes, check if playlists are up to date
    exists = db.session.query(User.user_id).filter_by(user_id = user_id).first() is not None
    if exists:
        # get current db playlists
        db_playlists = Playlists.query.filter_by(user_id = user_id).all()
        db_playlist_ids = [playlist.playlist_id for playlist in db_playlists]

        # get ids of playlists from spotify that are not in db
        new_playlists = [playlist for playlist in playlists if playlist["id"] not in db_playlist_ids]
        
        # also get playlists with differing snapshot ids (those playlists have been edited since last time)
        for playlist in db_playlists:
            for new_playlist in playlists:
                if playlist.playlist_id == new_playlist["id"]:
                    if playlist.snapshot_id != new_playlist["snapshot_id"]:
                        new_playlists.append(new_playlist)
        #print(new_playlists)
    
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
            # update if snapshot id is different (e.g. added a new song)
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
                        print(e)
                        pass
             
        songs[playlist_id] = songs_in_playlist
        
        

    # get info from db to display
    # create dictionary of playlists and songs

    # get all playlists from the current user
    playlists = Playlists.query.filter_by(user_id=user_id).all()
    playlist_ids = [playlist.playlist_id for playlist in playlists]

    # join with songByPlaylist where playlist ID matches
    songs_by_playlist = db.session.query(SongByPlaylist, Song).join(
        Song, Song.song_id == SongByPlaylist.song_id).filter(
        SongByPlaylist.playlist_id.in_(playlist_ids)).all()

    # make a dictionary with playlist names as keys and dictionaries of song_id:song_name as values
        # the song_id:song_name dictionary is so we can pass the id back to create playlists with (and not have to query db again)
    playlist_dict = {}
    for playlist in playlists:
        playlist_dict[playlist.playlist_name] = {song.song_id: song.song_name for song_by_playlist, song in songs_by_playlist if song_by_playlist.playlist_id == playlist.playlist_id}

   # print(playlist_dict)
    return render_template("spotify_info.html", ps=list(playlist_dict.keys()), sg=playlist_dict)


# this is where users go when they click the View By Genre button
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

   # get all playlists from the current user
    playlists = Playlists.query.filter_by(user_id=user_id).all()
    playlist_ids = [playlist.playlist_id for playlist in playlists]

    # join with SongByPlaylist where playlist ID matches
    songs_by_playlist = db.session.query(SongByPlaylist, Song, Artist).join(
        Song, Song.song_id == SongByPlaylist.song_id).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).filter(
        SongByPlaylist.playlist_id.in_(playlist_ids)).all()

    # also track song IDs to get genre info
    songs_by_playlists_ids = [song_by_playlist.song_id for song_by_playlist, song, artist in songs_by_playlist]

    # get genre info by connecting with artist and artistByGenre
    songs_by_genre = db.session.query(Song, Artist, Genre).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).join(
        ArtistByGenre, Artist.artist_id == ArtistByGenre.artist_id).join(
        Genre, Genre.genre_id == ArtistByGenre.genre_id).filter(
        Song.song_id.in_(songs_by_playlists_ids)).all()

    # make a dictionary with genre names as keys and dicts of song_id:song_name as values
    genre_dict = {}
    for song, artist, genre in songs_by_genre:
        if genre.genre_name not in genre_dict:
            genre_dict[genre.genre_name] = {}
        genre_dict[genre.genre_name][song.song_id] = song.song_name

    return render_template("spotify_genre_info.html", gn=list(genre_dict.keys()), sg=genre_dict)

# this is where users go when they click the View By Artist button
@app.route("/spotify-info/artist")
def show_spotify_info_by_artist():
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

    # get all playlists from the current user
    playlists = Playlists.query.filter_by(user_id=user_id).all()
    playlist_ids = [playlist.playlist_id for playlist in playlists]

    # join with songByPlaylist where playlist ID matches (getting song and artist info for user's songs)
    songs_by_playlist = db.session.query(SongByPlaylist, Song, Artist).join(
        Song, Song.song_id == SongByPlaylist.song_id).join(
        SongByArtist, Song.song_id == SongByArtist.song_id).join(
        Artist, Artist.artist_id == SongByArtist.artist_id).filter(
        SongByPlaylist.playlist_id.in_(playlist_ids)).all()

    # make a dictionary with artist names as keys and dict of song_id:song_name as values
    artist_dict = {}
    for song_by_playlist, song, artist in songs_by_playlist:
        if artist.artist_name not in artist_dict:
            artist_dict[artist.artist_name] = {}
        artist_dict[artist.artist_name][song.song_id] = song.song_name


    return render_template("spotify_artist_info.html", ar=list(artist_dict.keys()), sg=artist_dict)

# this is what handles the create playlist button
@app.route("/create-playlist/<playlist_name>", methods=["POST"])
def create_playlist(playlist_name):
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

    # get the track IDs from the request (from html page)
    data = request.get_json()
    track_ids = data.get('track_ids', [])
    #print(track_ids)

    # create a new playlist on Spotify
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name)

    # get playlist that we just made
    playlists = sp.user_playlists(user_id)
    new_playlist = list(playlists['items'])[0]
    new_playlist_id = new_playlist["id"] # get the id of the new playlist so we can edit it

    # setup track ids to pass through spotipy (spotify api formatting)
    tracklist = ["spotify:track:" + track for track in track_ids]

    # add tracks to the new playlist
    sp.user_playlist_add_tracks(user=user_id, playlist_id=new_playlist_id, tracks=tracklist)

    return "Playlist created", 200

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, use_debugger=True)