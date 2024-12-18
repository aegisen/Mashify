from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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