from flask import Blueprint, request, jsonify, redirect, session
from spotipy import Spotify
from src.user_info import get_token, oauth_manager

create_playlist_bp = Blueprint('spotify_bp', __name__)

@create_playlist_bp.route("/create-playlist/<playlist_name>", methods=["POST"])
def create_playlist(playlist_name):
    """
    Creates a new playlist on Spotify and adds selected tracks to it.

    This route is responsible for handling requests to create a new playlist on Spotify.
    It validates the user's authentication token, retrieves track information from the 
    request, creates the playlist, and adds the selected tracks to it.

    Parameters:
        playlist_name (str): The name of the playlist to be created.

    Returns:
        Any: A JSON response indicating the success or failure of the playlist creation.
    """
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