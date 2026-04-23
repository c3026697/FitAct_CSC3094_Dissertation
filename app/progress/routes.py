from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import WorkoutLog, LoggedExercise, Exercise

progress_bp = Blueprint("progress", __name__)


@progress_bp.route("/progress")
@login_required
def progress():
    logs = (
        WorkoutLog.query.filter_by(user_id=current_user.id)
        .order_by(WorkoutLog.completed_at.desc())
        .all()
    )
    return render_template("progress/progress.html", logs=logs)


@progress_bp.route("/progress/<int:log_id>/edit", methods=["GET", "POST"])
@login_required
def edit_log(log_id):
    log = WorkoutLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        # Delete existing logged exercises and replace with submitted values
        LoggedExercise.query.filter_by(log_id=log.id).delete()

        exercise_ids = request.form.getlist("exercise_id")
        for ex_id in exercise_ids:
            set_num = 1
            while request.form.get(f"ex_{ex_id}_set_{set_num}_reps") is not None:
                reps = request.form.get(f"ex_{ex_id}_set_{set_num}_reps", "")
                weight = request.form.get(f"ex_{ex_id}_set_{set_num}_weight", "")
                if reps.strip():
                    we_id = request.form.get(f"ex_{ex_id}_we_id", 0)
                    db.session.add(
                        LoggedExercise(
                            log_id=log.id,
                            workout_exercise_id=int(we_id),
                            exercise_id=int(ex_id),
                            sets_completed=set_num,
                            reps_completed=int(reps) if reps.strip() else 0,
                            weight_kg=float(weight) if weight.strip() else None,
                        )
                    )
                set_num += 1

        db.session.commit()
        flash("Workout log updated.", "success")
        return redirect(url_for("progress.progress"))

    # Group logged exercises by exercise for the edit form
    grouped = {}
    for le in log.logged_exercises:
        ex_id = le.exercise_id
        if ex_id not in grouped:
            grouped[ex_id] = {
                "exercise": le.exercise,
                "we_id": le.workout_exercise_id,
                "sets": [],
            }
        grouped[ex_id]["sets"].append(le)

    return render_template("progress/edit_log.html", log=log, grouped=grouped)


@progress_bp.route("/progress/<int:log_id>/delete", methods=["POST"])
@login_required
def delete_log(log_id):
    log = WorkoutLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    LoggedExercise.query.filter_by(log_id=log.id).delete()
    db.session.delete(log)
    db.session.commit()
    flash("Workout log deleted.", "info")
    return redirect(url_for("progress.progress"))
