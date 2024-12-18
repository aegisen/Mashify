from flask import Blueprint, render_template, session, redirect
from src.user_info import oauth_manager

homepage_bp = Blueprint('homepage', __name__)

@homepage_bp.route("/")
def homepage():
    return render_template(
        "index.html", spotify_auth_url=oauth_manager.get_authorize_url()
    )