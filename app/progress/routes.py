from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import WorkoutLog

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


@progress_bp.route('/progress/<int:log_id>/delete', methods=['POST'])
@login_required
def delete_log(log_id):
    log = WorkoutLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    db.session.delete(log)
    db.session.commit()
    flash('Log deleted.', 'info')
    return redirect(url_for('progress.progress'))