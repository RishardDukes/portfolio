import os
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from .db import db

login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # IMPORT MODELS BEFORE create_all
    from .models import User, Workout

    # Blueprints
    from .auth import auth
    from .routes import main
    app.register_blueprint(auth)
    app.register_blueprint(main)

    # Create tables
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # (Optional) template helper if you use {{ now() }} in templates
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {"now": datetime.utcnow}

    return app

# Optional: allows `python -m src.workout_tracker` to run directly
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)

