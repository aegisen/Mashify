from flask import Blueprint, session, redirect, render_template
from spotipy import Spotify
from src.user_info import get_token, get_playlist_info, get_song_info
from src.models import db, User, Playlists, SongByPlaylist, Song, Artist, SongByArtist, Genre, ArtistByGenre
from src.user_info import oauth_manager, get_token, get_playlist_info, get_song_info, get_artist_info  # Import the functions
import sqlalchemy
from sqlalchemy import exc

spotify_info_bp = Blueprint('spotify_info', __name__)

@spotify_info_bp.route("/spotify-info")
def show_spotify_info():
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        return redirect("/")
    
    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')

    sp = Spotify(auth=session.get('token_info').get('access_token'))
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
    
    # Your existing logic for getting playlists, songs, and artists here
    # Make sure to define the relevant queries and logic as in your original code

    return render_template("spotify_info.html", ps=playlists, sg=playlist_dict)