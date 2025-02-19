from flask import Blueprint, redirect, url_for, session, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from database import mongo
from database import get_db

auth_bp = Blueprint("auth", __name__)

# Google OAuth Blueprint
google_bp = make_google_blueprint(
    client_id="your_google_client_id",
    client_secret="your_google_client_secret",
    redirect_to="auth.google_login"
)

@auth_bp.route("/google", methods=["GET"])
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_info = resp.json()
        email = user_info["email"]

        # Check if user exists in DB
        db=get_db()
        user = db.users.find_one({"email": email})
        if not user:
            db.users.insert_one({"email": email, "oauth_provider": "google"})

        session["user"] = email
        return jsonify({"message": "Logged in successfully", "email": email})

    return jsonify({"error": "Google login failed"}), 401
