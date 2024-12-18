from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Represents a User in the database."""
    user_table_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)

    db.UniqueConstraint(user_id)


    def __init__(self, user_id):
        """Initializes the User object with the provided user ID."""
        self.user_id = user_id

    def __repr__(self):
        """Represents the User object as a string."""
        return f"User: ('{self.user_id}')"

class Playlists(db.Model):
    """Represents a Playlist associated with a User."""
    playlist_table_id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.String)
    playlist_name = db.Column(db.String)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    snapshot_id = db.Column(db.String)

    db.UniqueConstraint(playlist_id)


    def __init__(self, playlist_id, playlist_name, user_id, snapshot_id):
        """Initializes the Playlist object with the provided details."""
        self.playlist_id = playlist_id
        self.playlist_name = playlist_name
        self.user_id = user_id
        self.snapshot_id = snapshot_id

    def __repr__(self):
        """Represents the Playlist object as a string."""
        return f"Playlist: ('{self.playlist_id}', '{self.playlist_name}', '{self.snapshot_id}', '{self.user_id}')"

class SongByPlaylist(db.Model):
    """Represents the relationship between a Song and a Playlist."""
    song_table_id = db.Column(db.Integer(), primary_key=True)
    song_id = db.Column(db.String)
    playlist_id = db.Column(db.String, nullable=False) 

    db.UniqueConstraint(song_id, playlist_id)


    def __init__(self, song_id, playlist_id):
        """Initializes the SongByPlaylist object with the provided song and playlist IDs."""
        self.song_id = song_id
        self.playlist_id = playlist_id

    def __repr__(self):
        """Represents the SongByPlaylist object as a string."""
        return f"Song: ('{self.song_id}', '{self.playlist_id}')"

class Song(db.Model):
    """Represents a Song in the database."""
    song_table_id = db.Column(db.Integer(), primary_key=True)
    song_id = db.Column(db.String, nullable=False)
    song_name = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    month = db.Column(db.Integer(), nullable=False)
    day = db.Column(db.Integer(), nullable=False)

    db.UniqueConstraint(song_id)

    def __init__(self, song_id, song_name, year, month, day):
        """Initializes the Song object with the provided song details."""
        self.song_id = song_id
        self.song_name = song_name
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self):
        """Represents the Song object as a string."""
        return f"Song: ('{self.song_id}', '{self.song_name}')"

class Artist(db.Model):
    """Represents an Artist in the database."""
    artist_table_id = db.Column(db.Integer(), primary_key=True)
    artist_id = db.Column(db.String(50), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)

    db.UniqueConstraint(artist_id)

    def __init__(self, artist_id, artist_name):
        """Initializes the Artist object with the provided artist details."""
        self.artist_id = artist_id
        self.artist_name = artist_name

    def __repr__(self):
        """Represents the Artist object as a string."""
        return f"Song: ('{self.artist_id}', '{self.artist_name}')"


class SongByArtist(db.Model):
    """Represents the relationship between a Song and an Artist."""
    artist_song_table_id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.String,db.ForeignKey('song.song_id'),nullable=False)
    song_id = db.Column(db.String,db.ForeignKey('artist.artist_id'),nullable=False)
    
    db.UniqueConstraint(artist_id, song_id)

    def __init__(self, artist_id, song_id):
        """Initializes the SongByArtist object with the provided artist and song IDs."""
        self.artist_id = artist_id
        self.song_id = song_id

    def __repr__(self):
        """Represents the SongByArtist object as a string."""
        return f"SongByArtist: ('{self.artist_id}','{self.genre_id}')"
    

class Genre(db.Model):
    """Represents a Genre in the database."""
    genre_id = db.Column(db.Integer(), primary_key=True)
    genre_name = db.Column(db.String)

    db.UniqueConstraint(genre_name)

    def __init__(self,genre_name):
        """Initializes the Genre object with the provided genre name."""
        self.genre_name = genre_name

    def __repr__(self):
        """Represents the Genre object as a string."""
        return f"Genre: ('{self.genre_name}')"


class ArtistByGenre(db.Model):
    """Represents the relationship between an Artist and a Genre."""
    artist_genre_table_id = db.Column(db.Integer, primary_key = True)
    artist_id = db.Column(db.String,db.ForeignKey('artist.artist_id'),nullable=False)
    genre_id = db.Column(db.String,db.ForeignKey('genre.genre_id'),nullable=False)

    db.UniqueConstraint(artist_id, genre_id)

    def __init__(self, artist_id, genre_id):
        """Initializes the ArtistByGenre object with the provided artist and genre IDs."""
        self.artist_id = artist_id
        self.genre_id = genre_id

    def __repr__(self):
        """Represents the ArtistByGenre object as a string."""
        return f"ArtistByGenre: ('{self.artist_id}','{self.genre_id}')"