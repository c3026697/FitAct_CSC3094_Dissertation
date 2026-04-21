from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import WorkoutLog, LoggedExercise

progress_bp = Blueprint('progress', __name__)


@progress_bp.route('/progress')
@login_required
def progress():
    logs = (
        WorkoutLog.query
        .filter_by(user_id=current_user.id)
        .order_by(WorkoutLog.completed_at.desc())
        .all()
    )
    return render_template('progress/progress.html', logs=logs)


@progress_bp.route('/progress/<int:log_id>')
@login_required
def log_detail(log_id):
    log = WorkoutLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    return render_template('progress/log_detail.html', log=log)


@progress_bp.route('/progress/<int:log_id>/delete', methods=['POST'])
@login_required
def delete_log(log_id):
    log = WorkoutLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    # Explicitly delete child records first to avoid FK constraint errors
    LoggedExercise.query.filter_by(log_id=log.id).delete()
    db.session.delete(log)
    db.session.commit()
    flash('Workout log deleted.', 'info')
    return redirect(url_for('progress.progress'))