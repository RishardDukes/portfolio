from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    split = db.Column(db.String(20), default="Push", nullable=False)  # Push/Pull/Legs
    exercise = db.Column(db.String(120), nullable=False)
    sets = db.Column(db.Integer, default=0)
    reps = db.Column(db.Integer, default=0)
    weight = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("workouts", lazy="dynamic"))


class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("programs", lazy="dynamic"))
    days = db.relationship("ProgramDay", backref="program", cascade="all, delete-orphan",
                           order_by="ProgramDay.order")


class ProgramDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("program.id"), nullable=False, index=True)
    label = db.Column(db.String(80), nullable=False)
    order = db.Column(db.Integer, default=0)
    exercises = db.relationship("ProgramExercise", backref="day", cascade="all, delete-orphan",
                                order_by="ProgramExercise.order")


class ProgramExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey("program_day.id"), nullable=False, index=True)
    exercise_name = db.Column(db.String(120), nullable=False)
    target_sets = db.Column(db.Integer, default=3)
    target_reps = db.Column(db.Integer, default=10)
    order = db.Column(db.Integer, default=0)


class NutritionProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True, index=True)
    sex = db.Column(db.String(20), nullable=False, default="male")
    age = db.Column(db.Integer, default=25)
    height_inches = db.Column(db.Float, default=70.0)
    weight_lbs = db.Column(db.Float, default=180.0)
    activity_level = db.Column(db.String(40), nullable=False, default="moderate")
    activity_multiplier = db.Column(db.Float, default=1.55)
    goal_type = db.Column(db.String(20), nullable=False, default="maintain")
    daily_calorie_adjustment = db.Column(db.Integer, default=0)
    meals_per_day = db.Column(db.Integer, default=4)
    tdee = db.Column(db.Float, default=0.0)
    target_calories = db.Column(db.Integer, default=0)
    target_protein_g = db.Column(db.Float, default=0.0)
    target_carbs_g = db.Column(db.Float, default=0.0)
    target_fats_g = db.Column(db.Float, default=0.0)
    target_fiber_g = db.Column(db.Float, default=30.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("nutrition_profile", uselist=False))


class MealEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    meal_name = db.Column(db.String(40), nullable=False, default="Breakfast")
    food_name = db.Column(db.String(120), nullable=False)
    serving_size = db.Column(db.String(60))
    calories = db.Column(db.Float, default=0.0)
    protein_g = db.Column(db.Float, default=0.0)
    carbs_g = db.Column(db.Float, default=0.0)
    fats_g = db.Column(db.Float, default=0.0)
    fiber_g = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("meals", lazy="dynamic"))


class SavedMeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    default_meal_name = db.Column(db.String(40), nullable=False, default="Meal")
    food_name = db.Column(db.String(120), nullable=False)
    serving_size = db.Column(db.String(60))
    calories = db.Column(db.Float, default=0.0)
    protein_g = db.Column(db.Float, default=0.0)
    carbs_g = db.Column(db.Float, default=0.0)
    fats_g = db.Column(db.Float, default=0.0)
    fiber_g = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("saved_meals", lazy="dynamic"))


class BodyMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    weight_lbs = db.Column(db.Float, nullable=False)
    body_fat_pct = db.Column(db.Float)
    waist_inches = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref=db.backref("body_metrics", lazy="dynamic"))
