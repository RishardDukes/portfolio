import os
import logging
from pathlib import Path
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .db import db
from .extensions import limiter
from .models import User
from .auth import auth_bp
from .routes import main_bp

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ── Core security ─────────────────────────────────────────────────────────
    secret = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SECRET_KEY"] = secret

    _is_production = os.getenv("FLASK_ENV", "development").lower() == "production"

    # Secure cookies in production; allow plain http in dev so local testing works
    app.config["SESSION_COOKIE_SECURE"] = _is_production
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_SECURE"] = _is_production
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_NAME"] = "hercules_session"

    # ── Database ──────────────────────────────────────────────────────────────
    db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    # Heroku-style postgres:// → postgresql:// fix
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ── Logging ───────────────────────────────────────────────────────────────
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    app.logger.setLevel(logging.INFO)

    # ── Rate limiting ─────────────────────────────────────────────────────────
    limiter.init_app(app)

    db.init_app(app)
    Migrate(app, db)
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
