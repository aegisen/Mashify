from flask import Blueprint, render_template, session, redirect
from src.user_info import oauth_manager

homepage_bp = Blueprint('homepage', __name__)

@homepage_bp.route("/")
def homepage():
    """
    Renders the homepage of the application.

    This route is responsible for rendering the homepage template and passing the
    Spotify authorization URL to the template for user authentication.

    Returns:
        Any: The rendered homepage template with the Spotify authorization URL.
    """
    return render_template(
        "index.html", spotify_auth_url=oauth_manager.get_authorize_url()
    )