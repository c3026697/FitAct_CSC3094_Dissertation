from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models import (
    ProgrammeWorkout,
    Workout,
    WorkoutExercise,
    Exercise,
    SavedWorkout,
)

workouts_bp = Blueprint("workouts", __name__)


def get_todays_workout():
    from app.models import User

    user = User.query.get(current_user.id)
    if not user or not user.current_programme_id:
        return None

    programme_workouts = (
        ProgrammeWorkout.query.filter_by(programme_id=user.current_programme_id)
        .order_by(ProgrammeWorkout.day_number)
        .all()
    )

    if not programme_workouts:
        return None

    # Always default to day 1 if session has no valid day
    current_day = session.get("current_day", 1)
    total_days = len(programme_workouts)

    if current_day < 1 or current_day > total_days:
        current_day = 1
        session["current_day"] = 1

    pw = next(
        (p for p in programme_workouts if p.day_number == current_day),
        programme_workouts[0],  # always fall back to first workout
    )
    return pw.workout


@workouts_bp.route("/workout")
@login_required
def workout_page():
    from app.models import User

    user = User.query.get(current_user.id)
    if not user.current_programme_id:
        return redirect(url_for("questionnaire.questionnaire"))

    workout = get_todays_workout()
    programme = user.current_programme
    exercises = []
    if workout:
        exercises = (
            WorkoutExercise.query.filter_by(workout_id=workout.id)
            .order_by(WorkoutExercise.exercise_order)
            .all()
        )
    return render_template(
        "workouts/workout_page.html",
        workout=workout,
        programme=programme,
        exercises=exercises,
    )


@workouts_bp.route("/workout/change")
@login_required
def change_workout():
    from app.models import User

    user = User.query.get(current_user.id)
    programme = user.current_programme
    programme_workouts = []
    if programme:
        programme_workouts = (
            ProgrammeWorkout.query.filter_by(programme_id=programme.id)
            .order_by(ProgrammeWorkout.day_number)
            .all()
        )
    return render_template(
        "workouts/change_workout.html",
        programme=programme,
        programme_workouts=programme_workouts,
    )


@workouts_bp.route("/workout/set/<int:workout_id>")
@login_required
def set_workout(workout_id):
    pw = ProgrammeWorkout.query.filter_by(
        programme_id=current_user.current_programme_id, workout_id=workout_id
    ).first()
    if pw:
        session["current_day"] = pw.day_number
    return redirect(url_for("workouts.workout_page"))


# ── Repository ───────────────────────────────────────────────────────────────


@workouts_bp.route("/workouts")
@login_required
def repository():
    from_change = request.args.get("from_change", "0") == "1"
    workouts = Workout.query.filter_by(is_custom=False).order_by(Workout.name).all()
    saved_ids = {
        sw.workout_id
        for sw in SavedWorkout.query.filter_by(user_id=current_user.id).all()
    }
    return render_template(
        "workouts/repository.html",
        workouts=workouts,
        saved_ids=saved_ids,
        from_change=from_change,
    )


