# src/workout_tracker/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager

from .db import db
from .models import User  # ensures model tables are registered before create_all

login_manager = LoginManager()
login_manager.login_view = "auth.login"  # redirect target for @login_required

@login_manager.user_loader
def load_user(user_id: str):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

def create_app():
    # Load .env (Codespaces/dev)
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # --- Config ---
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --- Init extensions ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- Blueprints ---
    from .auth import auth
    from .routes import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # --- DB setup for dev ---
    with app.app_context():
        db.create_all()

    return app

# Allow `python -m flask run` with FLASK_APP=src/workout_tracker
# Or `python -m src.workout_tracker` to run directly for quick dev.
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
