from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db, bcrypt
from app.models import User
from flask import session as flask_session

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('workouts.workout_page'))
    return redirect(url_for('auth.login'))


@main_bp.route('/account')
@login_required
def account():
    return render_template('main/account.html')


@main_bp.route('/account/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_username = request.form.get('username', '').strip()
        new_email = request.form.get('email', '').strip().lower()

        error = None
        if not new_username or not new_email:
            error = 'Username and email are required.'
        elif new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                error = 'That username is already taken.'
        elif new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                error = 'That email is already in use.'

        if error:
            flash(error, 'danger')
        else:
            user = User.query.get(current_user.id)
            user.username = new_username
            user.email = new_email
            db.session.commit()
            flash('Profile updated.', 'success')
            return redirect(url_for('main.account'))

    return render_template('main/edit_profile.html')


@main_bp.route('/account/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        user = User.query.get(current_user.id)

        if not bcrypt.check_password_hash(user.password_hash, old_password):
            flash('Current password is incorrect.', 'danger')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
        else:
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('main.account'))

    return render_template('main/change_password.html')



@main_bp.route('/clear-badge-session', methods=['POST'])
@login_required
def clear_badge_session():
    flask_session.pop('new_badge_title', None)
    flask_session.pop('new_badge_description', None)
    return '', 204