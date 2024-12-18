from flask import Blueprint, session, redirect, request
from src.user_info import oauth_manager

callback_bp = Blueprint('callback', __name__)

@callback_bp.route("/callback")
def callback():
    session.clear()
    code = request.args.get('code')
    token_info = oauth_manager.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/spotify-info")