from flask import Blueprint, session, redirect, request
from src.user_info import oauth_manager

callback_bp = Blueprint('callback', __name__)

@callback_bp.route("/callback")
def callback():
    """
    Handles the OAuth callback from Spotify.

    This route is triggered when Spotify redirects the user after they authenticate.
    It retrieves the authorization code from the request, uses it to get an access token,
    stores the token in the session, and then redirects the user to the Spotify info page.

    Returns:
        redirect: A redirect response to the Spotify info page.
    """
    session.clear()
    code = request.args.get('code')
    token_info = oauth_manager.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/spotify-info")