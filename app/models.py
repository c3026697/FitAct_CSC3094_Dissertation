from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    current_programme_id = db.Column(
        db.Integer, db.ForeignKey("programme.id"), nullable=True
    )
    current_programme = db.relationship(
        "Programme", foreign_keys=[current_programme_id]
    )
    questionnaire_responses = db.relationship(
        "QuestionnaireResponse", backref="user", lazy=True
    )
    saved_workouts = db.relationship("SavedWorkout", backref="user", lazy=True)
    workout_logs = db.relationship("WorkoutLog", backref="user", lazy=True)
    achievements = db.relationship("UserAchievement", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Programme(db.Model):
    __tablename__ = "programme"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    split_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    programme_workouts = db.relationship(
        "ProgrammeWorkout",
        backref="programme",
        lazy=True,
        order_by="ProgrammeWorkout.day_number",
    )


class ProgrammeWorkout(db.Model):
    __tablename__ = "programme_workout"
    id = db.Column(db.Integer, primary_key=True)
    programme_id = db.Column(db.Integer, db.ForeignKey("programme.id"), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    workout_order = db.Column(db.Integer, nullable=False)
    workout = db.relationship("Workout", backref="programme_entries")


class Workout(db.Model):
    __tablename__ = "workout"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_custom = db.Column(db.Boolean, default=False, nullable=False)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    workout_exercises = db.relationship(
        "WorkoutExercise",
        backref="workout",
        lazy=True,
        order_by="WorkoutExercise.exercise_order",
    )


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercise"
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)
    sets_target = db.Column(db.Integer, nullable=False)
    reps_target = db.Column(db.Integer, nullable=False)
    exercise_order = db.Column(db.Integer, nullable=False)
    exercise = db.relationship("Exercise", backref="workout_entries")


class Exercise(db.Model):
    __tablename__ = "exercise"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    muscle_group = db.Column(db.String(50), nullable=False)
    guidance_text = db.Column(db.Text, nullable=True)


class QuestionnaireResponse(db.Model):
    __tablename__ = "questionnaire_response"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    training_days_per_week = db.Column(db.Integer, nullable=False)
    primary_goal = db.Column(db.String(100), nullable=False)
    experience_level = db.Column(db.String(50), nullable=False)
    equipment_access = db.Column(db.String(100), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class SavedWorkout(db.Model):
    __tablename__ = "saved_workout"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    workout = db.relationship("Workout", backref="saved_by")


class WorkoutLog(db.Model):
    __tablename__ = "workout_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey("workout.id"), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration_seconds = db.Column(db.Integer, nullable=True)  # NEW — workout timer
    notes = db.Column(db.Text, nullable=True)
    workout = db.relationship("Workout", backref="logs")
    logged_exercises = db.relationship(
        "LoggedExercise", backref="log", lazy=True, cascade="all, delete-orphan"
    )  # CASCADE DELETE FIX


class LoggedExercise(db.Model):
    __tablename__ = "logged_exercise"
    id = db.Column(db.Integer, primary_key=True)
    log_id = db.Column(db.Integer, db.ForeignKey("workout_log.id"), nullable=False)
    workout_exercise_id = db.Column(
        db.Integer, db.ForeignKey("workout_exercise.id"), nullable=False
    )
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)
    sets_completed = db.Column(db.Integer, nullable=False)
    reps_completed = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=True)  # NEW — weight tracking
    exercise = db.relationship("Exercise", backref="logged_entries")
    workout_exercise = db.relationship("WorkoutExercise", backref="logged_entries")


class Achievement(db.Model):
    __tablename__ = "achievement"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    milestone_type = db.Column(db.String(50), nullable=False)


class UserAchievement(db.Model):
    __tablename__ = "user_achievement"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    achievement_id = db.Column(
        db.Integer, db.ForeignKey("achievement.id"), nullable=False
    )
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)
    achievement = db.relationship("Achievement", backref="awarded_to")
