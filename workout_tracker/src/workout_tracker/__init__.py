import os
from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from .db import db
from .models import User
from .auth import auth_bp
from .routes import main_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_music_tracks():
        sounds_dir = Path(app.static_folder) / "sounds"
        allowed_suffixes = {".mp3", ".wav", ".ogg", ".m4a"}
        tracks = []
        if sounds_dir.exists() and sounds_dir.is_dir():
            tracks = [
                item.name
                for item in sounds_dir.iterdir()
                if item.is_file() and item.suffix.lower() in allowed_suffixes
            ]
            tracks.sort(key=str.lower)
        return {"topbar_tracks": tracks}

    with app.app_context():
        db.create_all()
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app
