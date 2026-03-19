from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager

from .auth import auth_bp
from .db import db
from .models import User
from .routes import main_bp

PACKAGE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = PACKAGE_DIR.parent / "instance"
DEFAULT_DB_PATH = INSTANCE_DIR / "app.db"


def create_app() -> Flask:
    load_dotenv()
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DEFAULT_DB_PATH}",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to continue."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_globals():
        return {"now": datetime.utcnow}

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
