"""Programme blueprint for FitAct.

Handles viewing the user's currently allocated programme, manually
changing the programme, and previewing programmes and their workouts (FR2, FR3).
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Programme, ProgrammeWorkout, User

programme_bp = Blueprint("programme", __name__)


@programme_bp.route("/programme")
@login_required
def my_programme():
    # Query directly instead of using relationship to avoid lazy-loading issues
    user = User.query.get(current_user.id)
    programme = None
    programme_workouts = []

    if user.current_programme_id:
        programme = Programme.query.get(user.current_programme_id)

    if programme:
        programme_workouts = (
            ProgrammeWorkout.query.filter_by(programme_id=programme.id)
            .order_by(ProgrammeWorkout.day_number)
            .all()
        )

    all_programmes = Programme.query.order_by(Programme.id).all()

    return render_template(
        "programme/programme.html",
        programme=programme,
        programme_workouts=programme_workouts,
        all_programmes=all_programmes,
    )


@programme_bp.route("/programme/change", methods=["GET", "POST"])
@login_required
def change_programme():
    all_programmes = Programme.query.order_by(Programme.id).all()

    if request.method == "POST":
        programme_id = request.form.get("programme_id")
        selected = Programme.query.get(programme_id)
        if selected:
            user = User.query.get(current_user.id)
            user.current_programme_id = selected.id
            db.session.commit()
            flash(f"Programme changed to {selected.name}.", "success")
            return redirect(url_for("programme.my_programme"))

    return render_template(
        "programme/change_programme.html", all_programmes=all_programmes
    )


@programme_bp.route("/programme/preview/<int:programme_id>")
@login_required
def programme_preview(programme_id):
    programme = Programme.query.get_or_404(programme_id)
    return render_template("programme/programme_preview.html", programme=programme)


@programme_bp.route("/programme/preview/<int:programme_id>/workout/<int:workout_id>")
@login_required
def workout_preview(programme_id, workout_id):
    from app.models import Workout, WorkoutExercise

    workout = Workout.query.get_or_404(workout_id)
    exercises = (
        WorkoutExercise.query.filter_by(workout_id=workout.id)
        .order_by(WorkoutExercise.exercise_order)
        .all()
    )
    return render_template(
        "programme/workout_preview.html",
        workout=workout,
        exercises=exercises,
        programme_id=programme_id,
    )