@workouts_bp.route("/workouts/<int:workout_id>/info")
@login_required
def workout_info(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    exercises = (
        WorkoutExercise.query.filter_by(workout_id=workout.id)
        .order_by(WorkoutExercise.exercise_order)
        .all()
    )
    is_saved = (
        SavedWorkout.query.filter_by(
            user_id=current_user.id, workout_id=workout_id
        ).first()
        is not None
    )
    from_change = request.args.get("from_change", "0") == "1"
    return render_template(
        "workouts/workout_info.html",
        workout=workout,
        exercises=exercises,
        is_saved=is_saved,
        from_change=from_change,
    )


@workouts_bp.route("/workouts/<int:workout_id>/save", methods=["POST"])
@login_required
def save_workout(workout_id):
    existing = SavedWorkout.query.filter_by(
        user_id=current_user.id, workout_id=workout_id
    ).first()
    if not existing:
        db.session.add(SavedWorkout(user_id=current_user.id, workout_id=workout_id))
        db.session.commit()
        flash("Workout saved.", "success")
    else:
        flash("Already in your saved workouts.", "info")
    return redirect(request.referrer or url_for("workouts.repository"))


@workouts_bp.route("/workouts/<int:workout_id>/start")
@login_required
def start_from_repository(workout_id):
    return redirect(url_for("tracking.execute", workout_id=workout_id))


# ── Saved workouts ───────────────────────────────────────────────────────────


@workouts_bp.route("/workouts/saved")
@login_required
def saved():
    from_change = request.args.get("from_change", "0") == "1"
    saved_workouts = (
        SavedWorkout.query.filter_by(user_id=current_user.id)
        .order_by(SavedWorkout.saved_at.desc())
        .all()
    )
    return render_template(
        "workouts/saved.html", saved_workouts=saved_workouts, from_change=from_change
    )


@workouts_bp.route("/workouts/saved/<int:saved_id>/delete", methods=["POST"])
@login_required
def delete_saved(saved_id):
    sw = SavedWorkout.query.filter_by(
        id=saved_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(sw)
    db.session.commit()
    flash("Removed from saved workouts.", "info")
    return redirect(url_for("workouts.saved"))


# ── Create custom workout ────────────────────────────────────────────────────


@workouts_bp.route("/workouts/create", methods=["GET", "POST"])
@login_required
def create_custom():
    exercises = Exercise.query.order_by(Exercise.muscle_group, Exercise.name).all()

    if request.method == "POST":
        name = request.form.get("workout_name", "").strip()
        selected_ids = request.form.getlist("exercise_ids")

        if not name:
            flash("Please give your workout a name.", "danger")
            return render_template("workouts/create_custom.html", exercises=exercises)
        if not selected_ids:
            flash("Please select at least one exercise.", "danger")
            return render_template("workouts/create_custom.html", exercises=exercises)

        workout = Workout(
            name=name, type="Custom", is_custom=True, created_by_user_id=current_user.id
        )
        db.session.add(workout)
        db.session.flush()

        for order, ex_id in enumerate(selected_ids, start=1):
            db.session.add(
                WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=int(ex_id),
                    sets_target=3,
                    reps_target=10,
                    exercise_order=order,
                )
            )

        db.session.add(SavedWorkout(user_id=current_user.id, workout_id=workout.id))
        db.session.commit()
        flash(
            f'Custom workout "{name}" created successfully and can be accessed via Saved Workouts.',
            "success",
        )
        # Always return to change workout page after creating a custom workout
        return redirect(url_for("workouts.change_workout"))

    return render_template("workouts/create_custom.html", exercises=exercises)


@workouts_bp.route("/workouts/<int:workout_id>/edit-custom", methods=["GET", "POST"])
@login_required
def edit_custom(workout_id):
    workout = Workout.query.filter_by(
        id=workout_id, is_custom=True, created_by_user_id=current_user.id
    ).first_or_404()
    all_exercises = Exercise.query.order_by(Exercise.muscle_group, Exercise.name).all()
    current_ids = {we.exercise_id for we in workout.workout_exercises}

    if request.method == "POST":
        new_name = request.form.get("workout_name", "").strip()
        selected_ids = request.form.getlist("exercise_ids")

        if not new_name:
            flash("Workout needs a name.", "danger")
            return render_template(
                "workouts/edit_custom.html",
                workout=workout,
                exercises=all_exercises,
                current_ids=current_ids,
            )
        if not selected_ids:
            flash("Select at least one exercise.", "danger")
            return render_template(
                "workouts/edit_custom.html",
                workout=workout,
                exercises=all_exercises,
                current_ids=current_ids,
            )

        workout.name = new_name
        WorkoutExercise.query.filter_by(workout_id=workout.id).delete()
        for order, ex_id in enumerate(selected_ids, start=1):
            db.session.add(
                WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=int(ex_id),
                    sets_target=3,
                    reps_target=10,
                    exercise_order=order,
                )
            )
        db.session.commit()
        flash("Workout updated.", "success")
        return redirect(url_for("workouts.saved"))

    return render_template(
        "workouts/edit_custom.html",
        workout=workout,
        exercises=all_exercises,
        current_ids=current_ids,
    )
