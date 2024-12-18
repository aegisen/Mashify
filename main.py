from src.app import app
from src.models import db, User, Playlists, SongByPlaylist, Song, Artist, SongByArtist, Genre, ArtistByGenre


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, use_debugger=True)