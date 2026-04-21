from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models import (Workout, WorkoutExercise, WorkoutLog,
                        LoggedExercise, Achievement, UserAchievement)

tracking_bp = Blueprint('tracking', __name__)


def award_first_workout_badge(user):
    log_count = WorkoutLog.query.filter_by(user_id=user.id).count()
    if log_count == 1:
        achievement = Achievement.query.filter_by(milestone_type='first_workout').first()
        if achievement:
            already = UserAchievement.query.filter_by(
                user_id=user.id, achievement_id=achievement.id
            ).first()
            if not already:
                db.session.add(UserAchievement(
                    user_id=user.id, achievement_id=achievement.id
                ))
                db.session.commit()
                return achievement   # return badge so we can show popup
    return None


@tracking_bp.route('/workout/<int:workout_id>/execute')
@login_required
def execute(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    exercises = (
        WorkoutExercise.query
        .filter_by(workout_id=workout.id)
        .order_by(WorkoutExercise.exercise_order)
        .all()
    )
    return render_template('tracking/execute.html', workout=workout, exercises=exercises)


@tracking_bp.route('/workout/<int:workout_id>/log', methods=['POST'])
@login_required
def log_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    exercises = (
        WorkoutExercise.query
        .filter_by(workout_id=workout.id)
        .order_by(WorkoutExercise.exercise_order)
        .all()
    )

    duration = request.form.get('duration_seconds', None)
    log = WorkoutLog(
        user_id=current_user.id,
        workout_id=workout.id,
        completed_at=datetime.utcnow(),
        duration_seconds=int(duration) if duration else None
    )
    db.session.add(log)
    db.session.flush()

    for we in exercises:
        # Per-set tracking: collect set_1_reps, set_1_weight etc.
        set_num = 1
        while request.form.get(f'ex_{we.id}_set_{set_num}_reps'):
            reps = int(request.form.get(f'ex_{we.id}_set_{set_num}_reps', 0) or 0)
            weight = request.form.get(f'ex_{we.id}_set_{set_num}_weight', None)
            db.session.add(LoggedExercise(
                log_id=log.id,
                workout_exercise_id=we.id,
                exercise_id=we.exercise_id,
                sets_completed=set_num,
                reps_completed=reps,
                weight_kg=float(weight) if weight else None
            ))
            set_num += 1

        # Fallback: if no per-set data, log a single summary row
        if set_num == 1:
            sets_done = int(request.form.get(f'sets_{we.id}', we.sets_target) or we.sets_target)
            reps_done = int(request.form.get(f'reps_{we.id}', we.reps_target) or we.reps_target)
            db.session.add(LoggedExercise(
                log_id=log.id,
                workout_exercise_id=we.id,
                exercise_id=we.exercise_id,
                sets_completed=sets_done,
                reps_completed=reps_done,
                weight_kg=None
            ))

    db.session.commit()

    badge = award_first_workout_badge(current_user)
    if badge:
        session['new_badge_title'] = badge.title
        session['new_badge_description'] = badge.description

    flash('Workout logged!', 'success')
    return redirect(url_for('progress.progress'))