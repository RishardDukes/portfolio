from datetime import datetime, date
from .db import db

class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Core fields
    date = db.Column(db.Date, nullable=False, default=date.today)
    exercise = db.Column(db.String(120), nullable=False)
    sets = db.Column(db.Integer, default=0)
    reps = db.Column(db.Integer, default=0)
    weight = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Optional: backref so you can do current_user.workouts
    user = db.relationship("User", backref=db.backref("workouts", lazy="dynamic"))
